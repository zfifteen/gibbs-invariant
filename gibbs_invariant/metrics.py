"""Core metrics and signal utilities for the Gibbs invariant project."""

from __future__ import annotations

from typing import Callable, List, Optional, Sequence, Tuple

import numpy as np

GIBBS_RADIUS_DELTA = 2 / np.pi * np.log(2)
DEFAULT_THRESHOLD = 0.20
GIBBS_OVERSHOOT_LIMIT = 1.178979744472167
GIBBS_OVERSHOOT_FRACTION_JUMP = (GIBBS_OVERSHOOT_LIMIT - 1.0) / 2.0
RADIUS_BUDGET_ASYMPTOTIC_CONSTANT = (2 / np.pi) * (2 * np.log(2) + np.euler_gamma)
ENERGY_ZONE_WIDTH_FACTOR = 1.0


def uniform_grid(num_samples: int = 65536) -> np.ndarray:
    return np.linspace(-np.pi, np.pi, num_samples, endpoint=False)


def square_wave(x: np.ndarray, amplitude: float = 1.0) -> np.ndarray:
    return amplitude * np.where(np.sin(x) >= 0.0, 1.0, -1.0)


def sawtooth_wave(x: np.ndarray, amplitude: float = 1.0) -> np.ndarray:
    x_wrapped = ((x + np.pi) % (2 * np.pi)) - np.pi
    return amplitude * (x_wrapped / np.pi)


def triangle_wave(x: np.ndarray, amplitude: float = 1.0) -> np.ndarray:
    x_wrapped = ((x + np.pi) % (2 * np.pi)) - np.pi
    return (2.0 * amplitude / np.pi) * np.arcsin(np.sin(x_wrapped))


def square_wave_partial_sum(x: np.ndarray, N: int, amplitude: float = 1.0) -> np.ndarray:
    if N < 1:
        return np.zeros_like(x, dtype=float)
    k = np.arange(1, 2 * N, 2, dtype=float)
    return (4.0 * amplitude / np.pi) * np.sum(np.sin(np.outer(k, x)) / k[:, None], axis=0)


def sawtooth_partial_sum(x: np.ndarray, N: int, amplitude: float = 1.0) -> np.ndarray:
    if N < 1:
        return np.zeros_like(x, dtype=float)
    k = np.arange(1, N + 1, dtype=float)
    coeff = (2.0 * amplitude / np.pi) * ((-1.0) ** (k + 1.0)) / k
    return np.sum(coeff[:, None] * np.sin(np.outer(k, x)), axis=0)


def triangle_partial_sum(x: np.ndarray, N: int, amplitude: float = 1.0) -> np.ndarray:
    if N < 1:
        return np.zeros_like(x, dtype=float)
    k = np.arange(1, 2 * N, 2, dtype=float)
    coeff = (8.0 * amplitude / (np.pi**2)) * ((-1.0) ** ((k - 1.0) / 2.0)) / (k**2)
    return np.sum(coeff[:, None] * np.sin(np.outer(k, x)), axis=0)


def square_wave_radii(N: int, amplitude: float = 1.0) -> np.ndarray:
    k = np.arange(1, 2 * N, 2, dtype=float)
    return (4 * amplitude) / (np.pi * k)


def sawtooth_radii(N: int, amplitude: float = 1.0) -> np.ndarray:
    k = np.arange(1, N + 1, dtype=float)
    return (2 * amplitude) / (np.pi * k)


def triangle_radii(N: int, amplitude: float = 1.0) -> np.ndarray:
    k = np.arange(1, 2 * N, 2, dtype=float)
    return (8.0 * amplitude) / (np.pi**2 * k**2)


def cumulative_radius_budget(radii: np.ndarray) -> np.ndarray:
    return np.cumsum(radii)


def periodic_closure_gap(signal: np.ndarray) -> float:
    values = np.asarray(signal, dtype=float)
    if values.size < 2:
        return 0.0
    return float(abs(values[0] - values[-1]))


def periodic_closure_ratio(signal: np.ndarray) -> float:
    values = np.asarray(signal, dtype=float)
    amplitude = float(np.max(values) - np.min(values)) if values.size else 0.0
    if amplitude <= 1e-12:
        return 0.0
    return float(periodic_closure_gap(values) / amplitude)


def radius_doubling_deltas(radii: np.ndarray, min_n: int = 8) -> List[float]:
    deltas: List[float] = []
    n = max(min_n, 1)
    while 2 * n <= len(radii):
        delta = radii[: 2 * n].sum() - radii[:n].sum()
        deltas.append(float(delta))
        n *= 2
    return deltas


