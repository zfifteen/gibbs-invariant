"""Core demo engine for the Gibbs Regime Switcher."""

from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Sequence, Tuple

import numpy as np

from gibbs_invariant import GibbsConfig, detect_gibbs, risk
from gibbs_invariant.metrics import (
    add_gaussian_noise,
    compute_jump_indices,
    estimate_crossover_harmonic,
    fft_partial_sum,
    jittered_sampling_grid,
    resample_to_uniform,
    square_wave,
    uniform_grid,
    zone_mask_from_jumps,
)

REQUIRED_RESULT_FILES = (
    "pipeline_summary.json",
    "gates_report.json",
    "constrained_metrics.json",
    "candidate_rankings.csv",
)

SUPPORTED_SIGNAL_FAMILIES = {"step", "square", "bandlimited_edge", "noisy_discontinuity"}


@dataclass(frozen=True)
class ArtifactStatus:
    name: str
    path: str
    timestamp_utc: str
    ok: bool
    message: str


@dataclass(frozen=True)
class ArtifactSnapshot:
    results_dir: str
    pipeline_summary: Dict[str, Any]
    gates_report: Dict[str, Any]
    constrained_metrics: Dict[str, Any]
    candidate_rankings: List[Dict[str, Any]]
    statuses: List[ArtifactStatus]


@dataclass(frozen=True)
class FrameMetrics:
    overshoot_ratio: float
    energy_redistribution: float
    invariant_residual: float
    jump_score: float
    jump_active: bool
    radius_residual: float
    energy_residual: float
    threshold_used: float
    estimated_crossover_n1: int


@dataclass(frozen=True)
class CounterfactualMetrics:
    baseline_edge_mse: float
    routed_edge_mse: float
    baseline_smooth_mse: float
    routed_smooth_mse: float
    quality_gain: float
    smooth_penalty: float
    baseline_cost: float
    routed_cost: float
    speed_gain: float
    edge_fraction: float
    mixed_fraction: float
    smooth_fraction: float


def _file_timestamp_utc(path: Path) -> str:
    ts = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    return ts.replace(microsecond=0).isoformat()


