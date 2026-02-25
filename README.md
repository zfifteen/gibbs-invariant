![The Gibbs Invariant Banner](assets/readme-banner.png)

# The Gibbs Invariant

> *Everyone knows the Gibbs phenomenon produces a persistent overshoot near discontinuities. Far fewer know that this overshoot is the visible tip of a deeper structure — one with quantifiable, scale-invariant properties that have concrete engineering consequences.*

---

## What This Is

This repository develops two linked theorems that reframe the Gibbs phenomenon: not as a local amplitude artifact, but as a **global structural property** of Fourier representations applied to piecewise-smooth signals.

The short version:

**Theorem 1 — The Gibbs Energy Invariant:** When you truncate a Fourier series, ~89% of all remaining squared error locks permanently into vanishingly narrow zones around each discontinuity. This fraction doesn't decay as you add harmonics. It is scale-invariant from N=10 to N=10,000. And it defines a computable crossover N₁ beyond which adding more global harmonics delivers less than 11% of remaining error reduction to the 90%+ of the domain that is actually smooth.

**Theorem 2 — The Gibbs Radius Invariant:** In the equivalent epicycle representation, a signal with true jump discontinuities requires a radius budget that grows without bound — adding exactly **(2/π)ln(2) ≈ 0.4413** units per doubling of circles, forever, regardless of how many circles are already employed. Smooth signals converge to a finite budget. The threshold is closed-form and exact, not empirical.

---

## Why It Matters

The Gibbs phenomenon has been known since 1899. What hasn't been stated cleanly until now is the **structural consequence**: there is a computable point N₁ beyond which globally-optimal Fourier methods become locally catastrophic, and the rational engineering response is always the same — make discontinuities explicit in the representation rather than leaving them implicit.

Every field that uses spectral methods on real-world signals has independently rediscovered this principle as a heuristic:

| Domain | The Heuristic Workaround |
|---|---|
| MRI reconstruction | Apodization (global windowing) |
| Audio codecs | Short transform windows near transients |
| Image compression | Perceptual quality metrics over PSNR |
| Computational fluid dynamics | Artificial viscosity near shocks |
| Machine learning | Perceptual loss functions (VGG, SSIM) |
| Control systems | Event-triggered and feedforward control |

These are all partial, independent rediscoveries of the same principle — applied without the theoretical justification that explains *why* they work, and therefore calibrated empirically rather than optimally.

The Gibbs Invariant framework is the unifying theory underneath all of them.

---

## The Core Results at a Glance

### Energy Invariant
For a piecewise-smooth signal with jump discontinuities, truncated to N Fourier terms:

- **~89% of total squared error** concentrates inside zones of width **π/N** around each discontinuity
- This fraction is **constant across all N** — it does not decay as you add harmonics
- Error density inside the zone scales as **N/π**, exactly compensating the shrinkage
- The crossover **N₁ ≈ 13** (unit square wave) marks the point at which Gibbs zone error surpasses global RMS error — after which global refinement is structurally inefficient

### Radius Invariant
For the same signal in epicycle form, the cumulative radius budget R(N) = Σ|cₖ|:

- Grows **logarithmically without bound**: R(M) ~ (2/π)ln(M) + C
- Per doubling: **ΔR → (2/π)ln(2) ≈ 0.4413** — exact, closed-form, invariant
- Smooth signals (triangle wave, etc.) converge to finite budget; increments decay to zero
- Decision rule: if the per-doubling increment stays **above ~0.2** past N ≈ 50, the signal contains true jump discontinuities

The mechanism behind both: at a discontinuity, every missing harmonic is **in phase** — their collective absence hits constructively. In smooth regions, missing harmonics have scattered phases and cancel. The jump is the one place where everything goes wrong at once, and it goes wrong in a precisely quantifiable way.

---

## Repository Contents

```
docs/
├── theorem_1_energy_invariant.md          ← Start here: Theorem 1 statement
├── theorem_1_technical_exposition.md      ← Full derivation and analysis
├── theorem_2_radius_invariant.md          ← Theorem 2 statement
├── theorem_2_technical_exposition.md      ← Full derivation and analysis
└── industry/
    └── gibbs_industrial_implications.md   ← Cross-domain engineering implications
```

### Suggested Reading Order

1. **`theorem_1_energy_invariant.md`** — The energy concentration result. Start with the theorem statement before the machinery.
2. **`theorem_2_radius_invariant.md`** — The radius budget result. Two pages, self-contained.
3. **`theorem_1_technical_exposition.md`** — Full derivation: harmonic energy accounting, phase-coherence mechanism, crossover interpretation, falsification criteria.
4. **`theorem_2_technical_exposition.md`** — Square-wave asymptotics, the (2/π)ln(2) derivation, contrast cases, decision rule.
5. **`industry/gibbs_industrial_implications.md`** — Eight domains, two invariants, one unified framework.

---

## Falsifiability

These are not observations dressed as theorems. Each result has explicit falsification criteria stated in the technical expositions.

The Gibbs Energy Invariant is falsified if, for a sharp square wave, the fraction of squared error inside a π/N zone around each discontinuity decays steadily with N rather than converging to a constant near 89%.

The Gibbs Radius Invariant is falsified if, for a sharp square wave, the added total radius per doubling decays steadily rather than settling near (2/π)ln(2) ≈ 0.4413.

Both have been verified numerically across N = 10 through N = 1,600 with convergence to theoretical values.

---

## Status

The theoretical results are established for the canonical piecewise-smooth case (square wave and relatives). Active work covers:

- [ ] Generalization of N₁ to the full piecewise-smooth function class  
- [ ] 2D extension (edges replacing point discontinuities)  
- [ ] Noise robustness analysis and modified detection thresholds  
- [ ] Non-uniform sampling analog  
- [ ] Formal submission

---

## Citation

If you use these results, please cite this repository until a formal paper is available.

```
@misc{gibbs-invariant,
  title   = {The Gibbs Invariant: Energy Concentration and Radius Budget Theorems
             for Fourier Representations of Piecewise-Smooth Signals},
  year    = {2026},
  url     = {https://github.com/zfifteen/gibbs-invariant}
}
```

---

*The Gibbs phenomenon has been called an annoyance, an artifact, a limitation. It is all of those things. It is also a precise, scale-invariant, closed-form structure that tells you exactly where your representation is failing and why. That's not a problem to be managed. That's information.*