def has_true_jumps(
    radii: np.ndarray,
    plateau: float = 1.0,
    threshold: float = DEFAULT_THRESHOLD,
) -> Tuple[bool, float]:
    if plateau <= 0:
        raise ValueError("plateau must be positive")
    deltas = radius_doubling_deltas(radii)
    if not deltas:
        return False, 0.0
    recent_avg = float(np.mean(deltas[-6:]))
    score = recent_avg / plateau
    return score > threshold, round(score, 4)


def gibbs_overshoot(
    N: int,
    amplitude: float = 1.0,
    local_samples_per_harmonic: int = 64,
) -> float:
    m = max(4096, local_samples_per_harmonic * N)
    window = 6.0 * np.pi / max(N, 1)
    x_local = np.linspace(-window, window, m, endpoint=False)
    approx_local = square_wave_partial_sum(x_local, N=N, amplitude=amplitude)
    mask = np.abs(x_local) < 4 * np.pi / max(N, 1)
    return float(np.max(approx_local[mask]) if np.any(mask) else 0.0)


def energy_concentration_fraction(
    N: int,
    x: np.ndarray,
    amplitude: float = 1.0,
    zone_width_factor: float = ENERGY_ZONE_WIDTH_FACTOR,
) -> float:
    return energy_concentration_fraction_for_signal(
        N=N,
        x=x,
        target_fn=lambda z: square_wave(z, amplitude=amplitude),
        partial_sum_fn=lambda z, n: square_wave_partial_sum(z, N=n, amplitude=amplitude),
        jump_locations=(0.0, np.pi, -np.pi),
        zone_width_factor=zone_width_factor,
        harmonic_bandwidth="odd",
    )


def sawtooth_energy_concentration_fraction(
    N: int,
    x: np.ndarray,
    amplitude: float = 1.0,
    zone_width_factor: float = ENERGY_ZONE_WIDTH_FACTOR,
) -> float:
    return energy_concentration_fraction_for_signal(
        N=N,
        x=x,
        target_fn=lambda z: sawtooth_wave(z, amplitude=amplitude),
        partial_sum_fn=lambda z, n: sawtooth_partial_sum(z, N=n, amplitude=amplitude),
        jump_locations=(np.pi, -np.pi),
        zone_width_factor=zone_width_factor,
        harmonic_bandwidth="all",
    )


def energy_concentration_fraction_for_signal(
    N: int,
    x: np.ndarray,
    target_fn: Callable[[np.ndarray], np.ndarray],
    partial_sum_fn: Callable[[np.ndarray, int], np.ndarray],
    jump_locations: Tuple[float, ...],
    zone_width_factor: float = ENERGY_ZONE_WIDTH_FACTOR,
    harmonic_bandwidth: str = "all",
) -> float:
    if N < 1:
        return 0.0

    approx = partial_sum_fn(x, N)
    target = target_fn(x)
    err2 = (approx - target) ** 2
    total = float(np.sum(err2))
    if total == 0.0:
        return 0.0

    denom = (2 * N + 1) if harmonic_bandwidth == "odd" else N
    width = zone_width_factor * np.pi / max(denom, 1)
    x_wrapped = ((x + np.pi) % (2 * np.pi)) - np.pi
    zone_mask = np.zeros_like(x_wrapped, dtype=bool)
    for jump in jump_locations:
        jump_wrapped = ((jump + np.pi) % (2 * np.pi)) - np.pi
        dist = np.abs(x_wrapped - jump_wrapped)
        dist = np.minimum(dist, 2 * np.pi - dist)
        zone_mask |= dist <= width
    zone = float(np.sum(err2[zone_mask]))
    return zone / total


def estimate_crossover_harmonic(max_N: int = 200) -> Optional[int]:
    x = uniform_grid(131072)
    target = square_wave(x)
    for N in range(2, max_N + 1):
        approx = square_wave_partial_sum(x, N)
        rms = float(np.sqrt(np.mean((approx - target) ** 2)))
        fixed_point_error = (gibbs_overshoot(N) - 1.0) / 2.0
        if fixed_point_error > rms:
            return N
    return None


