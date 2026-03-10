"""Compatibility entrypoint for legacy script execution.

This file preserves `python3 gibbs_invariant.py` behavior while the importable
package lives in `gibbs_invariant/`.
"""

from __future__ import annotations

from typing import Optional

import matplotlib.pyplot as plt
import numpy as np

from gibbs_invariant.metrics import (
    ENERGY_ZONE_WIDTH_FACTOR,
    GIBBS_OVERSHOOT_FRACTION_JUMP,
    GIBBS_OVERSHOOT_LIMIT,
    GIBBS_RADIUS_DELTA,
    RADIUS_BUDGET_ASYMPTOTIC_CONSTANT,
    cumulative_radius_budget,
    energy_concentration_fraction,
    estimate_crossover_harmonic,
    gibbs_overshoot,
    has_true_jumps,
    radius_doubling_deltas,
    sawtooth_energy_concentration_fraction,
    sawtooth_radii,
    square_wave,
    square_wave_partial_sum,
    square_wave_radii,
)


DEFAULT_THRESHOLD = 0.20


def plot_radius_budget(
    dark_mode: bool = True,
    save_path: Optional[str] = "assets/radius_budget_verification.png",
) -> None:
    ns = np.logspace(1, 4.2, 120, dtype=int)
    budgets_sq = np.array([cumulative_radius_budget(square_wave_radii(int(n)))[-1] for n in ns])
    budgets_saw = np.array([cumulative_radius_budget(sawtooth_radii(int(n)))[-1] for n in ns])

    def triangle_radii_local(n: int) -> np.ndarray:
        k = np.arange(1, 2 * n, 2, dtype=float)
        return 8.0 / (np.pi**2 * k**2)

    budgets_tri = np.array([cumulative_radius_budget(triangle_radii_local(int(n)))[-1] for n in ns])
    theo = (2 / np.pi) * np.log(ns) + RADIUS_BUDGET_ASYMPTOTIC_CONSTANT

    plt.figure(figsize=(12, 7))
    if dark_mode:
        plt.style.use("dark_background")
        color_sq = "#00eeff"
        color_saw = "#66ff66"
        color_tri = "#ff44cc"
        color_theo = "#ffcc44"
    else:
        color_sq = "#0088ff"
        color_saw = "#009944"
        color_tri = "#cc0088"
        color_theo = "#ff8800"

    plt.plot(ns, budgets_sq, "o-", color=color_sq, lw=2.8, ms=3.5, label="Square Wave (True Jumps — Theorem 2)")
    plt.plot(ns, budgets_saw, "^-", color=color_saw, lw=2.2, ms=3.2, label="Sawtooth (True Jumps — 1/k tail)")
    plt.plot(ns, budgets_tri, "s-", color=color_tri, lw=2.2, ms=3.5, label="Triangle Wave (Continuous — saturates)")
    plt.plot(ns, theo, "--", color=color_theo, lw=2.4, label=f"Theoretical: (2/pi)ln(N) + {RADIUS_BUDGET_ASYMPTOTIC_CONSTANT:.3f}")

    plt.xscale("log")
    plt.xlabel("Number of Harmonics N (log scale)", fontsize=13)
    plt.ylabel("Cumulative Circle-Length Budget R(N)", fontsize=13)
    plt.title("Gibbs Radius Invariant (Theorem 2) — Persistent Growth", fontsize=15, pad=15)
    plt.legend(fontsize=11.5, loc="upper left")
    plt.grid(True, alpha=0.35)

    plt.annotate(
        "dR ~= 0.4413\nper doubling",
        xy=(400, 4.9),
        xytext=(1200, 3.8),
        arrowprops=dict(arrowstyle="->", color=color_theo, lw=1.8),
        fontsize=12,
        color=color_theo,
        ha="center",
    )

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=420, bbox_inches="tight", facecolor="black" if dark_mode else "white")
    plt.show()


