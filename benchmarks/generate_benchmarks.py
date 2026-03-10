#!/usr/bin/env python3
"""Generate deterministic benchmark signals for v1."""

from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gibbs_invariant.fixtures import (
    bandlimited_edge_fixture,
    noisy_discontinuity_fixture,
    square_wave_fixture,
    step_function_fixture,
)


def _write(path: Path, values: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    np.save(path, values)


if __name__ == "__main__":
    _write(Path("benchmarks/step_function/signal.npy"), step_function_fixture(2048))
    _write(Path("benchmarks/square_wave/signal.npy"), square_wave_fixture(2048))
    _write(Path("benchmarks/bandlimited_edge/signal.npy"), bandlimited_edge_fixture(2048))
    _write(Path("benchmarks/noisy_discontinuity/signal.npy"), noisy_discontinuity_fixture(2048, snr_db=15.0, seed=7))
    print("Generated benchmark fixtures under benchmarks/")
