#!/usr/bin/env python3
"""Run phase2 artifacts, phase2b gates, phase3 constrained prototype, and ranking."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gibbs_invariant.constrained import run_constraint_prototype
from gibbs_invariant.experiments import run_all_phase2_artifacts
from gibbs_invariant.ranking import rank_candidates


if __name__ == "__main__":
    results_dir = ROOT / "results"
    candidate_file = ROOT / "docs/industry/github_candidate_software_list.md"
    gate_report = results_dir / "gates_report.json"
    constrained_report = results_dir / "constrained_metrics.json"

    phase2_summary = run_all_phase2_artifacts(output_dir=str(results_dir))
    constrained_summary = run_constraint_prototype(output_dir=str(results_dir))
    ranking = rank_candidates(
        candidate_file=str(candidate_file),
        output_dir=str(results_dir),
        gate_report_path=str(gate_report),
        constrained_report_path=str(constrained_report),
    )

    final = {
        "phase2": phase2_summary,
        "phase3": constrained_summary,
        "phase4": ranking,
    }

    output_path = results_dir / "pipeline_summary.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(final, handle, indent=2)

    print(f"Wrote {output_path}")