def _load_json(path: Path) -> Dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except Exception as exc:  # pragma: no cover - mapped to ValueError for caller
        raise ValueError(f"Malformed JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"Expected top-level object in {path}")
    return data


def _validate_pipeline_summary(data: Mapping[str, Any]) -> None:
    for key in ("phase2", "phase3", "phase4"):
        if key not in data:
            raise ValueError(f"pipeline_summary.json missing required key '{key}'")

    phase2 = data["phase2"]
    phase3 = data["phase3"]
    phase4 = data["phase4"]
    if not isinstance(phase2, Mapping) or not isinstance(phase3, Mapping) or not isinstance(phase4, Mapping):
        raise ValueError("pipeline_summary.json has invalid phase section types")
    if "phase2b_gates" not in phase2:
        raise ValueError("pipeline_summary.json phase2 missing phase2b_gates")
    if "pass" not in phase3:
        raise ValueError("pipeline_summary.json phase3 missing pass")
    if "selection_unblocked" not in phase4:
        raise ValueError("pipeline_summary.json phase4 missing selection_unblocked")


def _validate_gates_report(data: Mapping[str, Any]) -> None:
    required = ("all_pass", "noise_robustness", "nonuniform_sampling", "baseline_comparison")
    missing = [key for key in required if key not in data]
    if missing:
        raise ValueError(f"gates_report.json missing keys: {', '.join(missing)}")


def _validate_constrained_report(data: Mapping[str, Any]) -> None:
    required = ("pass", "tasks", "task_pass_count")
    missing = [key for key in required if key not in data]
    if missing:
        raise ValueError(f"constrained_metrics.json missing keys: {', '.join(missing)}")


def _load_candidate_rankings(path: Path) -> List[Dict[str, Any]]:
    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
    except Exception as exc:  # pragma: no cover - mapped for caller
        raise ValueError(f"Malformed CSV in {path}: {exc}") from exc
    if not rows:
        raise ValueError("candidate_rankings.csv has no rows")

    required_common = {"rank", "name", "repo_url"}
    keys = set(rows[0].keys()) if rows[0].keys() else set()
    if not required_common.issubset(keys):
        raise ValueError("candidate_rankings.csv missing required columns")
    if "score" not in keys and "total" not in keys:
        raise ValueError("candidate_rankings.csv must contain either 'score' or 'total' column")

    rankings: List[Dict[str, Any]] = []
    for row in rows:
        rankings.append(
            {
                "rank": int(row["rank"]),
                "name": str(row["name"]),
                "repo_url": str(row["repo_url"]),
                "score": float(row["score"]) if "score" in row and row["score"] not in (None, "") else float(row["total"]),
            }
        )
    return rankings


def load_artifacts(results_dir: str = "results") -> ArtifactSnapshot:
    """Load and validate evidence artifacts required by the demo."""

    out_dir = Path(results_dir)
    statuses: List[ArtifactStatus] = []

    for name in REQUIRED_RESULT_FILES:
        path = out_dir / name
        if not path.exists():
            raise ValueError(f"Missing required artifact: {path}")
        statuses.append(
            ArtifactStatus(
                name=name,
                path=str(path),
                timestamp_utc=_file_timestamp_utc(path),
                ok=True,
                message="Loaded",
            )
        )

    pipeline_summary = _load_json(out_dir / "pipeline_summary.json")
    _validate_pipeline_summary(pipeline_summary)

    gates_report = _load_json(out_dir / "gates_report.json")
    _validate_gates_report(gates_report)

    constrained_metrics = _load_json(out_dir / "constrained_metrics.json")
    _validate_constrained_report(constrained_metrics)

    candidate_rankings = _load_candidate_rankings(out_dir / "candidate_rankings.csv")

    return ArtifactSnapshot(
        results_dir=str(out_dir),
        pipeline_summary=dict(pipeline_summary),
        gates_report=dict(gates_report),
        constrained_metrics=dict(constrained_metrics),
        candidate_rankings=candidate_rankings,
        statuses=statuses,
    )


def _normalise(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    vmax = float(np.max(values))
    vmin = float(np.min(values))
    if vmax - vmin < 1e-12:
        return np.zeros_like(values)
    return (values - vmin) / (vmax - vmin)


def _scenario_seed(scenario: Mapping[str, Any]) -> int:
    text = str(scenario.get("id", "scenario"))
    return int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:8], 16)


def generate_signal(scenario: Mapping[str, Any], t: float) -> np.ndarray:
    """Generate deterministic scenario signal at time t."""

    family = str(scenario.get("signal_family", "")).strip()
    if family not in SUPPORTED_SIGNAL_FAMILIES:
        raise ValueError(f"Unsupported signal_family '{family}'")

    num_samples = int(scenario.get("num_samples", 2048))
    if num_samples < 256:
        raise ValueError("num_samples must be >= 256")

    x = uniform_grid(num_samples)
    phase = float(0.45 * t)

    if family == "step":
        base = np.where(x + 0.35 * np.sin(phase) < 0.0, -1.0, 1.0)
    elif family == "square":
        base = square_wave(x + phase)
    elif family == "bandlimited_edge":
        shifted = x + 0.20 * np.sin(phase)
        base = np.tanh(8.0 * shifted) + 0.10 * np.sin(9.0 * shifted + 0.2 * t)
    elif family == "noisy_discontinuity":
        base = np.where(x + 0.25 * np.sin(phase) < 0.0, -1.0, 1.0)
        snr_db = float(scenario.get("snr_db", 15.0))
        seed = _scenario_seed(scenario) + int(round(13.0 * t))
        base = add_gaussian_noise(base, snr_db=snr_db, seed=seed)
    else:  # pragma: no cover
        raise ValueError(f"Unsupported signal_family '{family}'")

    snr_db_override = scenario.get("snr_db")
    if family != "noisy_discontinuity" and snr_db_override is not None:
        snr_db = float(snr_db_override)
        if np.isfinite(snr_db) and snr_db > 0:
            base = add_gaussian_noise(base, snr_db=snr_db, seed=_scenario_seed(scenario) + int(t * 10))

    jitter_fraction = float(scenario.get("jitter_fraction", 0.0))
    if jitter_fraction > 0.0:
        jittered = jittered_sampling_grid(
            num_samples=num_samples,
            jitter_fraction=min(jitter_fraction, 0.49),
            seed=_scenario_seed(scenario) + int(17.0 * t),
        )
        sampled = np.interp(jittered, x, base, period=2.0 * np.pi)
        _, base = resample_to_uniform(jittered, sampled, num_samples=num_samples)

    return np.asarray(base, dtype=float)


