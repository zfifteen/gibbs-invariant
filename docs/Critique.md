# Critique and Formal Validation Review (Post-Update)

This document is a formal critique and validation review of the repository’s two linked results:

- Theorem 1 — Gibbs Energy Invariant (energy concentration in shrinking zones)
- Theorem 2 — Gibbs Radius Invariant (logarithmic “circle-length budget” growth)

The intent is to:
1) validate what is implied by classical Fourier analysis,
2) identify what is theorem-grade as stated,
3) isolate definition-dependence or missing proof bridges,
4) separate empirical calibration from closed-form.

This critique is written against the repository state that formalizes theorem assumptions, generalizes the energy metric, adds a sawtooth discontinuous example, and states the energy fraction as C(alpha) rather than a universal number.

---

## 1. Executive summary

### Theorem 2 (Radius Invariant): validated (theorem-grade)
- The statement follows directly from standard Fourier coefficient asymptotics for jump discontinuities.
- For canonical examples (square wave) the closed-form constants are correct.
- For general piecewise-smooth / bounded-variation signals with jumps, the qualitative behavior (log divergence; nonzero per-doubling increment) is robust.

### Theorem 1 (Energy Invariant): substantially improved; now theorem-shaped
- The repository no longer treats "~0.89" as a universal constant; it correctly encodes zone dependence via C(alpha).
- The remaining gap (if you want analyst-proof) is a short proof bridge for the limit F_N(alpha) -> C(alpha) for the stated function class, beyond numerical stabilization.

---

## 2. Repository strengths (post-update)

1) Theorem 1 assumptions and conventions are explicit (function class, finite jump set, and alpha via K(N)).

2) The energy metric now generalizes to arbitrary signals via energy_concentration_fraction_for_signal(...).

3) Sawtooth example added as a second discontinuous control.

4) Alpha dependence is printed in verification output (robustness check).

---

## 3. Theorem 2 — radius budget invariant

### 3.1 Formal content
Define a cumulative budget from Fourier coefficients:

R(N) = sum_{k <= N} |c_k|

Claim:
- If f has a jump, R(N) ~ A log N.
- Therefore R(2N) - R(N) -> A log 2.

For the unit square wave normalization in this repo:
- A = 2/pi, so the doubling limit is (2/pi)*log(2) ~ 0.4412712003.

### 3.2 Square wave constant check
Odd sine coefficients:

b_{2m-1} = 4/(pi*(2m-1))

so the series behaves like the harmonic series and yields A = 2/pi. No new math is needed.

### 3.3 General validity
Piecewise C1 (or bounded variation) with jumps gives |c_k| ~ const/k; smooth with faster decay yields convergent budgets. This matches the repo's smooth controls.

### 3.4 Verdict
Validated.

---

## 4. Theorem 1 — energy concentration invariant

### 4.1 Formal content
Let total energy E_tot(N) = integral (f - S_N f)^2.

Let Gibbs zones around each jump have width w_N(alpha) = alpha * pi / K(N).

Let E_zone(N, alpha) be the same integral restricted to the union of zones.

Define the fraction F_N(alpha) = E_zone(N, alpha) / E_tot(N).

Claim:
- For fixed alpha, F_N(alpha) stabilizes and converges to C(alpha) in (0,1).
- For the unit square wave with alpha = 1, the observed plateau is ~0.89.

### 4.2 Classical mechanism support
Gibbs phenomenon implies a universal scaled profile near each jump and an O(1/N) oscillatory width with non-vanishing overshoot; it is consistent for zone energy to stabilize rather than vanish.

### 4.3 Critical clarification
The constant is not free-floating universal; it is tied to the zone definition (alpha and K(N)). Your updated statement correctly reflects this.

### 4.4 Remaining closure needed
To make it analyst-proof as a theorem for piecewise C1/BV, add a short proof sketch or citations for:
- existence of the limit F_N(alpha), via a scaling form and an L2 decomposition
- signal-class independence of the limit (beyond amplitude normalization)

### 4.5 Verdict
Strong and defensible; remaining work is the proof bridge.

---

## 5. N1 crossover

N1 ~ 26 for the unit square wave in this repo is a useful diagnostic threshold but not universal; it depends on normalization and the RMS definition.

---

## 6. Minimal next steps

- Add docs/theorem_1_proof_sketch.md with the minimal scaling reduction (no new math).
- Keep C(alpha) explicit in Theorem 1 statements; avoid implying alpha-independent universality.
- Optionally add one asymmetric multi-jump piecewise constant example (unequal jump heights/spacing) as a robustness control.

---

End of critique.