def fft_partial_sum(signal: np.ndarray, n_harmonics: int) -> np.ndarray:
    """Return periodic reconstruction with low-frequency FFT harmonics only."""
    m = int(signal.shape[0])
    if m < 4:
        raise ValueError("signal length must be at least 4")

    n_harmonics = max(1, min(n_harmonics, (m // 2) - 1))
    coeff = np.fft.fft(signal)
    truncated = np.zeros_like(coeff)
    truncated[0 : n_harmonics + 1] = coeff[0 : n_harmonics + 1]
    truncated[-n_harmonics:] = coeff[-n_harmonics:]
    return np.fft.ifft(truncated).real


def compute_jump_indices(signal: np.ndarray, top_k: int = 2) -> np.ndarray:
    grad = np.abs(np.diff(signal, append=signal[0]))
    k = int(max(1, min(top_k, grad.size)))
    return np.argpartition(grad, -k)[-k:]


def zone_mask_from_jumps(
    length: int,
    jump_indices: Sequence[int],
    n_harmonics: int,
    alpha: float = 1.0,
) -> np.ndarray:
    mask = np.zeros(length, dtype=bool)
    if length <= 0:
        return mask
    radius = max(1, int(np.ceil(alpha * length / (2.0 * max(n_harmonics, 1)))))
    for index in jump_indices:
        i = int(index) % length
        for offset in range(-radius, radius + 1):
            mask[(i + offset) % length] = True
    return mask


def energy_concentration_from_reconstruction(
    signal: np.ndarray,
    reconstruction: np.ndarray,
    jump_indices: Sequence[int],
    n_harmonics: int,
    alpha: float = 1.0,
) -> float:
    err2 = (reconstruction - signal) ** 2
    total = float(np.sum(err2))
    if total == 0.0:
        return 0.0
    mask = zone_mask_from_jumps(signal.size, jump_indices, n_harmonics, alpha)
    return float(np.sum(err2[mask]) / total)


def measured_overshoot_fraction(
    signal: np.ndarray,
    reconstruction: np.ndarray,
    jump_index: int,
    window_radius: int,
) -> float:
    m = signal.size
    window_radius = max(2, min(window_radius, max(3, (m // 8))))
    idx = int(jump_index) % m

    left_slice = signal[(idx - window_radius) % m : idx]
    if left_slice.size == 0:
        left_slice = signal[max(0, idx - window_radius) : idx]
    right_slice = signal[idx : idx + window_radius]
    if right_slice.size == 0:
        right_slice = signal[idx : min(m, idx + window_radius)]

    if left_slice.size == 0 or right_slice.size == 0:
        return 0.0

    left_mean = float(np.mean(left_slice))
    right_mean = float(np.mean(right_slice))
    jump_height = abs(right_mean - left_mean)
    if jump_height < 1e-12:
        return 0.0

    window_indices = [(idx + offset) % m for offset in range(-window_radius, window_radius + 1)]
    local = reconstruction[window_indices]
    if right_mean >= left_mean:
        overshoot = float(np.max(local) - max(left_mean, right_mean))
    else:
        overshoot = float(min(left_mean, right_mean) - np.min(local))

    return max(0.0, overshoot / jump_height)


def add_gaussian_noise(signal: np.ndarray, snr_db: float, seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    power = float(np.mean(signal**2))
    if power <= 0.0:
        return signal.copy()
    noise_power = power / (10.0 ** (snr_db / 10.0))
    noise = rng.normal(0.0, np.sqrt(noise_power), size=signal.shape)
    return signal + noise


def jittered_sampling_grid(
    num_samples: int,
    jitter_fraction: float = 0.25,
    seed: int = 0,
) -> np.ndarray:
    if num_samples < 8:
        raise ValueError("num_samples must be >= 8")
    rng = np.random.default_rng(seed)
    x_uniform = uniform_grid(num_samples)
    spacing = (2.0 * np.pi) / num_samples
    jitter = rng.uniform(-jitter_fraction, jitter_fraction, size=num_samples) * spacing
    x_jittered = np.sort(x_uniform + jitter)
    return x_jittered


def resample_to_uniform(x: np.ndarray, y: np.ndarray, num_samples: int) -> Tuple[np.ndarray, np.ndarray]:
    order = np.argsort(x)
    x_sorted = x[order]
    y_sorted = y[order]
    x_target = uniform_grid(num_samples)

    x_ext = np.concatenate([x_sorted - 2.0 * np.pi, x_sorted, x_sorted + 2.0 * np.pi])
    y_ext = np.concatenate([y_sorted, y_sorted, y_sorted])
    y_target = np.interp(x_target, x_ext, y_ext)
    return x_target, y_target


def spectral_curvature(signal: np.ndarray, n_harmonics: int) -> np.ndarray:
    recon = fft_partial_sum(signal, n_harmonics)
    grad = np.diff(recon, append=recon[0])
    return np.abs(np.diff(grad, append=grad[0]))