def _config_from_input(config: GibbsConfig | Mapping[str, Any] | None) -> GibbsConfig:
    if config is None:
        return GibbsConfig(n_values=(16, 32, 64, 96), noise_policy="robust")
    if isinstance(config, GibbsConfig):
        return config.validated()
    cfg = GibbsConfig(
        n_values=tuple(int(n) for n in config.get("n_values", (16, 32, 64, 96))),
        alpha=float(config.get("alpha", 1.0)),
        jump_threshold=float(config.get("jump_threshold", 0.20)),
        noise_policy=str(config.get("noise_policy", "robust")),
        sampling_mode=str(config.get("sampling_mode", "uniform")),
    )
    return cfg.validated()


def analyze_signal(signal: np.ndarray, config: GibbsConfig | Mapping[str, Any] | None = None) -> FrameMetrics:
    """Run Gibbs detector and return normalized frame metrics."""

    values = np.asarray(signal, dtype=float)
    cfg = _config_from_input(config)
    report = detect_gibbs(values, config=cfg)

    coeff = np.abs(np.fft.rfft(values))[1:]
    risk_report = risk(coefficients=coeff, config=cfg)
    n1 = estimate_crossover_harmonic(max_N=220)

    return FrameMetrics(
        overshoot_ratio=float(report.overshoot_ratio),
        energy_redistribution=float(report.energy_redistribution),
        invariant_residual=float(report.invariant_residual),
        jump_score=float(risk_report.jump_score),
        jump_active=bool(risk_report.jump_active),
        radius_residual=float(report.radius_residual),
        energy_residual=float(report.energy_residual),
        threshold_used=float(risk_report.threshold_used),
        estimated_crossover_n1=int(n1 if n1 is not None else -1),
    )


def _route_masks(signal: np.ndarray, quantile_mixed: float, quantile_edge: float) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    grad = np.abs(np.diff(signal, append=signal[0]))
    curv = np.abs(np.diff(grad, append=grad[0]))
    residual = np.abs(signal - fft_partial_sum(signal, n_harmonics=24))

    score = 0.50 * _normalise(grad) + 0.30 * _normalise(curv) + 0.20 * _normalise(residual)
    edge_threshold = float(np.quantile(score, quantile_edge))
    mixed_threshold = float(np.quantile(score, quantile_mixed))

    edge_mask = score >= edge_threshold
    mixed_mask = (score >= mixed_threshold) & ~edge_mask
    smooth_mask = ~(edge_mask | mixed_mask)
    return smooth_mask, mixed_mask, edge_mask


