# The Gibbs Invariant: Theorem 1 Technical Exposition

## Core Statement

Let \(f\) be \(2\pi\)-periodic and piecewise \(C^1\) (bounded variation is sufficient), with finitely many jumps at locations \(J=\{x_j\}\).
For a Fourier truncation \(S_N f\), define the residual \(e_N(x)=S_N f(x)-f(x)\).

For a zone-width factor \(\alpha>0\), define jump zones
\[
\Omega_N(\alpha)=\bigcup_{x_j\in J}\{|x-x_j|_{\mathbb T}\le \alpha\pi/K(N)\},
\]
where \(|\cdot|_{\mathbb T}\) is wrapped distance on the \(2\pi\)-torus, and:

- \(K(N)=2N+1\) for odd-harmonic truncation (square-wave mode in this repo),
- \(K(N)=N\) for full-harmonic truncation.

Define concentration fraction
\[
F_N(\alpha)=\frac{\int_{\Omega_N(\alpha)}|e_N(x)|^2\,dx}{\int_{-\pi}^{\pi}|e_N(x)|^2\,dx}.
\]

The claim is that \(F_N(\alpha)\to C(\alpha)\in(0,1)\) as \(N\to\infty\): the fraction is asymptotically stable in \(N\) for fixed \(\alpha\), and the limit depends on \(\alpha\).

## Mechanism

Near each jump, missing high-frequency modes align coherently and produce \(O(1)\) local oscillation amplitude inside a band that shrinks like \(1/K(N)\). In smooth regions, phase cancellation dominates and residual energy density is much lower. This creates a stable partition of residual \(L^2\) energy between jump zones and smooth regions.

## Code-Level Definitions

In [`gibbs_invariant.py`](/Users/velocityworks/IdeaProjects/gibbs-invariant/gibbs_invariant.py):

- `energy_concentration_fraction(...)` is the square-wave specialization.
- `energy_concentration_fraction_for_signal(...)` is the generic implementation with explicit `jump_locations`, `zone_width_factor`, and truncation mode (`odd` vs `all` harmonics).
- Wrapped-distance masking is used, so boundary jumps at \(\pm\pi\) are handled correctly.

## Numerical Behavior in This Repo

Using the current implementation:

- Square wave, \(\alpha=1\): \(F_N(1)\) stabilizes near \(0.89\) for moderate/large \(N\).
- Square wave, varying \(\alpha\): the reported means are approximately
  - \(\alpha=0.5\): \(0.86\)
  - \(\alpha=1.0\): \(0.895\)
  - \(\alpha=2.0\): \(0.948\)
- Additional discontinuous example: periodic sawtooth also exhibits stable high jump-zone concentration for fixed \(\alpha\), consistent with jump-class behavior beyond the square wave.

## Crossover Convention \(N_1\)

`estimate_crossover_harmonic(...)` defines \(N_1\) as the first \(N\) where:

1. pointwise Gibbs error as a fraction of jump height
2. exceeds global RMS residual error

under plateau normalization \(\pm1\) (jump height \(2\)).
With this convention, the square-wave estimate is \(N_1\approx26\).

## Falsification Criteria

For a jump signal and fixed \(\alpha\), if \(F_N(\alpha)\) shows monotone decay toward \(0\) with increasing \(N\) (instead of stabilizing near a nonzero level), the theorem claim fails for that setup.

For square-wave normalization in this repo, if \(\alpha=1\) does not stabilize near its observed band around \(0.89\) over moderate-to-large \(N\), the current empirical claim is falsified.
