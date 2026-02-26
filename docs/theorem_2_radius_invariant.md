# The Gibbs Invariant: Theorem 2 (Radius Budget Invariant)

## Formal statement

Let \(f\) be \(2\pi\)-periodic, piecewise \(C^1\) (BV suffices), with at least one jump discontinuity. Let \(c_k\) be Fourier coefficients and define the radius budget
\[
R(N)=\sum_{k=1}^{N} |c_k|.
\]
Under a jump, \(|c_k| \sim K/k\), hence
\[
R(N)=K\log N + O(1),
\]
so \(R(N)\) diverges logarithmically.

Equivalently, the doubling increment converges:
\[
\Delta_N := R(2N)-R(N)\to K\log 2.
\]

## Square-wave normalization used in code

Conventions in this repo:

- Plateau normalization: square wave levels are \(\pm 1\) (jump height \(2\)).
- Truncation: first \(N\) odd harmonics.
- Radii: \(r_m=\frac{4}{\pi(2m-1)}\), \(m=1,\dots,N\).

Then
\[
R(N)\sim \frac{2}{\pi}\log N + C,\qquad
R(2N)-R(N)\to \frac{2}{\pi}\log 2 \approx 0.4412712.
\]

## Contrasts and additional discontinuous example

- Continuous control (triangle-like, \(1/k^2\) tail): \(R(N)\) saturates and \(\Delta_N \to 0\).
- Additional discontinuous control (periodic sawtooth, full-harmonic \(1/k\) tail): \(R(N)\) again grows like \(\log N\), with persistent nonzero doubling increment.

This confirms the invariant is about jump-regularity class, not one specific waveform.

## Decision rule used operationally

When recent doubling increments stay above a plateau-scaled threshold (default `0.2`) beyond moderate \(N\), classify as true-jump behavior. When increments collapse toward zero, classify as continuous/corner-only behavior.