def run_counterfactual(signal: np.ndarray, policy: Mapping[str, Any] | None = None) -> CounterfactualMetrics:
    """Simulate baseline-vs-routed proxy codec policy."""

    values = np.asarray(signal, dtype=float)
    cfg: MutableMapping[str, Any] = dict(policy or {})

    n_low = int(cfg.get("n_low", 12))
    n_mid = int(cfg.get("n_mid", 32))
    n_high = int(cfg.get("n_high", 72))
    quantile_mixed = float(cfg.get("quantile_mixed", 0.65))
    quantile_edge = float(cfg.get("quantile_edge", 0.88))
    edge_blend = float(cfg.get("edge_blend", 0.75))
    alpha = float(cfg.get("alpha", 1.0))

    cost_model = dict(cfg.get("cost_model", {}))
    edge_weight = float(cost_model.get("edge_weight", 1.0))
    smooth_weight = float(cost_model.get("smooth_weight", 0.25))
    mixed_weight = float(cfg.get("mixed_weight", (edge_weight + smooth_weight) * 0.5))

    smooth_mask, mixed_mask, edge_mask = _route_masks(values, quantile_mixed, quantile_edge)

    baseline_recon = fft_partial_sum(values, n_harmonics=n_high)
    low_recon = fft_partial_sum(values, n_harmonics=n_low)
    mid_recon = fft_partial_sum(values, n_harmonics=n_mid)

    routed = low_recon.copy()
    routed[mixed_mask] = mid_recon[mixed_mask]
    routed[edge_mask] = baseline_recon[edge_mask] + edge_blend * (values[edge_mask] - baseline_recon[edge_mask])

    jump_indices = compute_jump_indices(values, top_k=2)
    edge_zone_mask = zone_mask_from_jumps(length=values.size, jump_indices=jump_indices, n_harmonics=max(n_mid, 2), alpha=alpha)
    smooth_zone_mask = ~edge_zone_mask

    baseline_err2 = (baseline_recon - values) ** 2
    routed_err2 = (routed - values) ** 2

    baseline_edge_mse = float(np.mean(baseline_err2[edge_zone_mask])) if np.any(edge_zone_mask) else 0.0
    routed_edge_mse = float(np.mean(routed_err2[edge_zone_mask])) if np.any(edge_zone_mask) else 0.0
    baseline_smooth_mse = float(np.mean(baseline_err2[smooth_zone_mask])) if np.any(smooth_zone_mask) else 0.0
    routed_smooth_mse = float(np.mean(routed_err2[smooth_zone_mask])) if np.any(smooth_zone_mask) else 0.0

    quality_gain = baseline_edge_mse - routed_edge_mse
    smooth_penalty = routed_smooth_mse - baseline_smooth_mse

    total = float(values.size)
    edge_count = float(np.sum(edge_mask))
    mixed_count = float(np.sum(mixed_mask))
    smooth_count = float(np.sum(smooth_mask))

    baseline_cost = max(1e-12, total * edge_weight)
    routed_cost = edge_weight * edge_count + mixed_weight * mixed_count + smooth_weight * smooth_count
    speed_gain = 1.0 - (routed_cost / baseline_cost)

    return CounterfactualMetrics(
        baseline_edge_mse=float(baseline_edge_mse),
        routed_edge_mse=float(routed_edge_mse),
        baseline_smooth_mse=float(baseline_smooth_mse),
        routed_smooth_mse=float(routed_smooth_mse),
        quality_gain=float(quality_gain),
        smooth_penalty=float(smooth_penalty),
        baseline_cost=float(baseline_cost),
        routed_cost=float(routed_cost),
        speed_gain=float(speed_gain),
        edge_fraction=float(edge_count / total),
        mixed_fraction=float(mixed_count / total),
        smooth_fraction=float(smooth_count / total),
    )


def compute_disruption_index(metrics: CounterfactualMetrics) -> float:
    """Collapse quality-speed tradeoffs into a bounded [0, 100] score."""

    edge_base = max(abs(metrics.baseline_edge_mse), 1e-4)
    smooth_base = max(abs(metrics.baseline_smooth_mse), 1e-3)

    quality_term = np.tanh(metrics.quality_gain / edge_base)
    smooth_term = np.tanh(max(0.0, metrics.smooth_penalty) / smooth_base)
    speed_term = metrics.speed_gain

    score = 50.0 + 28.0 * quality_term + 35.0 * speed_term - 15.0 * smooth_term
    return float(np.clip(score, 0.0, 100.0))


def _validate_script(script: Sequence[Mapping[str, Any]]) -> None:
    for idx, row in enumerate(script):
        if "t_sec" not in row or "action" not in row:
            raise ValueError(f"script row {idx} missing required keys")
        if str(row["action"]) != "set_scene":
            raise ValueError("script actions currently support only 'set_scene'")


