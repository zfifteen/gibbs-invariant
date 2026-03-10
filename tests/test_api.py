import unittest

import numpy as np

from gibbs_invariant import GibbsConfig, detect_gibbs, risk
from gibbs_invariant.fixtures import square_wave_fixture


class ApiTest(unittest.TestCase):
    def test_detect_gibbs_report_shape(self) -> None:
        signal = square_wave_fixture(2048)
        cfg = GibbsConfig(n_values=(16, 32, 64), noise_policy="robust")
        report = detect_gibbs(signal, config=cfg)

        self.assertIsInstance(report.overshoot_ratio, float)
        self.assertIsInstance(report.energy_redistribution, float)
        self.assertIsInstance(report.invariant_residual, float)
        self.assertIsInstance(report.jump_score, float)
        self.assertIsInstance(report.jump_active, bool)
        self.assertGreaterEqual(report.energy_redistribution, 0.0)
        self.assertLessEqual(report.energy_redistribution, 1.0)

    def test_risk_api(self) -> None:
        signal = square_wave_fixture(2048)
        coeff = np.abs(np.fft.rfft(signal))[1:]
        cfg = GibbsConfig(jump_threshold=0.2)
        result = risk(coeff, config=cfg)
        self.assertIsInstance(result.jump_active, bool)
        self.assertIsInstance(result.jump_score, float)
        self.assertGreaterEqual(result.threshold_used, 0.0)


if __name__ == "__main__":
    unittest.main()
