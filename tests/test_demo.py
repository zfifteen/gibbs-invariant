import json
import shutil
import tempfile
import unittest
from pathlib import Path

import numpy as np

from demo.engine import (
    analyze_signal,
    compute_policy_timeline_hash,
    generate_signal,
    load_artifacts,
    load_scenarios,
    run_counterfactual,
    scenario_to_config,
)
from gibbs_invariant.metrics import uniform_grid


class DemoEngineTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parents[1]
        cls.scenarios = load_scenarios(cls.root / "demo/scenarios")

    def test_analyze_signal_square_wave_detects_jump(self) -> None:
        scenario = self.scenarios["step_function"]
        signal = generate_signal(scenario, t=0.0)
        frame = analyze_signal(signal, config=scenario_to_config(scenario))
        self.assertGreater(frame.jump_score, 0.20)
        self.assertGreaterEqual(frame.energy_redistribution, 0.20)
        self.assertLessEqual(frame.energy_redistribution, 1.0)

    def test_analyze_signal_smooth_rejection(self) -> None:
        x = uniform_grid(2048)
        smooth = np.sin(3.0 * x) + 0.25 * np.sin(8.0 * x + 0.4)
        cfg = {"n_values": (16, 32, 64), "jump_threshold": 0.20, "alpha": 1.0, "noise_policy": "robust"}
        frame = analyze_signal(smooth, config=cfg)
        self.assertFalse(frame.jump_active)

    def test_deterministic_replay_hash(self) -> None:
        scenario = self.scenarios["noisy_discontinuity"]
        hash_1 = compute_policy_timeline_hash(scenario, steps=12, duration_s=7.0)
        hash_2 = compute_policy_timeline_hash(scenario, steps=12, duration_s=7.0)
        self.assertEqual(hash_1, hash_2)

    def test_load_artifacts_golden_shape(self) -> None:
        snapshot = load_artifacts(str(self.root / "results"))
        self.assertIn("phase2", snapshot.pipeline_summary)
        self.assertIn("phase3", snapshot.pipeline_summary)
        self.assertIn("phase4", snapshot.pipeline_summary)
        self.assertIsInstance(snapshot.pipeline_summary["phase2"]["phase2b_gates"]["all_pass"], bool)
        drift = snapshot.pipeline_summary["phase2"]["phase2b_gates"]["noise_robustness"]["mean_score_drift"]
        self.assertGreaterEqual(float(drift), 0.0)
        self.assertLess(float(drift), 2.0)

    def test_load_artifacts_fails_on_malformed_pipeline(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            for name in (
                "pipeline_summary.json",
                "gates_report.json",
                "constrained_metrics.json",
                "candidate_rankings.csv",
            ):
                shutil.copy(self.root / "results" / name, tmp_path / name)

            bad = json.loads((tmp_path / "pipeline_summary.json").read_text(encoding="utf-8"))
            bad.pop("phase4", None)
            (tmp_path / "pipeline_summary.json").write_text(json.dumps(bad), encoding="utf-8")

            with self.assertRaises(ValueError):
                load_artifacts(str(tmp_path))

    def test_counterfactual_has_win_and_non_win(self) -> None:
        scenario_ids = ["noisy_discontinuity", "nonuniform_sampling", "bandlimited_edge", "step_function"]
        has_win = False
        has_non_win = False

        for scenario_id in scenario_ids:
            scenario = self.scenarios[scenario_id]
            signal = generate_signal(scenario, t=1.5)
            counter = run_counterfactual(
                signal,
                policy={"alpha": scenario["alpha"], "cost_model": scenario["cost_model"]},
            )
            if counter.quality_gain > 0.0 and counter.speed_gain > 0.0:
                has_win = True
            else:
                has_non_win = True

        self.assertTrue(has_win)
        self.assertTrue(has_non_win)


if __name__ == "__main__":
    unittest.main()
