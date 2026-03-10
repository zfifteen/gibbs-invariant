#!/usr/bin/env python3
"""Run spectral curvature map suite."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gibbs_invariant.experiments import run_spectral_curvature_tests


if __name__ == "__main__":
    path = run_spectral_curvature_tests(output_dir="results")
    print(f"Wrote {path}")
