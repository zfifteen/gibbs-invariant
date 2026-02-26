"""
gibbs_invariant.py  v2.4 — Verified
Official implementation of both Gibbs invariants
https://github.com/zfifteen/gibbs-invariant
"""

import numpy as np
from typing import Tuple, List, Optional
import matplotlib.pyplot as plt

# ========================= CONSTANTS =========================
GIBBS_RADIUS_DELTA = 2 / np.pi * np.log(2)          # 0.4412712003053032
DEFAULT_THRESHOLD = 0.20
GIBBS_OVERSHOOT_LIMIT = 1.178979744472167   # exact Wilbraham–Gibbs constant (plateau=1)
GIBBS_OVERSHOOT_FRACTION_JUMP = (GIBBS_OVERSHOOT_LIMIT - 1.0) / 2.0  # ~0.08949 of jump height
RADIUS_BUDGET_ASYMPTOTIC_CONSTANT = (2 / np.pi) * (2 * np.log(2) + np.euler_gamma)
ENERGY_ZONE_WIDTH_FACTOR = 1.0

# ========================= SIGNALS =========================
def square_wave(x: np.ndarray, amplitude: float = 1.0) -> np.ndarray:
    return amplitude * np.where(np.sin(x) >= 0.0, 1.0, -1.0)

def square_wave_partial_sum(x: np.ndarray, N: int, amplitude: float = 1.0) -> np.ndarray:
    """N odd harmonics for a unit-periodized square wave on [-pi, pi)."""
    if N < 1:
        return np.zeros_like(x, dtype=float)
    k = np.arange(1, 2 * N, 2, dtype=float)
    return (4.0 * amplitude / np.pi) * np.sum(np.sin(np.outer(k, x)) / k[:, None], axis=0)

def sawtooth_wave(x: np.ndarray, amplitude: float = 1.0) -> np.ndarray:
    """Periodic sawtooth on [-pi, pi) with single jump at +/-pi."""
    x_wrapped = ((x + np.pi) % (2 * np.pi)) - np.pi
    return amplitude * (x_wrapped / np.pi)

def sawtooth_partial_sum(x: np.ndarray, N: int, amplitude: float = 1.0) -> np.ndarray:
    """N-harmonic sine series for sawtooth on [-pi, pi)."""
    if N < 1:
        return np.zeros_like(x, dtype=float)
    k = np.arange(1, N + 1, dtype=float)
    coeff = (2.0 * amplitude / np.pi) * ((-1.0) ** (k + 1.0)) / k
    return np.sum(coeff[:, None] * np.sin(np.outer(k, x)), axis=0)

# ========================= RADII (Theorem 2) =========================
def square_wave_radii(N: int, amplitude: float = 1.0) -> np.ndarray:
    k = np.arange(1, 2 * N, 2, dtype=float)
    return (4 * amplitude) / (np.pi * k)

def sawtooth_radii(N: int, amplitude: float = 1.0) -> np.ndarray:
    k = np.arange(1, N + 1, dtype=float)
    return (2 * amplitude) / (np.pi * k)

def cumulative_radius_budget(radii: np.ndarray) -> np.ndarray:
    return np.cumsum(radii)

def radius_doubling_deltas(radii: np.ndarray, min_n: int = 8) -> List[float]:
    """Return [R(2n)-R(n)] from small n to large n."""
    deltas: List[float] = []
    n = max(min_n, 1)
    while 2 * n <= len(radii):
        delta = radii[:2 * n].sum() - radii[:n].sum()
        deltas.append(delta)
        n *= 2
    return deltas

def has_true_jumps(radii: np.ndarray,
                   plateau: float = 1.0,
                   threshold: float = DEFAULT_THRESHOLD) -> Tuple[bool, float]:
    if plateau <= 0:
        raise ValueError("plateau must be positive")
    deltas = radius_doubling_deltas(radii)
    if not deltas:
        return False, 0.0
    recent_avg = np.mean(deltas[-6:])
    score = recent_avg / plateau
    return score > threshold, round(score, 4)

