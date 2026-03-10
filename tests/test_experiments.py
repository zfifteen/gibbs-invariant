import json
import tempfile
import unittest
from pathlib import Path

from gibbs_invariant.experiments import (
    plot_invariant_convergence,
    run_baseline_comparison_gate,
    run_falsification_gates,
    run_invariant_convergence,
    run_overshoot_prediction,
    run_spectral_curvature_tests,
)


class ExperimentsTest(unittest.TestCase):
    def test_artifact_generation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = run_invariant_convergence(output_dir=tmp, n_values=(10, 25, 50))
            json_path = run_overshoot_prediction(output_dir=tmp, n_values=(16, 32, 64))
            npy_path = run_spectral_curvature_tests(output_dir=tmp, n_values=(8, 16))
            png_path = plot_invariant_convergence(invariant_csv=str(csv_path), output_path=f"{tmp}/plot.png")

            self.assertTrue(Path(csv_path).exists())
            self.assertTrue(Path(json_path).exists())
            self.assertTrue(Path(npy_path).exists())
            self.assertTrue(Path(png_path).exists())

    def test_gate_reports(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            gates = run_falsification_gates(output_dir=tmp, baseline_sample_count=60, baseline_num_samples=512)
            self.assertIn("all_pass", gates)
            self.assertIn("noise_robustness", gates)
            self.assertIn("nonuniform_sampling", gates)
            self.assertIn("baseline_comparison", gates)

            report_path = Path(tmp) / "gates_report.json"
            self.assertTrue(report_path.exists())
            report = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertIn("all_pass", report)

    def test_baseline_has_non_win_cases_field(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report = run_baseline_comparison_gate(output_dir=tmp, sample_count=60, num_samples=512)
            self.assertIn("non_win_cases", report)


if __name__ == "__main__":
    unittest.main()
