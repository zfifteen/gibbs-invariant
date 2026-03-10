"""Deterministic scenario replay for the Gibbs Regime Switcher demo."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from .engine import (
    compute_policy_timeline_hash,
    load_scenarios,
    simulate_policy_timeline,
)


def run_replay(
    scenario_id: str,
    scenarios_dir: str | None = None,
    steps: int = 16,
    duration_s: float = 8.0,
) -> Dict[str, Any]:
    base_dir = scenarios_dir or str(Path(__file__).resolve().parent / "scenarios")
    scenarios = load_scenarios(base_dir)
    if scenario_id not in scenarios:
        names = ", ".join(sorted(scenarios))
        raise ValueError(f"Unknown scenario '{scenario_id}'. Available: {names}")

    scenario = scenarios[scenario_id]
    timeline = simulate_policy_timeline(scenario=scenario, steps=steps, duration_s=duration_s)
    digest = compute_policy_timeline_hash(scenario=scenario, steps=steps, duration_s=duration_s)
    return {
        "scenario_id": scenario_id,
        "title": scenario["title"],
        "steps": int(steps),
        "duration_s": float(duration_s),
        "timeline_hash": digest,
        "timeline": timeline,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Replay a deterministic Gibbs demo scenario.")
    parser.add_argument("--scenario", required=True, help="Scenario id from demo/scenarios/*.json")
    parser.add_argument("--scenarios-dir", help="Directory with scenario JSON files")
    parser.add_argument("--steps", type=int, default=16, help="Number of timeline samples")
    parser.add_argument("--duration", type=float, default=8.0, help="Duration in seconds represented by replay")
    parser.add_argument("--output", help="Optional output JSON path for replay result")
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    result = run_replay(
        scenario_id=args.scenario,
        scenarios_dir=args.scenarios_dir,
        steps=args.steps,
        duration_s=args.duration,
    )

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"Wrote replay output to {out_path}")
    else:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