# ========================= THEOREM 1 METRICS =========================
def gibbs_overshoot(N: int,
                    amplitude: float = 1.0,
                    local_samples_per_harmonic: int = 64) -> float:
    """Maximum value of partial sum near x=0 jump (robust at high N)."""
    m = max(4096, local_samples_per_harmonic * N)
    window = 6.0 * np.pi / max(N, 1)
    x_local = np.linspace(-window, window, m, endpoint=False)
    approx_local = square_wave_partial_sum(x_local, N=N, amplitude=amplitude)
    mask = np.abs(x_local) < 4 * np.pi / max(N, 1)
    return float(np.max(approx_local[mask]) if np.any(mask) else 0.0)

def energy_concentration_fraction(N: int,
                                  x: np.ndarray,
                                  amplitude: float = 1.0,
                                  zone_width_factor: float = ENERGY_ZONE_WIDTH_FACTOR) -> float:
    """
    Fraction of squared error inside Gibbs zones around discontinuities.
    Zone width per jump: zone_width_factor * pi / (2N + 1).
    """
    return energy_concentration_fraction_for_signal(
        N=N,
        x=x,
        target_fn=lambda z: square_wave(z, amplitude=amplitude),
        partial_sum_fn=lambda z, n: square_wave_partial_sum(z, N=n, amplitude=amplitude),
        jump_locations=(0.0, np.pi, -np.pi),
        zone_width_factor=zone_width_factor,
        harmonic_bandwidth="odd",
    )

def energy_concentration_fraction_for_signal(
    N: int,
    x: np.ndarray,
    target_fn,
    partial_sum_fn,
    jump_locations: Tuple[float, ...],
    zone_width_factor: float = ENERGY_ZONE_WIDTH_FACTOR,
    harmonic_bandwidth: str = "all",
) -> float:
    """
    Fraction of squared reconstruction error inside Gibbs zones for a given signal.
    Zone width per jump is zone_width_factor * pi / K(N), where K(N)=2N+1 for odd-only
    truncations and K(N)=N for full-harmonic truncations.
    """
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

def estimate_crossover_harmonic(max_N: int = 200) -> Optional[int]:
    """Docs definition: first N where 8.95%-style pointwise error exceeds global RMS error."""
    x = np.linspace(-np.pi, np.pi, 131072, endpoint=False)
    target = square_wave(x)
    for N in range(2, max_N + 1):
        approx = square_wave_partial_sum(x, N)
        rms = float(np.sqrt(np.mean((approx - target) ** 2)))
        # Docs compare pointwise Gibbs error as a fraction of jump height (2 for plateau=1).
        fixed_point_error = (gibbs_overshoot(N) - 1.0) / 2.0
        if fixed_point_error > rms:
            return N
    return None

