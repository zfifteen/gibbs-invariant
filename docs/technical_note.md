# Two Computable Invariants for Fourier Approximation of Piecewise-Smooth Signals

**Author:** Big D

---

## Abstract

This note presents two linked, falsifiable invariants for Fourier partial sums of piecewise-smooth periodic signals. The **energy concentration invariant** (Theorem 1) shows that a stable fraction \(C(\alpha)\) of total \(L^2\) reconstruction error concentrates in shrinking neighborhoods of jump discontinuities; for the unit square wave at zone-width factor \(\alpha=1\), \(C(1)\approx 0.89\). The **radius budget invariant** (Theorem 2) shows that the cumulative Fourier coefficient magnitude grows logarithmically, with per-doubling increment \(\Delta R \to (2/\pi)\ln 2 \approx 0.4413\).

Together the two invariants yield a crossover criterion: for the unit square wave, pointwise Gibbs error exceeds global RMS error at \(N_1 \approx 26\). They also provide an operational decision rule: persistent \(\Delta R > 0.2\) past \(N\approx 50\) indicates true jump discontinuities. Both invariants are verified numerically for \(N=10\) through \(N=2{,}000\) with explicit falsification criteria. Single-command regeneration via `python3 gibbs_invariant.py` reproduces all figures and verification tables.

---

## 1. Introduction

The Gibbs phenomenon — the persistent overshoot of Fourier partial sums near jump discontinuities — is conventionally treated as a limitation of spectral methods. This note reframes it as a **computable diagnostic**: two invariant quantities that together determine *when* jump structure is active in a signal and *where* residual error concentrates.

The phenomenon was first observed by Wilbraham (1848) and independently by Gibbs (1899); the modern formalization is due to Hewitt and Hewitt (1979). Reconstruction methods that mitigate the effect include the Gegenbauer approach of Gottlieb and Shu (1997) and the mollifier framework of Tadmor (2007). These methods address the *consequences* of jump-induced spectral error; the present work addresses its *detection and quantification*.

What is new here is the identification of two linked, falsifiable invariants that operate at different levels of the approximation pipeline:

1. **Theorem 1 (Energy Concentration):** A stable, computable fraction of total \(L^2\) error is trapped in shrinking zones around discontinuities, independent of truncation order \(N\).
2. **Theorem 2 (Radius Budget):** The cumulative Fourier coefficient magnitude diverges logarithmically for jump signals, with a closed-form per-doubling constant.

Together they provide a two-stage diagnostic: Theorem 2 detects the presence of jumps; Theorem 1 quantifies the resulting error allocation. This note treats the canonical piecewise-smooth case: the unit square wave as the primary example, with sawtooth (discontinuous control) and triangle wave (continuous control) for validation.

---

## 2. Setup and Notation

Let \(f\) be a \(2\pi\)-periodic, piecewise \(C^1\) function (bounded variation is sufficient) with finitely many jump locations \(J=\{x_j\}\subset[-\pi,\pi)\).

**Fourier partial sum.** Let \(\{a_k\}_{k\ge 0}\) and \(\{b_k\}_{k\ge 1}\) denote the real Fourier coefficients of \(f\). For an effective bandwidth \(K(N)\) (defined below), the truncated Fourier approximation is
\[
S_N f(x) \;=\; \frac{a_0}{2} \;+\; \sum_{k=1}^{K(N)} \bigl(a_k \cos(kx) + b_k \sin(kx)\bigr),
\]
with residual \(e_N(x) = S_N f(x) - f(x)\).

**Truncation conventions.** Two conventions are used:
- **Odd-harmonic truncation** (square wave): effective bandwidth \(K(N)=2N+1\). For the canonical square wave, only the odd-indexed coefficients \(a_{2m+1},b_{2m+1}\) with \(1 \le 2m+1 \le K(N)\) are nonzero, so the sum for \(S_N f\) above effectively reduces to the first \(N\) odd harmonics.
- **Full-harmonic truncation** (sawtooth): effective bandwidth \(K(N)=N\), retaining all harmonics \(k=1,\dots,N\) in the sum for \(S_N f\).

**Jump-zone definition.** For zone-width factor \(\alpha>0\), define the Gibbs zone
\[
\Omega_N(\alpha) = \bigcup_{x_j\in J}\bigl\{x : |x-x_j|_{\mathbb{T}} \le \alpha\pi/K(N)\bigr\},
\]
where \(|\cdot|_{\mathbb{T}}\) denotes wrapped distance on the \(2\pi\)-torus. For \(x,x_j\in[-\pi,\pi)\), this is \(|x-x_j|_{\mathbb{T}} = \min(|x-x_j|,\, 2\pi - |x-x_j|)\).

