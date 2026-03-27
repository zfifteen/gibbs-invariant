import unittest

import numpy as np

from gibbs_invariant.fixtures import bandlimited_edge_fixture, step_function_fixture
from gibbs_invariant.metrics import (
    GIBBS_OVERSHOOT_FRACTION_JUMP,
    GIBBS_RADIUS_DELTA,
    energy_concentration_fraction,
    estimate_crossover_harmonic,
    periodic_closure_ratio,
    radius_doubling_deltas,
    square_wave_radii,
    uniform_grid,
)


class MetricsTest(unittest.TestCase):
    def test_constants_stable(self) -> None:
        self.assertAlmostEqual(GIBBS_RADIUS_DELTA, 0.4412712003053032, places=12)
        self.assertAlmostEqual(GIBBS_OVERSHOOT_FRACTION_JUMP, 0.08948987223608354, places=12)

    def test_radius_delta_trend(self) -> None:
        radii = square_wave_radii(4096)
        deltas = radius_doubling_deltas(radii, min_n=8)
        self.assertGreater(len(deltas), 5)
        recent = float(np.mean(deltas[-3:]))
        self.assertAlmostEqual(recent, GIBBS_RADIUS_DELTA, delta=0.03)

    def test_energy_concentration_stability(self) -> None:
        x = uniform_grid(32768)
        values = [energy_concentration_fraction(n, x) for n in (64, 128, 256)]
        self.assertGreater(np.mean(values), 0.80)
        self.assertLess(np.mean(values), 0.95)

    def test_crossover_reasonable(self) -> None:
        n1 = estimate_crossover_harmonic(max_N=120)
        self.assertIsNotNone(n1)
        assert n1 is not None
        self.assertGreaterEqual(n1, 20)
        self.assertLessEqual(n1, 40)

    def test_periodic_closure_ratio_distinguishes_step_from_periodic_control(self) -> None:
        self.assertGreater(periodic_closure_ratio(step_function_fixture(2048)), 0.90)
        self.assertLess(periodic_closure_ratio(bandlimited_edge_fixture(2048)), 0.05)


if __name__ == "__main__":
    unittest.main()