# ========================= PLOTS =========================
def plot_radius_budget(dark_mode: bool = True,
                       save_path: Optional[str] = "assets/radius_budget_verification.png"):
    """Theorem 2: persistent logarithmic radius-budget growth for true jumps."""
    Ns = np.logspace(1, 4.2, 120, dtype=int)
    budgets_sq = np.array([cumulative_radius_budget(square_wave_radii(int(n)))[-1] for n in Ns])
    budgets_saw = np.array([cumulative_radius_budget(sawtooth_radii(int(n)))[-1] for n in Ns])

    def triangle_radii(N: int):
        k = np.arange(1, 2 * N, 2, dtype=float)
        return 8.0 / (np.pi**2 * k**2)
    budgets_tri = np.array([cumulative_radius_budget(triangle_radii(int(n)))[-1] for n in Ns])

    theo = (2 / np.pi) * np.log(Ns) + RADIUS_BUDGET_ASYMPTOTIC_CONSTANT

    plt.figure(figsize=(12, 7))
    if dark_mode:
        plt.style.use('dark_background')
        color_sq = '#00eeff'
        color_saw = '#66ff66'
        color_tri = '#ff44cc'
        color_theo = '#ffcc44'
    else:
        color_sq = '#0088ff'
        color_saw = '#009944'
        color_tri = '#cc0088'
        color_theo = '#ff8800'

    plt.plot(Ns, budgets_sq, 'o-', color=color_sq, lw=2.8, ms=3.5,
             label='Square Wave (True Jumps — Theorem 2)')
    plt.plot(Ns, budgets_saw, '^-', color=color_saw, lw=2.2, ms=3.2,
             label='Sawtooth (True Jumps — 1/k tail)')
    plt.plot(Ns, budgets_tri, 's-', color=color_tri, lw=2.2, ms=3.5,
             label='Triangle Wave (Continuous — saturates)')
    plt.plot(Ns, theo, '--', color=color_theo, lw=2.4,
             label=f'Theoretical: (2/π)ln(N) + {RADIUS_BUDGET_ASYMPTOTIC_CONSTANT:.3f}')

    plt.xscale('log')
    plt.xlabel('Number of Harmonics N (log scale)', fontsize=13)
    plt.ylabel('Cumulative Circle-Length Budget R(N)', fontsize=13)
    plt.title('Gibbs Radius Invariant (Theorem 2) — Persistent Growth', fontsize=15, pad=15)
    plt.legend(fontsize=11.5, loc='upper left')
    plt.grid(True, alpha=0.35)

    plt.annotate('ΔR ≈ 0.4413\nper doubling',
                 xy=(400, 4.9), xytext=(1200, 3.8),
                 arrowprops=dict(arrowstyle='->', color=color_theo, lw=1.8),
                 fontsize=12, color=color_theo, ha='center')

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=420, bbox_inches='tight',
                    facecolor='black' if dark_mode else 'white')
    plt.show()


def plot_energy_invariant(dark_mode: bool = True,
                          save_path: Optional[str] = "assets/energy_invariant.png"):
    """Theorem 1: overshoot persistence + concentrated L2 error fraction."""
    Ns = [10, 25, 50, 100, 200, 400, 800, 1200, 2000]
    overshoots = []
    overshoot_fraction_jump = []
    concentrations = []
    x = np.linspace(-np.pi, np.pi, 65536, endpoint=False)

    if dark_mode:
        plt.style.use('dark_background')

    for N in Ns:
        ov = gibbs_overshoot(N)
        overshoots.append(ov)
        overshoot_fraction_jump.append((ov - 1.0) / 2.0)
        concentrations.append(energy_concentration_fraction(N, x))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.8))
    if dark_mode:
        color_ov = '#ffdd44'
        color_ec = '#2de2e6'
        hline = 'white'
    else:
        color_ov = '#ff8800'
        color_ec = '#0088ff'
        hline = 'black'

    ax1.plot(Ns, overshoot_fraction_jump, 'o-', color=color_ov, lw=3, ms=7,
             label='Numerical pointwise error / jump height')
    ax1.axhline(y=GIBBS_OVERSHOOT_FRACTION_JUMP, color=hline, ls='--', alpha=0.7,
                label=f'Theoretical level {GIBBS_OVERSHOOT_FRACTION_JUMP:.6f}')
    ax1.set_xscale('log')
    ax1.set_xlabel('N (log scale)')
    ax1.set_ylabel('Pointwise error fraction of jump')
    ax1.set_title('Persistent Gibbs Overshoot')
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=10)

    ax2.plot(Ns, concentrations, 'o-', color=color_ec, lw=3, ms=7,
             label='L2 error fraction in Gibbs zones')
    ax2.axhline(y=0.89, color=hline, ls='--', alpha=0.7, label='Claimed invariant level ~0.89')
    ax2.set_xscale('log')
    ax2.set_ylim(0.0, 1.0)
    ax2.set_xlabel('N (log scale)')
    ax2.set_ylabel('Error concentration fraction')
    ax2.set_title('Energy Concentration Invariant')
    ax2.grid(True, alpha=0.3)
    ax2.legend(fontsize=10)

    fig.suptitle('Gibbs Energy Invariant (Theorem 1)', fontsize=14)
    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=420, bbox_inches='tight',
                    facecolor='black' if dark_mode else 'white')
    plt.show()

