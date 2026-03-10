#!/usr/bin/env python3
"""Run invariant convergence suite and generate CSV + plot."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gibbs_invariant.experiments import plot_invariant_convergence, run_invariant_convergence


if __name__ == "__main__":
    csv_path = run_invariant_convergence(output_dir="results")
    png_path = plot_invariant_convergence(invariant_csv=str(csv_path), output_path="results/invariant_convergence.png")
    print(f"Wrote {csv_path}")
    print(f"Wrote {png_path}")