**Cumulative radius budget.** Define
\[
R(N) = \sum_{k=1}^{N} |c_k|,
\]
where \(c_k\) are the Fourier coefficient magnitudes in the chosen truncation convention.

---

## 3. Theorem 1: Energy Concentration Invariant

### Statement

For fixed \(\alpha>0\), define the concentration fraction
\[
F_N(\alpha) = \frac{\int_{\Omega_N(\alpha)} |e_N(x)|^2\,dx}{\int_{-\pi}^{\pi} |e_N(x)|^2\,dx} = \frac{E_{\text{zone}}}{E_{\text{total}}}.
\]
Then \(F_N(\alpha)\to C(\alpha)\in(0,1)\) as \(N\to\infty\). The limit depends on \(\alpha\) and the truncation convention, but is stable in \(N\).

### Mechanism

Near each jump \(x_j\), the truncation error follows a universal scaled Gibbs profile: in the local variable \(u=K(N)(x-x_j)\), the error density scales as \(O(N)\) because the missing harmonics align coherently. The zone width shrinks as \(O(1/N)\), so the integrated zone energy scales as
\[
E_{\text{zone}}(N,\alpha) \sim \frac{C_{\text{zone}}(\alpha)}{K(N)}.
\]
Away from jumps, phases decorrelate and the smooth-region error density is much lower. The total error energy also scales as \(E_{\text{total}}(N)\sim C_{\text{total}}/K(N)\) (from Parseval's theorem and coefficient asymptotics). Since both numerator and denominator share the same \(1/K(N)\) scale, their ratio converges.

### Canonical values

For the unit square wave (\(\pm 1\) plateau, jump height 2) with odd-harmonic truncation:

| \(\alpha\) | \(C(\alpha)\) (approximate) |
|---|---|
| 0.5 | 0.860 |
| 1.0 | 0.895 |
| 2.0 | 0.948 |

These values are stable across \(N=64\) through \(N=1{,}024\) in the zone-width robustness sweep.

### Crossover \(N_1\)

Define \(N_1\) as the first \(N\) where the pointwise Gibbs error as a fraction of jump height exceeds the global RMS error of the \(N\)-term truncation. Under plateau normalization \(\pm 1\):
\[
N_1 \approx 26.
\]
Below \(N_1\), global spectral refinement efficiently reduces total error. Above \(N_1\), the jump-zone error dominates and targeted treatment becomes advantageous.

### Falsification criterion

For a sharp square wave at fixed \(\alpha\), if \(F_N(\alpha)\) decays monotonically toward zero rather than stabilizing near \(C(\alpha)\), the claim is falsified.

---

## 4. Theorem 2: Radius Budget Invariant

### Statement

If \(f\) has at least one jump discontinuity, then \(|c_k|\sim A/k\) for large \(k\), giving
\[
R(N) = A\ln N + O(1),
\]
and therefore the doubling increment converges:
\[
\Delta_N := R(2N) - R(N) \to A\ln 2.
\]

### Square-wave normalization

For the unit square wave with odd-harmonic truncation, radii are \(r_m = 4/(\pi(2m-1))\) for \(m=1,\dots,N\). Then
\[
R(N) \sim \frac{2}{\pi}\ln N + C, \qquad \Delta R \to \frac{2}{\pi}\ln 2 \approx 0.4413.
\]

### Why the budget grows

A true jump enforces a \(1/k\) harmonic tail. Individual high-frequency magnitudes are small, but they are not \(\ell^1\)-summable: \(\sum 1/k\) diverges. The cumulative radius budget therefore grows logarithmically without bound. Partial-sum cancellations keep the waveform amplitude bounded away from jumps, but do not prevent the cumulative coefficient magnitude from growing.

### Smooth-signal contrast

For a triangle wave (corner singularity, no jumps), the coefficient decay is \(1/k^2\). The series \(\sum 1/k^2\) converges, so \(R(N)\) saturates and the doubling increment \(\Delta_N\to 0\). This provides a clear separation between jump-class and smooth-class behavior.

### Additional discontinuous control

The periodic sawtooth wave has full-harmonic \(1/k\) coefficients and exhibits the same qualitative behavior: logarithmic budget growth and persistent nonzero doubling increment. This confirms the invariant is tied to the jump-regularity class, not to one specific waveform.

### Falsification criterion

For a sharp jump signal, if \(R(2N)-R(N)\) decays toward zero rather than settling near a nonzero constant, the claim is falsified.

---

## 5. Decision Rules

### Regime detection (Theorem 2)

Compute rolling doubling increments \(\Delta_N\). If the normalized score (recent average divided by plateau level) remains above a threshold of approximately 0.2 past moderate \(N\) (around 50), classify the signal as **jump-active**. If increments collapse toward zero, classify as **continuous/corner-only**.

### Error allocation (Theorem 1)

Once jumps are confirmed, the energy concentration fraction \(F_N(\alpha)\to C(\alpha)\) quantifies the fraction of residual \(L^2\) energy trapped in shrinking neighborhoods around discontinuities. This justifies a **two-budget split**: one error budget for smooth regions (where spectral convergence is efficient) and one for edge regions (where targeted methods are needed).

### Crossover guard

Below \(N_1\), global spectral refinement remains efficient across the entire domain. Above \(N_1\) with a jump-active classification, taper global refinement and route computational resources locally toward discontinuity neighborhoods.

### Waste quantification

At \(N=256\), the Gibbs zone with \(\alpha=1\) covers approximately \(p_N\approx 0.39\%\) of the domain while \(F_N(1)\approx 0.89\). Thus roughly 89% of the \(L^2\) error mass sits in under 1% of the domain area — quantifying the inefficiency of uniform global refinement for jump-bearing signals.

---

## 6. Numerical Verification

### Environment

- Python 3.9+, NumPy, Matplotlib
- Single-command regeneration: `python3 gibbs_invariant.py`
- All plots are saved to `assets/`

### Theorem 1 verification

**Overshoot convergence (left panel of energy invariant plot):**
The pointwise Gibbs overshoot as a fraction of jump height converges to the Wilbraham–Gibbs limit:
\[
\frac{\text{overshoot} - 1}{2} \to 0.08949\ldots
\]
across \(N=10\) to \(N=2{,}000\).

**Energy concentration (right panel):**
\(F_N(1)\) stabilizes near 0.89 across the same range.

**Zone-width robustness sweep:**
For \(\alpha\in\{0.5, 1.0, 2.0\}\), the concentration fraction is stable within each \(\alpha\) band across \(N=64\) through \(N=1{,}024\):

| \(\alpha\) | Mean \(F_N(\alpha)\) | Min | Max |
|---|---|---|---|
| 0.5 | ~0.86 | ~0.85 | ~0.87 |
| 1.0 | ~0.895 | ~0.88 | ~0.91 |
| 2.0 | ~0.948 | ~0.94 | ~0.95 |

### Theorem 2 verification

**Square-wave radius budget:**
\(R(N)\) follows the theoretical curve \((2/\pi)\ln N + C\) with \(C = (2/\pi)(2\ln 2 + \gamma)\), where \(\gamma\) is the Euler–Mascheroni constant.

**Doubling increment:**
Converges to \((2/\pi)\ln 2 \approx 0.4413\) as \(N\) increases.

**Triangle-wave control:**
Budget converges to a finite limit; doubling increments decay to zero.

**Sawtooth control:**
Budget grows logarithmically; doubling increments persist at a nonzero level, confirming jump-class behavior.

### Crossover estimation

\(N_1 = 26\) for the unit square wave under plateau normalization \(\pm 1\). Sensitivity to normalization: different amplitude conventions shift \(N_1\) but the qualitative crossover persists.

### Expected console output

Running `python3 gibbs_invariant.py` produces (among other output):

```
Theorem 2 delta-per-doubling target: 0.441271200305
Theorem 1 overshoot target (plateau=1): 1.178979744472
Theorem 1 pointwise error as jump fraction: 0.089489872236
Estimated crossover N where pointwise Gibbs error > global RMS error: 26
```

Along with verification tables for the square wave, sawtooth, and zone-width robustness sweep. Exact digit-level values may vary slightly by platform/BLAS implementation, but the constants and crossover should remain stable.

---

## 7. Open Problems

Generalization of \(N_1\) to the full piecewise-smooth function class (beyond square-wave normalization) remains open. Extension to two dimensions, where edge curves replace point discontinuities, would connect these invariants to image-processing applications. Noise robustness analysis — determining how additive noise modifies the detection thresholds of Theorem 2 and the concentration levels of Theorem 1 — is needed for practical deployment. Finally, a non-uniform sampling analog would extend the framework beyond the classical equispaced Fourier setting.

---

## Appendix A: Asymptotic Derivation of \(\Delta R\)

For the unit square wave with odd-harmonic truncation, the radii are
\[
r_m = \frac{4}{\pi(2m-1)}, \qquad m=1,2,\dots
\]
The cumulative budget through the first \(N\) odd harmonics is
\[
R(N) = \sum_{m=1}^{N} \frac{4}{\pi(2m-1)} = \frac{4}{\pi}\sum_{m=1}^{N}\frac{1}{2m-1}.
\]
Using the identity for partial sums of the odd reciprocal series,
\[
\sum_{m=1}^{N}\frac{1}{2m-1} = H_{2N} - \frac{1}{2}H_N,
\]
where \(H_n=\sum_{k=1}^n 1/k\) is the harmonic number, and the asymptotic expansion \(H_n=\ln n + \gamma + O(1/n)\), we obtain
\[
R(N) = \frac{4}{\pi}\left(\ln(2N)+\gamma - \frac{1}{2}\ln N - \frac{\gamma}{2} + O(1/N)\right) = \frac{2}{\pi}\ln N + \frac{2}{\pi}(2\ln 2+\gamma) + O(1/N).
\]
The doubling increment is then
\[
R(2N)-R(N) = \frac{2}{\pi}\ln(2N) - \frac{2}{\pi}\ln N + O(1/N) = \frac{2}{\pi}\ln 2 + O(1/N),
\]
converging to the exact constant \((2/\pi)\ln 2 \approx 0.4412712\).

---

## Appendix B: Proof Sketch for Energy Concentration Stability

The proof proceeds in three steps.

**Step 1: Global tail energy scales as \(1/K(N)\).**
For BV functions with jumps, the standard Fourier coefficient asymptotics give \(\hat{f}(k) = \sum_j \Delta_j e^{-ikx_j}/(2\pi ik) + O(1/k^2)\). By Parseval's theorem,
\[
E_{\text{total}}(N) = \sum_{|k|\ge K(N)} |\hat{f}(k)|^2 \sim \frac{C_{\text{total}}}{K(N)}.
\]

**Step 2: Zone energy shares the same scale.**
Using the Dirichlet kernel representation and the universal Gibbs scaling profile \(g(u)\) with \(u=K(N)(x-x_j)\), a change of variables gives
\[
E_{\text{zone}}(N,\alpha) = \sum_j \int_{|u|\le\alpha\pi} \Delta_j^2 g(u)^2\,\frac{du}{K(N)} + \text{lower order} = \frac{C_{\text{zone}}(\alpha)}{K(N)} + o\!\left(\frac{1}{K(N)}\right),
\]
with \(C_{\text{zone}}(\alpha) = \sum_j \Delta_j^2 \int_{-\alpha\pi}^{\alpha\pi} g(u)^2\,du\).

**Step 3: Ratio convergence.**
Since
\[
F_N(\alpha) = \frac{E_{\text{zone}}(N,\alpha)}{E_{\text{total}}(N)} = \frac{C_{\text{zone}}(\alpha)/K(N) + o(1/K(N))}{C_{\text{total}}/K(N) + o(1/K(N))} \to \frac{C_{\text{zone}}(\alpha)}{C_{\text{total}}} = C(\alpha)\in(0,1),
\]
the concentration fraction converges. The limit depends on \(\alpha\) and the truncation convention (through the profile \(g\)) but not on \(N\). Mixed jump terms carry oscillatory phase factors that average out at leading order, leaving the diagonal \(\sum_j \Delta_j^2\) structure in both numerator and denominator.

---

## Appendix C: Source Listing and Verification Table

### Key functions in `gibbs_invariant.py`

| Function | Description |
|---|---|
| `energy_concentration_fraction_for_signal(...)` | Generic energy concentration fraction for any signal with specified jump locations, zone width, and truncation mode |
| `cumulative_radius_budget(...)` | Cumulative sum of Fourier coefficient magnitudes |
| `radius_doubling_deltas(...)` | List of \(R(2n)-R(n)\) increments from small to large \(n\) |
| `has_true_jumps(...)` | Jump detection decision rule: returns boolean and normalized score |
| `estimate_crossover_harmonic(...)` | Finds first \(N\) where pointwise Gibbs error exceeds global RMS error |

### Verification targets

| Quantity | Target | Tolerance |
|---|---|---|
| Theorem 2 \(\Delta R\) (per-doubling) | 0.441271200305 | \(\pm 2\times 10^{-3}\) |
| Theorem 1 overshoot (plateau=1) | 1.178979744472 | \(\pm 2\times 10^{-3}\) |
| Theorem 1 error/jump fraction | 0.089489872236 | \(\pm 2\times 10^{-3}\) |
| Crossover \(N_1\) (square wave) | 26 | exact |
| \(F_N(1)\) at \(N=200\) | \(\in [0.86, 0.93]\) | band check |

### Full verification table (representative values)

The `verify_invariants()` function prints a table for \(N\in\{10, 25, 50, 100, 200, 500, 1000, 2000\}\) with columns:

- **Budget**: cumulative radius \(R(N)\)
- **Δ/double**: average doubling increment
- **Overshoot**: maximum partial-sum value near jump
- **Err/jump**: overshoot as fraction of jump height
- **E-zone**: energy concentration fraction \(F_N(1)\)
- **Jumps?**: detection result and score

Additional tables cover the sawtooth control signal and zone-width robustness across \(\alpha\in\{0.5, 1.0, 2.0\}\).

Platform-level variability (BLAS implementation, floating-point rounding) may shift the last displayed digit of table entries but should not affect the constants, crossover value, or qualitative convergence behavior.
