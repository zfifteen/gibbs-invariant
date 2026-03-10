"""Toy constrained-optimization prototypes for v1 evaluation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, Tuple

import numpy as np

from ..metrics import (
    GIBBS_OVERSHOOT_FRACTION_JUMP,
    add_gaussian_noise,
    compute_jump_indices,
    fft_partial_sum,
    measured_overshoot_fraction,
    uniform_grid,
)
from .invariant_loss import reconstruction_error


def _edge_zone_mask(signal: np.ndarray, radius: int = 40) -> np.ndarray:
    idx = compute_jump_indices(signal, top_k=2)
    mask = np.zeros(signal.size, dtype=bool)
    for i in idx:
        for offset in range(-radius, radius + 1):
            mask[(int(i) + offset) % signal.size] = True
    return mask


def _zone_mse(reconstruction: np.ndarray, target: np.ndarray, mask: np.ndarray) -> Tuple[float, float]:
    err2 = (reconstruction - target) ** 2
    edge = float(np.mean(err2[mask])) if np.any(mask) else 0.0
    smooth_mask = ~mask
    smooth = float(np.mean(err2[smooth_mask])) if np.any(smooth_mask) else 0.0
    return edge, smooth


def _build_tasks(num_samples: int = 2048, seed: int = 123) -> Dict[str, Dict[str, np.ndarray]]:
    x = uniform_grid(num_samples)

    target_base = np.where(x < 0.0, -1.0, 1.0)

    denoise_target = target_base
    denoise_obs = add_gaussian_noise(denoise_target, snr_db=14.0, seed=seed)

    trunc_target = target_base + 0.15 * np.sin(3 * x)
    trunc_obs = fft_partial_sum(trunc_target, n_harmonics=24)

    smooth_target = target_base + 0.08 * np.sin(8 * x)
    blurred = np.convolve(
        np.concatenate([smooth_target[-2:], smooth_target, smooth_target[:2]]),
        np.array([0.15, 0.2, 0.3, 0.2, 0.15]),
        mode="valid",
    )
    smooth_obs = add_gaussian_noise(blurred, snr_db=20.0, seed=seed + 4)

    return {
        "denoising": {"target": denoise_target, "observation": denoise_obs},
        "truncated_fourier_reconstruction": {"target": trunc_target, "observation": trunc_obs},
        "edge_preserving_smoothing": {"target": smooth_target, "observation": smooth_obs},
    }


def _evaluate_task(
    target: np.ndarray,
    observation: np.ndarray,
    n_values: Iterable[int],
    lambda_weight: float,
    smooth_tolerance: float,
) -> Dict[str, float]:
    unique_n = tuple(sorted(set(int(n) for n in n_values)))
    edge_mask = _edge_zone_mask(target)
    edge_mask_float = edge_mask.astype(float)
    jump_index = int(compute_jump_indices(target, top_k=1)[0])

    candidates = []
    for n in unique_n:
        base_recon = fft_partial_sum(observation, n_harmonics=int(n))
        for beta in (0.0, 0.25, 0.50, 0.75):
            # Local edge blend introduces a controllable edge/smooth tradeoff.
            recon = base_recon + beta * edge_mask_float * (observation - base_recon)
            window_radius = max(8, target.size // max(16, 2 * int(n)))
            overshoot_fraction = measured_overshoot_fraction(
                signal=target,
                reconstruction=recon,
                jump_index=jump_index,
                window_radius=window_radius,
            )
            invariant_residual = overshoot_fraction - GIBBS_OVERSHOOT_FRACTION_JUMP
            mse = reconstruction_error(recon, target)
            edge_mse, smooth_mse = _zone_mse(recon, target, edge_mask)
            # In v1 we optimize smooth-zone fidelity and use invariant residual to
            # discourage over-smoothing of discontinuity neighborhoods.
            constrained = smooth_mse + lambda_weight * (invariant_residual**2)
            candidates.append(
                {
                    "n": int(n),
                    "beta": float(beta),
                    "reconstruction": recon,
                    "mse": mse,
                    "objective_error": float(smooth_mse),
                    "constrained_loss": constrained,
                    "edge_mse": edge_mse,
                    "smooth_mse": smooth_mse,
                    "invariant_residual": invariant_residual,
                }
            )

    baseline = min([row for row in candidates if row["beta"] == 0.0], key=lambda row: row["objective_error"])
    constrained_best = min(candidates, key=lambda row: row["constrained_loss"])

    edge_improvement = baseline["edge_mse"] - constrained_best["edge_mse"]
    smooth_regression = constrained_best["smooth_mse"] - baseline["smooth_mse"]
    pass_gate = bool(edge_improvement > 0.0 and smooth_regression <= smooth_tolerance)

    return {
        "baseline_n": int(baseline["n"]),
        "baseline_beta": float(baseline["beta"]),
        "constrained_n": int(constrained_best["n"]),
        "constrained_beta": float(constrained_best["beta"]),
        "baseline_mse": float(baseline["mse"]),
        "constrained_mse": float(constrained_best["mse"]),
        "baseline_edge_mse": float(baseline["edge_mse"]),
        "constrained_edge_mse": float(constrained_best["edge_mse"]),
        "baseline_smooth_mse": float(baseline["smooth_mse"]),
        "constrained_smooth_mse": float(constrained_best["smooth_mse"]),
        "edge_improvement": float(edge_improvement),
        "smooth_regression": float(smooth_regression),
        "pass": pass_gate,
    }


def run_constraint_prototype(
    output_dir: str = "results",
    lambda_weight: float = 0.35,
    smooth_tolerance: float = 0.02,
    n_values: Iterable[int] = (8, 12, 16, 24, 32, 48, 64),
) -> Dict[str, object]:
    tasks = _build_tasks(num_samples=2048, seed=123)
    results: Dict[str, Dict[str, float]] = {}

    for name, payload in tasks.items():
        results[name] = _evaluate_task(
            target=payload["target"],
            observation=payload["observation"],
            n_values=n_values,
            lambda_weight=lambda_weight,
            smooth_tolerance=smooth_tolerance,
        )

    task_pass_count = int(sum(1 for row in results.values() if row["pass"]))
    max_smooth_regression = float(max(row["smooth_regression"] for row in results.values()))
    non_win_tasks = [name for name, row in results.items() if row["edge_improvement"] <= 0.0]

    # Prototype acceptance gate:
    # - at least one toy task must show edge improvement
    # - no task may exceed smooth-region regression tolerance.
    overall_pass = bool(task_pass_count >= 1 and max_smooth_regression <= smooth_tolerance)
    summary: Dict[str, object] = {
        "pass": overall_pass,
        "lambda_weight": float(lambda_weight),
        "smooth_tolerance": float(smooth_tolerance),
        "task_pass_count": task_pass_count,
        "max_smooth_regression": max_smooth_regression,
        "non_win_tasks": non_win_tasks,
        "tasks": results,
    }

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "constrained_metrics.json"
    with out_path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)

    return summary
