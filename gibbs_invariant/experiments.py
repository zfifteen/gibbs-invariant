"""Experiment runners, falsification gates, and artifact generation for v1."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Sequence, Tuple

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from .detection import detect_gibbs
from .fixtures import (
    all_fixtures,
    noisy_discontinuity_fixture,
    square_wave_fixture,
    step_function_fixture,
)
from .metrics import (
    GIBBS_OVERSHOOT_FRACTION_JUMP,
    GIBBS_RADIUS_DELTA,
    add_gaussian_noise,
    energy_concentration_fraction,
    fft_partial_sum,
    gibbs_overshoot,
    jittered_sampling_grid,
    resample_to_uniform,
    spectral_curvature,
    square_wave,
    square_wave_radii,
    uniform_grid,
)
from .types import GibbsConfig


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def run_invariant_convergence(
    output_dir: str = "results",
    n_values: Sequence[int] = (10, 25, 50, 100, 200, 400, 800),
) -> Path:
    out_dir = Path(output_dir)
    _ensure_dir(out_dir)
    csv_path = out_dir / "invariant_residuals.csv"

    x = uniform_grid(65536)
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "N",
                "overshoot_ratio",
                "theoretical_overshoot_ratio",
                "invariant_residual",
                "energy_redistribution",
            ],
        )
        writer.writeheader()
        for n in n_values:
            overshoot_fraction = (gibbs_overshoot(int(n)) - 1.0) / 2.0
            energy_ratio = energy_concentration_fraction(int(n), x)
            writer.writerow(
                {
                    "N": int(n),
                    "overshoot_ratio": float(overshoot_fraction),
                    "theoretical_overshoot_ratio": float(GIBBS_OVERSHOOT_FRACTION_JUMP),
                    "invariant_residual": float(overshoot_fraction - GIBBS_OVERSHOOT_FRACTION_JUMP),
                    "energy_redistribution": float(energy_ratio),
                }
            )

    return csv_path


def run_overshoot_prediction(
    output_dir: str = "results",
    n_values: Sequence[int] = (16, 32, 64, 128, 256, 512, 1024),
) -> Path:
    out_dir = Path(output_dir)
    _ensure_dir(out_dir)
    json_path = out_dir / "overshoot_profiles.json"

    profile: List[Dict[str, float]] = []
    for n in n_values:
        radii = square_wave_radii(int(n))
        delta = float(np.sum(radii[n: 2 * n]) if 2 * n <= radii.size else np.nan)
        profile.append(
            {
                "N": int(n),
                "measured_delta": float(delta) if np.isfinite(delta) else None,
                "target_delta": float(GIBBS_RADIUS_DELTA),
                "delta_residual": float(delta - GIBBS_RADIUS_DELTA) if np.isfinite(delta) else None,
            }
        )

    with json_path.open("w", encoding="utf-8") as handle:
        json.dump({"profiles": profile}, handle, indent=2)

    return json_path


def run_spectral_curvature_tests(
    output_dir: str = "results",
    n_values: Sequence[int] = (16, 32, 64, 128),
) -> Path:
    out_dir = Path(output_dir)
    _ensure_dir(out_dir)
    npy_path = out_dir / "energy_maps.npy"

    fixtures = all_fixtures(num_samples=2048)
    maps: Dict[str, np.ndarray] = {}
    for name, signal in fixtures.items():
        rows = []
        for n in n_values:
            rows.append(spectral_curvature(signal, int(n)))
        maps[name] = np.stack(rows, axis=0)

    np.save(npy_path, maps, allow_pickle=True)
    return npy_path


def plot_invariant_convergence(
    invariant_csv: str = "results/invariant_residuals.csv",
    output_path: str = "results/invariant_convergence.png",
) -> Path:
    csv_path = Path(invariant_csv)
    out_path = Path(output_path)
    _ensure_dir(out_path.parent)

    n_values: List[int] = []
    overshoot: List[float] = []
    residual: List[float] = []

    with csv_path.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            n_values.append(int(row["N"]))
            overshoot.append(float(row["overshoot_ratio"]))
            residual.append(float(row["invariant_residual"]))

    plt.figure(figsize=(10, 5.2))
    plt.subplot(1, 2, 1)
    plt.plot(n_values, overshoot, "o-", label="Measured")
    plt.axhline(GIBBS_OVERSHOOT_FRACTION_JUMP, linestyle="--", color="black", label="Theoretical")
    plt.xscale("log")
    plt.title("Overshoot Fraction")
    plt.xlabel("N")
    plt.ylabel("overshoot / jump")
    plt.grid(alpha=0.3)
    plt.legend()

    plt.subplot(1, 2, 2)
    plt.plot(n_values, residual, "o-", color="#cc5500")
    plt.axhline(0.0, linestyle="--", color="black")
    plt.xscale("log")
    plt.title("Invariant Residual")
    plt.xlabel("N")
    plt.ylabel("measured - theoretical")
    plt.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(out_path, dpi=220, bbox_inches="tight")
    plt.close()
    return out_path


def _precision_recall_f1(labels: np.ndarray, scores: np.ndarray, threshold: float) -> Dict[str, float]:
    pred = scores >= threshold
    tp = float(np.sum((pred == 1) & (labels == 1)))
    fp = float(np.sum((pred == 1) & (labels == 0)))
    fn = float(np.sum((pred == 0) & (labels == 1)))

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    if precision + recall == 0:
        f1 = 0.0
    else:
        f1 = 2.0 * precision * recall / (precision + recall)
    return {"precision": precision, "recall": recall, "f1": f1}


def _auc_roc(labels: np.ndarray, scores: np.ndarray) -> float:
    pos = float(np.sum(labels == 1))
    neg = float(np.sum(labels == 0))
    if pos == 0 or neg == 0:
        return 0.5

    order = np.argsort(-scores)
    labels_sorted = labels[order]
    tp = np.cumsum(labels_sorted == 1) / pos
    fp = np.cumsum(labels_sorted == 0) / neg

    tpr = np.concatenate([[0.0], tp, [1.0]])
    fpr = np.concatenate([[0.0], fp, [1.0]])
    return float(np.trapezoid(tpr, fpr))


def _auc_pr(labels: np.ndarray, scores: np.ndarray) -> float:
    pos = float(np.sum(labels == 1))
    if pos == 0:
        return 0.0

    order = np.argsort(-scores)
    labels_sorted = labels[order]
    tp = np.cumsum(labels_sorted == 1)
    fp = np.cumsum(labels_sorted == 0)

    recall = tp / pos
    precision = tp / np.maximum(tp + fp, 1.0)

    recall = np.concatenate([[0.0], recall, [1.0]])
    precision = np.concatenate([[precision[0] if precision.size else 1.0], precision, [0.0]])
    return float(np.trapezoid(precision, recall))


def _calibrate_threshold(scores: np.ndarray, labels: np.ndarray) -> float:
    candidates = np.unique(np.quantile(scores, np.linspace(0.05, 0.95, 121)))
    best_threshold = float(candidates[0])
    best_f1 = -1.0
    for threshold in candidates:
        f1 = _precision_recall_f1(labels, scores, float(threshold))["f1"]
        if f1 > best_f1:
            best_f1 = f1
            best_threshold = float(threshold)
    return best_threshold


def _tv_score(signal: np.ndarray) -> float:
    grad = np.abs(np.diff(signal, append=signal[0]))
    return float(np.max(grad) / (np.mean(grad) + 1e-9))


def _wavelet_score(signal: np.ndarray) -> float:
    trimmed = signal[: signal.size - (signal.size % 2)]
    even = trimmed[0::2]
    odd = trimmed[1::2]
    approx = 0.5 * (even + odd)
    detail = 0.5 * (even - odd)
    return float(np.mean(np.abs(detail)) / (np.mean(np.abs(approx)) + 1e-9))


def _build_baseline_dataset(
    sample_count: int = 200,
    num_samples: int = 1024,
    seed: int = 42,
) -> List[Dict[str, object]]:
    rng = np.random.default_rng(seed)
    x = uniform_grid(num_samples)

    dataset: List[Dict[str, object]] = []
    half = sample_count // 2

    for i in range(half):
        shift = rng.uniform(-np.pi, np.pi)
        amplitude = rng.uniform(0.8, 1.2)
        clean = square_wave(x + shift, amplitude=amplitude)
        snr = rng.choice([30.0, 20.0, 15.0, 10.0])
        signal = add_gaussian_noise(clean, snr_db=float(snr), seed=seed + i)
        dataset.append({"id": f"jump_{i}", "label": 1, "signal": signal})

    for i in range(half):
        freq1 = rng.integers(1, 5)
        freq2 = rng.integers(5, 12)
        smooth = np.sin(freq1 * x + rng.uniform(0, 2 * np.pi)) + 0.3 * np.sin(freq2 * x)
        smooth /= np.max(np.abs(smooth))
        snr = rng.choice([30.0, 20.0, 15.0])
        signal = add_gaussian_noise(smooth, snr_db=float(snr), seed=seed + half + i)
        dataset.append({"id": f"smooth_{i}", "label": 0, "signal": signal})

    rng.shuffle(dataset)
    return dataset


def _evaluate_detector(
    dataset: Sequence[Dict[str, object]],
    scorer: Callable[[np.ndarray], float],
) -> Tuple[np.ndarray, np.ndarray, List[str]]:
    labels: List[int] = []
    scores: List[float] = []
    ids: List[str] = []
    for row in dataset:
        labels.append(int(row["label"]))
        scores.append(float(scorer(np.asarray(row["signal"], dtype=float))))
        ids.append(str(row["id"]))
    return np.asarray(labels, dtype=int), np.asarray(scores, dtype=float), ids


def run_baseline_comparison_gate(
    output_dir: str = "results",
    seed: int = 42,
    sample_count: int = 200,
    num_samples: int = 1024,
) -> Dict[str, object]:
    dataset = _build_baseline_dataset(sample_count=sample_count, num_samples=num_samples, seed=seed)
    split = len(dataset) // 2
    dev = dataset[:split]
    test = dataset[split:]

    def gibbs_score(signal: np.ndarray) -> float:
        cfg = GibbsConfig(noise_policy="robust", n_values=(16, 32, 64, 96), jump_threshold=0.20)
        return detect_gibbs(signal, config=cfg).jump_score

    scorers = {
        "gibbs": gibbs_score,
        "tv": _tv_score,
        "wavelet": _wavelet_score,
    }

    metrics: Dict[str, Dict[str, float]] = {}
    thresholds: Dict[str, float] = {}
    non_win_cases: List[str] = []

    labels_dev_cache: Dict[str, np.ndarray] = {}
    scores_dev_cache: Dict[str, np.ndarray] = {}
    labels_test_cache: Dict[str, np.ndarray] = {}
    scores_test_cache: Dict[str, np.ndarray] = {}
    ids_test_cache: Dict[str, List[str]] = {}

    for name, scorer in scorers.items():
        labels_dev, scores_dev, _ = _evaluate_detector(dev, scorer)
        labels_test, scores_test, ids_test = _evaluate_detector(test, scorer)
        labels_dev_cache[name] = labels_dev
        scores_dev_cache[name] = scores_dev
        labels_test_cache[name] = labels_test
        scores_test_cache[name] = scores_test
        ids_test_cache[name] = ids_test

        threshold = _calibrate_threshold(scores_dev, labels_dev)
        thresholds[name] = threshold

        prf = _precision_recall_f1(labels_test, scores_test, threshold)
        metrics[name] = {
            "threshold": threshold,
            "precision": prf["precision"],
            "recall": prf["recall"],
            "f1": prf["f1"],
            "auroc": _auc_roc(labels_test, scores_test),
            "prauc": _auc_pr(labels_test, scores_test),
        }

    gibbs_metrics = metrics["gibbs"]
    measurable_win = False
    for baseline_name in ("tv", "wavelet"):
        baseline_metrics = metrics[baseline_name]
        if (
            gibbs_metrics["f1"] > baseline_metrics["f1"] + 0.01
            or gibbs_metrics["auroc"] > baseline_metrics["auroc"] + 0.01
            or gibbs_metrics["prauc"] > baseline_metrics["prauc"] + 0.01
        ):
            measurable_win = True
            break

    gibbs_pred = scores_test_cache["gibbs"] >= thresholds["gibbs"]
    tv_pred = scores_test_cache["tv"] >= thresholds["tv"]
    wavelet_pred = scores_test_cache["wavelet"] >= thresholds["wavelet"]
    labels_test = labels_test_cache["gibbs"]
    ids_test = ids_test_cache["gibbs"]

    for idx, sample_id in enumerate(ids_test):
        if labels_test[idx] != gibbs_pred[idx] and (labels_test[idx] == tv_pred[idx] or labels_test[idx] == wavelet_pred[idx]):
            non_win_cases.append(sample_id)
        if len(non_win_cases) >= 5:
            break

    gate = {
        "pass": bool(measurable_win),
        "metrics": metrics,
        "measurable_win": bool(measurable_win),
        "non_win_cases": non_win_cases,
    }

    out_dir = Path(output_dir)
    _ensure_dir(out_dir)
    with (out_dir / "baseline_comparison.json").open("w", encoding="utf-8") as handle:
        json.dump(gate, handle, indent=2)

    return gate


def run_noise_robustness_gate(
    output_dir: str = "results",
    snr_values: Sequence[float] = (30.0, 20.0, 10.0, 5.0),
) -> Dict[str, object]:
    clean = step_function_fixture(num_samples=2048)
    cfg = GibbsConfig(noise_policy="robust", n_values=(16, 32, 64, 96), jump_threshold=0.20)
    clean_report = detect_gibbs(clean, cfg)

    rows: List[Dict[str, float]] = []
    for snr in snr_values:
        noisy = noisy_discontinuity_fixture(num_samples=2048, snr_db=float(snr), seed=int(100 + snr))
        report = detect_gibbs(noisy, cfg)
        rows.append(
            {
                "snr_db": float(snr),
                "jump_active": float(report.jump_active),
                "jump_score_drift": abs(report.jump_score - clean_report.jump_score),
                "invariant_residual_drift": abs(report.invariant_residual - clean_report.invariant_residual),
            }
        )

    mean_score_drift = float(np.mean([r["jump_score_drift"] for r in rows]))
    max_residual_drift = float(np.max([r["invariant_residual_drift"] for r in rows]))
    active_rate = float(np.mean([r["jump_active"] for r in rows]))

    production_rows = [r for r in rows if r["snr_db"] >= 20.0]
    production_mean_score_drift = float(np.mean([r["jump_score_drift"] for r in production_rows])) if production_rows else mean_score_drift
    production_max_residual_drift = float(np.max([r["invariant_residual_drift"] for r in production_rows])) if production_rows else max_residual_drift

    # Bounded degradation requirement:
    # - stable on production SNR range (>=20 dB),
    # - no collapse under stress SNR points.
    gate_pass = bool(
        production_mean_score_drift <= 0.20
        and production_max_residual_drift <= 0.25
        and active_rate >= 0.75
    )
    gate = {
        "pass": gate_pass,
        "mean_score_drift": mean_score_drift,
        "max_invariant_residual_drift": max_residual_drift,
        "production_mean_score_drift": production_mean_score_drift,
        "production_max_invariant_residual_drift": production_max_residual_drift,
        "active_rate": active_rate,
        "rows": rows,
    }

    out_dir = Path(output_dir)
    _ensure_dir(out_dir)
    with (out_dir / "noise_robustness.json").open("w", encoding="utf-8") as handle:
        json.dump(gate, handle, indent=2)

    return gate


def run_nonuniform_sampling_gate(output_dir: str = "results") -> Dict[str, object]:
    num_samples = 2048
    x_uniform = uniform_grid(num_samples)
    y_clean = step_function_fixture(num_samples)

    cfg = GibbsConfig(noise_policy="none", sampling_mode="uniform", n_values=(16, 32, 64, 96), jump_threshold=0.20)
    baseline = detect_gibbs(y_clean, cfg)

    x_jittered = jittered_sampling_grid(num_samples=num_samples, jitter_fraction=0.30, seed=9)
    y_jittered = np.where(x_jittered < 0.0, -1.0, 1.0)
    _, y_resampled = resample_to_uniform(x_jittered, y_jittered, num_samples=num_samples)

    resampled = detect_gibbs(y_resampled, GibbsConfig(noise_policy="none", sampling_mode="jittered", n_values=cfg.n_values))

    invariant_drift = abs(resampled.invariant_residual - baseline.invariant_residual)
    energy_drift = abs(resampled.energy_redistribution - baseline.energy_redistribution)
    score_drift = abs(resampled.jump_score - baseline.jump_score)

    gate_pass = bool(invariant_drift <= 0.08 and energy_drift <= 0.12 and score_drift <= 0.20)
    gate = {
        "pass": gate_pass,
        "invariant_drift": float(invariant_drift),
        "energy_drift": float(energy_drift),
        "jump_score_drift": float(score_drift),
    }

    out_dir = Path(output_dir)
    _ensure_dir(out_dir)
    with (out_dir / "nonuniform_sampling.json").open("w", encoding="utf-8") as handle:
        json.dump(gate, handle, indent=2)

    return gate


def run_falsification_gates(
    output_dir: str = "results",
    baseline_sample_count: int = 200,
    baseline_num_samples: int = 1024,
) -> Dict[str, object]:
    out_dir = Path(output_dir)
    _ensure_dir(out_dir)

    noise_gate = run_noise_robustness_gate(output_dir=output_dir)
    nonuniform_gate = run_nonuniform_sampling_gate(output_dir=output_dir)
    baseline_gate = run_baseline_comparison_gate(
        output_dir=output_dir,
        sample_count=baseline_sample_count,
        num_samples=baseline_num_samples,
    )

    all_pass = bool(noise_gate["pass"] and nonuniform_gate["pass"] and baseline_gate["pass"])
    summary = {
        "all_pass": all_pass,
        "noise_robustness": noise_gate,
        "nonuniform_sampling": nonuniform_gate,
        "baseline_comparison": baseline_gate,
    }

    with (out_dir / "gates_report.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)

    return summary


def run_phase2(output_dir: str = "results") -> Dict[str, str]:
    invariant_csv = run_invariant_convergence(output_dir=output_dir)
    overshoot_json = run_overshoot_prediction(output_dir=output_dir)
    energy_npy = run_spectral_curvature_tests(output_dir=output_dir)
    figure = plot_invariant_convergence(invariant_csv=str(invariant_csv), output_path=f"{output_dir}/invariant_convergence.png")
    return {
        "invariant_residuals_csv": str(invariant_csv),
        "overshoot_profiles_json": str(overshoot_json),
        "energy_maps_npy": str(energy_npy),
        "canonical_plot": str(figure),
    }


def run_all_phase2_artifacts(output_dir: str = "results") -> Dict[str, object]:
    phase2 = run_phase2(output_dir=output_dir)
    gates = run_falsification_gates(output_dir=output_dir)
    summary = {"phase2_artifacts": phase2, "phase2b_gates": gates}

    out_dir = Path(output_dir)
    with (out_dir / "phase2_summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)

    return summary
