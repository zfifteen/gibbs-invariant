"""Render a wrap-around seam animation for periodic FFT intuition.

This script visualizes how a signal strip is interpreted when the FFT treats it
as a periodic loop and glues the right edge back to the left edge.
"""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
import sys
from typing import Dict, List

import imageio.v2 as imageio
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from gibbs_invariant.fixtures import bandlimited_edge_fixture
from gibbs_invariant.metrics import uniform_grid


FPS = 8
FLAT_HOLD_FRAMES = 8
WRAP_FRAMES = 28
FINAL_HOLD_FRAMES = 14
FIGSIZE = (13.5, 7.8)
BASE_RADIUS = 0.88
RADIAL_SCALE = 0.22
LINE_Y_SCALE = 0.48
SEAM_ANGLE = np.pi / 2.0


def _ease_in_out(t: float) -> float:
    return 3.0 * t * t - 2.0 * t * t * t


def _build_signals(num_samples: int = 1024) -> List[Dict[str, object]]:
    x = uniform_grid(num_samples)
    current = bandlimited_edge_fixture(num_samples)
    closure_matched = np.tanh(8.0 * np.sin(x)) + 0.10 * np.sin(9.0 * x)

    return [
        {
            "title": 'Current "Bandlimited Edge"',
            "caption": "Looks smooth in the window, but its ends do not meet when wrapped.",
            "signal": current,
            "color": "#c43c39",
        },
        {
            "title": "Closure-Matched Smooth Control",
            "caption": "The ends line up, so wrapping does not create a jump at the join.",
            "signal": closure_matched,
            "color": "#228b5a",
        },
    ]


def _interpolated_curve(signal: np.ndarray, progress: float) -> tuple[np.ndarray, np.ndarray]:
    n = signal.size
    max_abs = max(float(np.max(np.abs(signal))), 1e-12)
    scaled = signal / max_abs

    x_line = np.linspace(-1.35, 1.35, n)
    y_line = LINE_Y_SCALE * scaled

    theta = SEAM_ANGLE + np.linspace(0.0, 2.0 * np.pi, n, endpoint=False)
    radius = BASE_RADIUS + RADIAL_SCALE * scaled
    x_loop = radius * np.cos(theta)
    y_loop = radius * np.sin(theta)

    x_interp = (1.0 - progress) * x_line + progress * x_loop
    y_interp = (1.0 - progress) * y_line + progress * y_loop
    return x_interp, y_interp