# ========================= VERIFICATION =========================
def verify_invariants():
    N_list = [10, 25, 50, 100, 200, 500, 1000, 2000]
    x = np.linspace(-np.pi, np.pi, 65536, endpoint=False)

    print("Gibbs Invariants Verification v2.4")
    print("=" * 110)
    print(f"{'N':>5} | {'Budget':>7} | {'Δ/double':>9} | {'Overshoot':>10} | {'Err/jump':>9} | {'E-zone':>7} | {'Jumps?':>7} (score)")
    print("-" * 110)

    for N in N_list:
        approx = square_wave_partial_sum(x, N)
        target = square_wave(x)

        radii = square_wave_radii(N)
        cum_budget = cumulative_radius_budget(radii)[-1]
        deltas = radius_doubling_deltas(radii)
        avg_delta = np.mean(deltas) if deltas else 0.0
        overshoot = gibbs_overshoot(N)
        jump_error = overshoot - 1.0
        jump_fraction = jump_error / 2.0
        e_zone = energy_concentration_fraction(N, x)
        detects, score = has_true_jumps(radii)

        print(f"{N:5d} | {cum_budget:7.3f} | {avg_delta:9.4f} | {overshoot:10.6f} | {jump_fraction:9.5f} | "
              f"{e_zone:7.4f} | "
              f"{detects!s:>7}  ({score})")

    crossover = estimate_crossover_harmonic(max_N=120)
    print("-" * 110)
    print(f"Estimated crossover N where pointwise Gibbs error > global RMS error: {crossover}")
    print("Reference constants:")
    print(f"  Theorem 2 delta-per-doubling target: {GIBBS_RADIUS_DELTA:.12f}")
    print(f"  Theorem 1 overshoot target (plateau=1): {GIBBS_OVERSHOOT_LIMIT:.12f}")
    print(f"  Theorem 1 pointwise error as jump fraction: {GIBBS_OVERSHOOT_FRACTION_JUMP:.12f}")
    print()
    print("Additional discontinuous example (sawtooth):")
    print(f"{'N':>5} | {'R(N)':>7} | {'Δ/double':>9} | {'E-zone α=1':>11}")
    print("-" * 42)
    for N in [16, 32, 64, 128, 256, 512]:
        radii_sw = sawtooth_radii(N)
        deltas_sw = radius_doubling_deltas(radii_sw, min_n=8)
        avg_delta_sw = np.mean(deltas_sw[-3:]) if deltas_sw else 0.0
        e_zone_sw = sawtooth_energy_concentration_fraction(N, x, zone_width_factor=1.0)
        print(f"{N:5d} | {radii_sw.sum():7.3f} | {avg_delta_sw:9.4f} | {e_zone_sw:11.4f}")

    print()
    print("Zone-width robustness check (square wave):")
    for alpha in [0.5, 1.0, 2.0]:
        vals = [energy_concentration_fraction(N, x, zone_width_factor=alpha) for N in [64, 128, 256, 512, 1024]]
        print(f"  alpha={alpha:.1f}: mean={np.mean(vals):.4f}, min={np.min(vals):.4f}, max={np.max(vals):.4f}")

# ========================= RUN =========================
if __name__ == "__main__":
    print("Gibbs Invariant Library v2.4 — Verified Build\n")
    verify_invariants()
    plot_radius_budget(dark_mode=True)
    plot_energy_invariant(dark_mode=True)
    print("\nBoth plots saved to assets/.")
