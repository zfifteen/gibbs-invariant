"""Invariant-constrained loss helpers."""

from __future__ import annotations

import numpy as np


def reconstruction_error(reconstruction: np.ndarray, target: np.ndarray) -> float:
    return float(np.mean((np.asarray(reconstruction) - np.asarray(target)) ** 2))


def invariant_constrained_loss(
    reconstruction: np.ndarray,
    target: np.ndarray,
    invariant_residual: float,
    lambda_weight: float,
) -> float:
    base = reconstruction_error(reconstruction=reconstruction, target=target)
    return float(base + lambda_weight * (invariant_residual**2))