def validate_scenario(payload: Mapping[str, Any]) -> Dict[str, Any]:
    required = {"id", "title", "signal_family", "snr_db", "jitter_fraction", "n_values", "alpha", "jump_threshold", "cost_model", "script"}
    missing = [key for key in required if key not in payload]
    if missing:
        raise ValueError(f"scenario missing required keys: {', '.join(missing)}")
    family = str(payload["signal_family"])
    if family not in SUPPORTED_SIGNAL_FAMILIES:
        raise ValueError(f"Unsupported scenario signal_family '{family}'")
    n_values = payload["n_values"]
    if not isinstance(n_values, Sequence) or not n_values:
        raise ValueError("scenario n_values must be a non-empty list")
    cost_model = payload["cost_model"]
    if not isinstance(cost_model, Mapping):
        raise ValueError("scenario cost_model must be an object")
    if "edge_weight" not in cost_model or "smooth_weight" not in cost_model:
        raise ValueError("scenario cost_model requires edge_weight and smooth_weight")
    script = payload["script"]
    if not isinstance(script, Sequence):
        raise ValueError("scenario script must be a list")
    _validate_script(script)
    return dict(payload)


def load_scenarios(scenarios_dir: str | Path) -> Dict[str, Dict[str, Any]]:
    root = Path(scenarios_dir)
    if not root.exists():
        raise ValueError(f"Scenario directory does not exist: {root}")

    scenarios: Dict[str, Dict[str, Any]] = {}
    for path in sorted(root.glob("*.json")):
        with path.open("r", encoding="utf-8") as handle:
            raw = json.load(handle)
        scenario = validate_scenario(raw)
        scenarios[str(scenario["id"])] = scenario

    if not scenarios:
        raise ValueError(f"No scenario JSON files found in {root}")
    return scenarios


def scenario_to_config(scenario: Mapping[str, Any]) -> GibbsConfig:
    return GibbsConfig(
        n_values=tuple(int(v) for v in scenario["n_values"]),
        alpha=float(scenario["alpha"]),
        jump_threshold=float(scenario["jump_threshold"]),
        noise_policy="robust",
        sampling_mode="jittered" if float(scenario.get("jitter_fraction", 0.0)) > 0 else "uniform",
    ).validated()


def simulate_policy_timeline(
    scenario: Mapping[str, Any],
    steps: int = 16,
    duration_s: float = 8.0,
) -> List[Dict[str, float]]:
    if steps < 2:
        raise ValueError("steps must be >= 2")

    cfg = scenario_to_config(scenario)
    policy = {
        "alpha": float(scenario["alpha"]),
        "cost_model": {
            "edge_weight": float(scenario["cost_model"]["edge_weight"]),
            "smooth_weight": float(scenario["cost_model"]["smooth_weight"]),
        },
    }

    timeline: List[Dict[str, float]] = []
    for idx in range(steps):
        t = float((duration_s * idx) / (steps - 1))
        signal = generate_signal(scenario, t=t)
        frame = analyze_signal(signal, config=cfg)
        counter = run_counterfactual(signal, policy=policy)
        disruption = compute_disruption_index(counter)
        timeline.append(
            {
                "t_sec": round(t, 6),
                "jump_score": round(frame.jump_score, 6),
                "energy_redistribution": round(frame.energy_redistribution, 6),
                "quality_gain": round(counter.quality_gain, 6),
                "speed_gain": round(counter.speed_gain, 6),
                "smooth_penalty": round(counter.smooth_penalty, 6),
                "disruption_index": round(disruption, 6),
            }
        )
    return timeline


def timeline_hash(timeline: Sequence[Mapping[str, float]]) -> str:
    payload = json.dumps(list(timeline), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def compute_policy_timeline_hash(
    scenario: Mapping[str, Any],
    steps: int = 16,
    duration_s: float = 8.0,
) -> str:
    return timeline_hash(simulate_policy_timeline(scenario=scenario, steps=steps, duration_s=duration_s))


def scene_order() -> Tuple[str, ...]:
    return (
        "Invariant Convergence",
        "N1 Crossover",
        "Noise/Jitter Stress",
        "Smooth Impostor Rejection",
        "Codec Routing Economics",
        "Deployment Bridge (mozjpeg)",
    )
