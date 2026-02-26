# The Gibbs Invariant: Theorem 1 (Energy Concentration Invariant)

## Formal statement

Let \(f\) be \(2\pi\)-periodic and piecewise \(C^1\) (equivalently bounded variation is sufficient), with a finite jump set \(J \subset [-\pi,\pi)\). Let \(S_N f\) denote the Fourier truncation used in code:

- For square-wave mode: odd-harmonic truncation with \(N\) odd harmonics.
- Error metric: \(e_N(x)=S_N f(x)-f(x)\), with global energy \(\|e_N\|_{L^2}^2\).
- Gibbs zones: for each \(x_j \in J\), zone half-width
  \[
  w_N(\alpha)=\alpha \frac{\pi}{K(N)}, \quad
  K(N)=\begin{cases}
  2N+1 & \text{odd-only truncation}\\
  N & \text{full-harmonic truncation}
  \end{cases}
  \]
  where \(\alpha>0\) is `zone_width_factor`.

Define
\[
F_N(\alpha)=\frac{\int_{\cup_j\{|x-x_j|\le w_N(\alpha)\}} |e_N(x)|^2\,dx}
{\int_{-\pi}^{\pi}|e_N(x)|^2\,dx}.
\]
Then \(F_N(\alpha)\to C(\alpha)\in(0,1)\) as \(N\to\infty\), where \(C\) depends on \(\alpha\) (zone-width choice) but not on \(N\).

## Proof bridge

A minimal derivation of the convergence claim is provided in
[`docs/theorem_1_proof_sketch.md`](theorem_1_proof_sketch.md),
showing both \(E_{\text{zone}}(N,\alpha)\) and \(E_{\text{tot}}(N)\) scale as \(1/K(N)\), so their ratio converges to \(C(\alpha)\).

## Practical interpretation

The Gibbs phenomenon is therefore not only a local overshoot effect; it is an error-allocation law. As \(N\) grows, edge zones shrink (\(\sim 1/N\)) while error density inside them rises, producing an \(N\)-stable fraction of total residual \(L^2\) error.

For the unit square wave with \(\alpha=1\), numerical values in this repo stabilize near \(C(1)\approx 0.89\).

## Crossover convention

`estimate_crossover_harmonic(...)` defines \(N_1\) as the first \(N\) such that:

- pointwise Gibbs error fraction of jump height exceeds
- global RMS error of the \(N\)-term truncation.

With the current normalization (plateau \(=\pm1\), jump height \(=2\)), this gives \(N_1 \approx 26\) for the square wave.

## Robustness checks in code

- Zone-width dependence is explicit via `zone_width_factor` (\(\alpha\)); the limiting constant is \(C(\alpha)\), not a universal 0.89 for all \(\alpha\).
- Additional discontinuous example included: periodic sawtooth (`sawtooth_*` functions). This verifies the same qualitative concentration law on a non-square jump signal.
