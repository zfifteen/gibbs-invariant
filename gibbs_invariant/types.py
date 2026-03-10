"""Public datatypes for the Gibbs invariant APIs."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True)
class GibbsConfig:
    """Configuration for v1 Gibbs detection and risk scoring APIs."""

    n_values: Tuple[int, ...] = field(default_factory=lambda: (16, 32, 64, 128, 256))
    alpha: float = 1.0
    jump_threshold: float = 0.20
    noise_policy: str = "none"
    sampling_mode: str = "uniform"

    def validated(self) -> "GibbsConfig":
        if not self.n_values:
            raise ValueError("n_values must contain at least one harmonic count")
        if any(n < 2 for n in self.n_values):
            raise ValueError("n_values must contain values >= 2")
        if self.alpha <= 0:
            raise ValueError("alpha must be positive")
        if self.jump_threshold <= 0:
            raise ValueError("jump_threshold must be positive")
        if self.noise_policy not in {"none", "robust"}:
            raise ValueError("noise_policy must be one of: none, robust")
        if self.sampling_mode not in {"uniform", "jittered"}:
            raise ValueError("sampling_mode must be one of: uniform, jittered")
        return self


@dataclass(frozen=True)
class RiskReport:
    jump_score: float
    jump_active: bool
    threshold_used: float


@dataclass(frozen=True)
class GibbsReport:
    overshoot_ratio: float
    energy_redistribution: float
    invariant_residual: float
    jump_score: float
    jump_active: bool
    radius_residual: float
    energy_residual: float
