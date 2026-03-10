import tempfile
import unittest
from pathlib import Path

from gibbs_invariant.constrained import invariant_constrained_loss, run_constraint_prototype


class ConstrainedTest(unittest.TestCase):
    def test_loss_formula(self) -> None:
        value = invariant_constrained_loss(
            reconstruction=[0.0, 1.0, 0.0],
            target=[0.0, 0.0, 0.0],
            invariant_residual=0.1,
            lambda_weight=2.0,
        )
        self.assertAlmostEqual(value, (1.0 / 3.0) + 2.0 * 0.01, places=8)

    def test_constraint_prototype_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report = run_constraint_prototype(output_dir=tmp, n_values=(8, 16, 24, 32))
            self.assertIn("pass", report)
            self.assertIn("tasks", report)
            self.assertIn("denoising", report["tasks"])
            self.assertIn("truncated_fourier_reconstruction", report["tasks"])
            self.assertIn("edge_preserving_smoothing", report["tasks"])
            self.assertTrue((Path(tmp) / "constrained_metrics.json").exists())


if __name__ == "__main__":
    unittest.main()