def plot_energy_invariant(
    dark_mode: bool = True,
    save_path: Optional[str] = "assets/energy_invariant.png",
) -> None:
    ns = [10, 25, 50, 100, 200, 400, 800, 1200, 2000]
    overshoot_fraction_jump = []
    concentrations = []
    x = np.linspace(-np.pi, np.pi, 65536, endpoint=False)

    if dark_mode:
        plt.style.use("dark_background")

    for n in ns:
        ov = gibbs_overshoot(n)
        overshoot_fraction_jump.append((ov - 1.0) / 2.0)
        concentrations.append(energy_concentration_fraction(n, x, zone_width_factor=ENERGY_ZONE_WIDTH_FACTOR))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.8))
    if dark_mode:
        color_ov = "#ffdd44"
        color_ec = "#2de2e6"
        hline = "white"
    else:
        color_ov = "#ff8800"
        color_ec = "#0088ff"
        hline = "black"

    ax1.plot(ns, overshoot_fraction_jump, "o-", color=color_ov, lw=3, ms=7, label="Numerical pointwise error / jump height")
    ax1.axhline(y=GIBBS_OVERSHOOT_FRACTION_JUMP, color=hline, ls="--", alpha=0.7, label=f"Theoretical level {GIBBS_OVERSHOOT_FRACTION_JUMP:.6f}")
    ax1.set_xscale("log")
    ax1.set_xlabel("N (log scale)")
    ax1.set_ylabel("Pointwise error fraction of jump")
    ax1.set_title("Persistent Gibbs Overshoot")
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=10)

    ax2.plot(ns, concentrations, "o-", color=color_ec, lw=3, ms=7, label="L2 error fraction in Gibbs zones")
    ax2.axhline(y=0.89, color=hline, ls="--", alpha=0.7, label="Claimed invariant level ~0.89")
    ax2.set_xscale("log")
    ax2.set_ylim(0.0, 1.0)
    ax2.set_xlabel("N (log scale)")
    ax2.set_ylabel("Error concentration fraction")
    ax2.set_title("Energy Concentration Invariant")
    ax2.grid(True, alpha=0.3)
    ax2.legend(fontsize=10)

    fig.suptitle("Gibbs Energy Invariant (Theorem 1)", fontsize=14)
    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=420, bbox_inches="tight", facecolor="black" if dark_mode else "white")
    plt.show()


def verify_invariants() -> None:
    n_list = [10, 25, 50, 100, 200, 500, 1000, 2000]
    x = np.linspace(-np.pi, np.pi, 65536, endpoint=False)

    print("Gibbs Invariants Verification v2.5")
    print("=" * 110)
    print(f"{'N':>5} | {'Budget':>7} | {'d/double':>9} | {'Overshoot':>10} | {'Err/jump':>9} | {'E-zone':>7} | {'Jumps?':>7} (score)")
    print("-" * 110)

    for n in n_list:
        approx = square_wave_partial_sum(x, n)
        target = square_wave(x)
        _ = approx, target

        radii = square_wave_radii(n)
        cum_budget = cumulative_radius_budget(radii)[-1]
        deltas = radius_doubling_deltas(radii)
        avg_delta = float(np.mean(deltas)) if deltas else 0.0
        overshoot = gibbs_overshoot(n)
        jump_fraction = (overshoot - 1.0) / 2.0
        e_zone = energy_concentration_fraction(n, x)
        detects, score = has_true_jumps(radii, threshold=DEFAULT_THRESHOLD)

        print(
            f"{n:5d} | {cum_budget:7.3f} | {avg_delta:9.4f} | {overshoot:10.6f} | {jump_fraction:9.5f} | {e_zone:7.4f} | {detects!s:>7}  ({score})"
        )

    crossover = estimate_crossover_harmonic(max_N=120)
    print("-" * 110)
    print(f"Estimated crossover N where pointwise Gibbs error > global RMS error: {crossover}")
    print("Reference constants:")
    print(f"  Theorem 2 delta-per-doubling target: {GIBBS_RADIUS_DELTA:.12f}")
    print(f"  Theorem 1 overshoot target (plateau=1): {GIBBS_OVERSHOOT_LIMIT:.12f}")
    print(f"  Theorem 1 pointwise error as jump fraction: {GIBBS_OVERSHOOT_FRACTION_JUMP:.12f}")
    print()
    print("Additional discontinuous example (sawtooth):")
    print(f"{'N':>5} | {'R(N)':>7} | {'d/double':>9} | {'E-zone alpha=1':>14}")
    print("-" * 48)

    for n in [16, 32, 64, 128, 256, 512]:
        radii_sw = sawtooth_radii(n)
        deltas_sw = radius_doubling_deltas(radii_sw, min_n=8)
        avg_delta_sw = float(np.mean(deltas_sw[-3:])) if deltas_sw else 0.0
        e_zone_sw = sawtooth_energy_concentration_fraction(n, x, zone_width_factor=1.0)
        print(f"{n:5d} | {radii_sw.sum():7.3f} | {avg_delta_sw:9.4f} | {e_zone_sw:14.4f}")


if __name__ == "__main__":
    print("Gibbs Invariant Library v2.5 — Package Compatibility Build\n")
    verify_invariants()
    plot_radius_budget(dark_mode=True)
    plot_energy_invariant(dark_mode=True)
    print("\nBoth plots saved to assets/.")