def _draw_panel(ax: plt.Axes, item: Dict[str, object], progress: float) -> None:
    signal = np.asarray(item["signal"], dtype=float)
    color = str(item["color"])
    title = str(item["title"])
    caption = str(item["caption"])
    amp = float(signal.max() - signal.min())
    join_gap = float(abs(signal[0] - signal[-1]))
    closure_ratio = join_gap / amp if amp > 1e-12 else 0.0

    x_curve, y_curve = _interpolated_curve(signal, progress)

    ax.plot(x_curve, y_curve, color=color, lw=3.0)

    # Show the destination loop faintly so the bend-into-a-circle story is easy to track.
    theta_ring = np.linspace(0.0, 2.0 * np.pi, 361)
    ax.plot(BASE_RADIUS * np.cos(theta_ring), BASE_RADIUS * np.sin(theta_ring), color="#b9b9b9", lw=1.0, alpha=0.25)

    ax.scatter([x_curve[0], x_curve[-1]], [y_curve[0], y_curve[-1]], color=["#2563eb", "#7c3aed"], s=68, zorder=6)

    # The seam guide is the place where the FFT glues the ends together.
    seam_x = np.array([0.0, 0.0])
    seam_y = np.array([0.15, BASE_RADIUS + RADIAL_SCALE + 0.10])
    ax.plot(seam_x, seam_y, ls="--", lw=1.2, color="black", alpha=0.55)

    if progress >= 0.82:
        ax.plot([x_curve[0], x_curve[-1]], [y_curve[0], y_curve[-1]], color="black", lw=1.7, alpha=0.55)
        if closure_ratio > 0.1:
            ax.annotate(
                "seam appears here",
                xy=((x_curve[0] + x_curve[-1]) / 2.0, (y_curve[0] + y_curve[-1]) / 2.0),
                xytext=(0.56, 0.82),
                textcoords="axes fraction",
                fontsize=10,
                arrowprops=dict(arrowstyle="->", color="black", lw=1.1),
            )
        else:
            ax.annotate(
                "ends almost meet",
                xy=((x_curve[0] + x_curve[-1]) / 2.0, (y_curve[0] + y_curve[-1]) / 2.0),
                xytext=(0.56, 0.82),
                textcoords="axes fraction",
                fontsize=10,
                arrowprops=dict(arrowstyle="->", color="black", lw=1.1),
            )

    ax.text(
        0.03,
        0.95,
        title,
        transform=ax.transAxes,
        va="top",
        fontsize=13,
        fontweight="bold",
        color=color,
    )
    ax.text(
        0.03,
        0.86,
        caption,
        transform=ax.transAxes,
        va="top",
        fontsize=10,
        bbox=dict(boxstyle="round,pad=0.25", facecolor="white", alpha=0.9, edgecolor="none"),
    )
    ax.text(
        0.03,
        0.72,
        f"join gap / signal height = {closure_ratio:.3f}",
        transform=ax.transAxes,
        va="top",
        fontsize=10,
        bbox=dict(boxstyle="round,pad=0.25", facecolor="white", alpha=0.9, edgecolor="none"),
    )

    if progress <= 0.25:
        ax.annotate(
            "left edge",
            xy=(x_curve[0], y_curve[0]),
            xytext=(0.07, 0.18),
            textcoords="axes fraction",
            fontsize=10,
            color="#2563eb",
            arrowprops=dict(arrowstyle="->", color="#2563eb", lw=1.2),
        )
        ax.annotate(
            "right edge",
            xy=(x_curve[-1], y_curve[-1]),
            xytext=(0.72, 0.18),
            textcoords="axes fraction",
            fontsize=10,
            color="#7c3aed",
            arrowprops=dict(arrowstyle="->", color="#7c3aed", lw=1.2),
        )

    ax.set_xlim(-1.65, 1.65)
    ax.set_ylim(-1.45, 1.45)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)


def _make_frame(signals: List[Dict[str, object]], progress: float) -> np.ndarray:
    fig, axes = plt.subplots(1, 2, figsize=FIGSIZE, constrained_layout=True)
    fig.patch.set_facecolor("white")
    fig.suptitle("Think of the FFT as bending the signal into a loop and gluing the ends", fontsize=18, y=1.01)
    fig.text(
        0.5,
        0.95,
        "If the ends land at different heights, the join becomes a jump. If they land together, there is no seam.",
        ha="center",
        fontsize=11,
    )

    for ax, item in zip(axes, signals):
        _draw_panel(ax, item, progress)

    fig.text(0.5, 0.04, "blue dot = left edge    purple dot = right edge    dashed line = wrap-around join", ha="center", fontsize=10)

    buffer = BytesIO()
    fig.savefig(buffer, format="png", dpi=180, bbox_inches="tight")
    plt.close(fig)
    buffer.seek(0)
    return imageio.imread(buffer)


def render_animation(output_dir: str = "results") -> tuple[Path, Path]:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    gif_path = out_dir / "closure_wrap_animation.gif"
    mp4_path = out_dir / "closure_wrap_animation.mp4"

    signals = _build_signals()
    frames: List[np.ndarray] = []

    for _ in range(FLAT_HOLD_FRAMES):
        frames.append(_make_frame(signals, progress=0.0))

    for i in range(WRAP_FRAMES):
        t = i / max(WRAP_FRAMES - 1, 1)
        frames.append(_make_frame(signals, progress=_ease_in_out(float(t))))

    for _ in range(FINAL_HOLD_FRAMES):
        frames.append(_make_frame(signals, progress=1.0))

    imageio.mimsave(gif_path, frames, fps=FPS, loop=0)
    with imageio.get_writer(mp4_path, fps=FPS, codec="libx264", quality=8) as writer:
        for frame in frames:
            writer.append_data(frame)

    return gif_path, mp4_path


if __name__ == "__main__":
    gif_path, mp4_path = render_animation()
    print(gif_path.resolve())
    print(mp4_path.resolve())
