"""Public detection APIs for Gibbs-invariant diagnostics."""

from __future__ import annotations

from typing import Optional

import numpy as np

from .metrics import (
    GIBBS_OVERSHOOT_FRACTION_JUMP,
    GIBBS_RADIUS_DELTA,
    compute_jump_indices,
    energy_concentration_from_reconstruction,
    fft_partial_sum,
    measured_overshoot_fraction,
    radius_doubling_deltas,
)
from .types import GibbsConfig, GibbsReport, RiskReport


def _smooth_signal(signal: np.ndarray, window: int = 5) -> np.ndarray:
    if window <= 1:
        return signal.copy()
    kernel = np.ones(window, dtype=float) / float(window)
    padded = np.concatenate([signal[-(window - 1) :], signal, signal[: window - 1]])
    smoothed = np.convolve(padded, kernel, mode="valid")
    return smoothed[: signal.size]


def risk(coefficients: np.ndarray, config: Optional[GibbsConfig] = None) -> RiskReport:
    cfg = (config or GibbsConfig()).validated()
    radii = np.abs(np.asarray(coefficients, dtype=float))
    if radii.size < 8:
        return RiskReport(jump_score=0.0, jump_active=False, threshold_used=cfg.jump_threshold)

    deltas = radius_doubling_deltas(radii, min_n=4)
    if not deltas:
        return RiskReport(jump_score=0.0, jump_active=False, threshold_used=cfg.jump_threshold)

    recent_avg = float(np.mean(deltas[-min(6, len(deltas)) :]))
    plateau = float(np.max(radii)) if np.max(radii) > 0 else 1.0
    jump_score = recent_avg / plateau

    return RiskReport(
        jump_score=float(jump_score),
        jump_active=bool(jump_score > cfg.jump_threshold),
        threshold_used=float(cfg.jump_threshold),
    )


def detect_gibbs(signal: np.ndarray, config: Optional[GibbsConfig] = None) -> GibbsReport:
    cfg = (config or GibbsConfig()).validated()
    values = np.asarray(signal, dtype=float)
    if values.ndim != 1:
        raise ValueError("signal must be one-dimensional")
    if values.size < 64:
        raise ValueError("signal must have at least 64 samples")

    processed = values.copy()
    if cfg.noise_policy == "robust":
        processed = _smooth_signal(processed, window=5)

    n_ref = max(cfg.n_values)
    reconstruction = fft_partial_sum(processed, n_harmonics=n_ref)
    jump_indices = compute_jump_indices(processed, top_k=2)
    jump_index = int(jump_indices[np.argmax(np.abs(np.diff(processed, append=processed[0]))[jump_indices])])
    window_radius = max(6, processed.size // max(16, 2 * n_ref))

    overshoot_ratio = measured_overshoot_fraction(
        signal=processed,
        reconstruction=reconstruction,
        jump_index=jump_index,
        window_radius=window_radius,
    )
    energy_redistribution = energy_concentration_from_reconstruction(
        signal=processed,
        reconstruction=reconstruction,
        jump_indices=jump_indices,
        n_harmonics=n_ref,
        alpha=cfg.alpha,
    )

    coeff = np.abs(np.fft.rfft(processed))[1:]
    risk_report = risk(coefficients=coeff, config=cfg)

    invariant_residual = overshoot_ratio - GIBBS_OVERSHOOT_FRACTION_JUMP
    radius_residual = risk_report.jump_score - GIBBS_RADIUS_DELTA
    energy_residual = energy_redistribution - 0.89

    return GibbsReport(
        overshoot_ratio=float(overshoot_ratio),
        energy_redistribution=float(energy_redistribution),
        invariant_residual=float(invariant_residual),
        jump_score=float(risk_report.jump_score),
        jump_active=bool(risk_report.jump_active),
        radius_residual=float(radius_residual),
        energy_residual=float(energy_residual),
    )
