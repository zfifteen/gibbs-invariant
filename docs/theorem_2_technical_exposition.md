# The Gibbs Invariant: Theorem 2 Technical Exposition

## Core Statement

Let \(f\) be \(2\pi\)-periodic and piecewise \(C^1\) (bounded variation is sufficient), and let \(c_k\) be its Fourier coefficients in complex or amplitude form. Define the radius budget
\[
R(N)=\sum_{k=1}^N |c_k|.
\]

If \(f\) has at least one jump discontinuity, then \(|c_k|\sim K/k\) for large \(k\), so
\[
R(N)=K\log N + O(1),
\]
and therefore
\[
R(2N)-R(N)\to K\log 2.
\]

This gives a global discontinuity diagnostic: persistent nonzero doubling increment indicates jump-class behavior.

## Square-Wave Normalization Used in This Repo

The implementation uses plateau levels \(\pm1\) (jump height \(2\)) and odd-harmonic truncation:
\[
r_m=\frac{4}{\pi(2m-1)},\qquad m=1,\dots,N.
\]
Hence
\[
R(N)\sim \frac{2}{\pi}\log N + C,\qquad
R(2N)-R(N)\to \frac{2}{\pi}\log 2\approx 0.4412712.
\]

These constants are encoded in `GIBBS_RADIUS_DELTA` and used by the verification routine.

## Why the Budget Grows

A true jump enforces a harmonic \(1/k\) tail. Individual high-frequency components are small, but their absolute magnitudes are not summable, so the \(\ell^1\) budget diverges logarithmically. Partial-sum cancellations keep waveform amplitude bounded away from jumps, but do not prevent cumulative coefficient magnitude from growing.

## Contrasts

- Continuous/corner-only signals (for example triangle-like \(1/k^2\) decay): \(R(N)\) converges; doubling increments decay to \(0\).
- Jump signals: \(R(N)\) keeps growing like \(\log N\); doubling increments stabilize at a nonzero level.

## Additional Discontinuous Example

Beyond the square wave, this repo now includes a periodic sawtooth example:

- `sawtooth_radii(N)` with full-harmonic \(1/k\) coefficients,
- persistent nonzero doubling increment under `radius_doubling_deltas(...)`.

This confirms the behavior is tied to jump regularity class, not to one specific waveform.

## Operational Decision Rule

`has_true_jumps(...)` computes a recent average of doubling increments and normalizes by plateau level. With default threshold `0.2`:

- score above threshold at moderate/large \(N\) -> classify as true-jump behavior,
- score collapsing toward \(0\) -> classify as continuous/corner-only behavior.

## Falsification Criteria

For a sharp jump signal, if \(R(2N)-R(N)\) decays toward \(0\) as \(N\) increases (instead of stabilizing near a nonzero level), the theorem claim fails for that setup.

For the square-wave normalization used here, failure to approach \(\frac{2}{\pi}\log 2\approx 0.4412712\) would falsify the stated asymptotic target.
