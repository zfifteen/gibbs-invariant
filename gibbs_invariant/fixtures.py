"""Deterministic benchmark fixtures for v1 experiments."""

from __future__ import annotations

from typing import Dict

import numpy as np

from .metrics import add_gaussian_noise, sawtooth_wave, square_wave, triangle_wave, uniform_grid


def step_function_fixture(num_samples: int = 2048) -> np.ndarray:
    x = uniform_grid(num_samples)
    return np.where(x < 0.0, -1.0, 1.0)


def square_wave_fixture(num_samples: int = 2048) -> np.ndarray:
    x = uniform_grid(num_samples)
    return square_wave(x)


def sawtooth_fixture(num_samples: int = 2048) -> np.ndarray:
    x = uniform_grid(num_samples)
    return sawtooth_wave(x)


def triangle_fixture(num_samples: int = 2048) -> np.ndarray:
    x = uniform_grid(num_samples)
    return triangle_wave(x)


def bandlimited_edge_fixture(num_samples: int = 2048) -> np.ndarray:
    x = uniform_grid(num_samples)
    smooth_edge = np.tanh(8.0 * x)
    ripple = 0.10 * np.sin(9.0 * x)
    return smooth_edge + ripple


def noisy_discontinuity_fixture(
    num_samples: int = 2048,
    snr_db: float = 15.0,
    seed: int = 7,
) -> np.ndarray:
    clean = step_function_fixture(num_samples)
    return add_gaussian_noise(clean, snr_db=snr_db, seed=seed)


def all_fixtures(num_samples: int = 2048) -> Dict[str, np.ndarray]:
    return {
        "step_function": step_function_fixture(num_samples),
        "square_wave": square_wave_fixture(num_samples),
        "bandlimited_edge": bandlimited_edge_fixture(num_samples),
        "noisy_discontinuity": noisy_discontinuity_fixture(num_samples),
    }
