import importlib.util
import pathlib
import unittest

import numpy as np

from gibbs_invariant.metrics import gibbs_overshoot as pkg_gibbs_overshoot
from gibbs_invariant.metrics import square_wave_radii as pkg_square_wave_radii


class RegressionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        root = pathlib.Path(__file__).resolve().parents[1]
        legacy_path = root / "gibbs_invariant.py"
        spec = importlib.util.spec_from_file_location("legacy_gibbs_script", legacy_path)
        if spec is None or spec.loader is None:
            raise RuntimeError("Unable to load legacy compatibility script")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        cls.legacy = module

    def test_legacy_radii_match_package(self) -> None:
        legacy = self.legacy.square_wave_radii(64)
        packaged = pkg_square_wave_radii(64)
        np.testing.assert_allclose(legacy, packaged, rtol=1e-12, atol=1e-12)

    def test_legacy_overshoot_match_package(self) -> None:
        legacy = self.legacy.gibbs_overshoot(128)
        packaged = pkg_gibbs_overshoot(128)
        self.assertAlmostEqual(legacy, packaged, places=10)


if __name__ == "__main__":
    unittest.main()
