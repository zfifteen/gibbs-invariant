# MISSION: Gibbs-Invariant Optimization Project

## Mission Statement

Build and validate **invariant-aware optimization patterns** for Fourier/spectral software so systems stop wasting global compute on discontinuity-local error.

For contributors (human or LLM): the job is not to re-explain Gibbs qualitatively; the job is to implement, measure, and ship **decision rules** based on two computable invariants.  

## Core Insight (What is new here)

### Invariant 1: Energy Concentration Law

For piecewise-smooth periodic signals with jumps, the residual of truncated Fourier reconstruction,
`e_N = S_N f - f`, has an `N`-stable concentration fraction

`F_N(alpha) = E_zone / E_total -> C(alpha) in (0,1)`

inside shrinking jump neighborhoods of width `alpha * pi / K(N)` (`K(N)=2N+1` odd-harmonic, `K(N)=N` full-harmonic).  
In this repo’s square-wave convention, `C(1) ~= 0.89`.  
Source: [Theorem 1 statement](docs/theorem_1_energy_invariant.md), [proof sketch](docs/theorem_1_proof_sketch.md), [technical exposition](docs/theorem_1_technical_exposition.md).

### Invariant 2: Radius Budget Law

For jump signals with Fourier coefficients `c_k`, the cumulative absolute coefficient budget

`R(N) = sum_{k=1..N} |c_k|`

grows logarithmically: `R(N)=K log N + O(1)`, so

`Delta_N = R(2N)-R(N) -> K log 2` (nonzero plateau).

In this repo’s square-wave normalization:

`Delta_N -> (2/pi) log 2 ~= 0.4412712`.

Source: [Theorem 2 statement](docs/theorem_2_radius_invariant.md), [technical exposition](docs/theorem_2_technical_exposition.md).

### Operational Crossover

The repo defines `N1` as first `N` where pointwise Gibbs error fraction exceeds global RMS residual; in current normalization, square-wave `N1 ~= 26`.  
Source: [README](README.md), [Theorem 1 exposition](docs/theorem_1_technical_exposition.md).

---

## How this maps to current industry algorithms

Many deployed systems already use heuristic workarounds that implicitly acknowledge the same structure:

- MRI: global apodization/windowing
- Audio codecs: short transform windows near transients
- Image compression: perceptual metrics replacing pure PSNR/MSE
- CFD: artificial viscosity / shock-localized schemes
- ML: perceptual losses (SSIM/VGG-like) instead of pure global MSE
- Control: event-triggered/feedforward regimes

These examples are documented in [README Practical Implications](README.md) and expanded in [Industrial Implications](docs/industry/gibbs_industrial_implications.docx.md).

Project thesis: these are domain-specific partial rediscoveries of one shared rule:

1. detect jump regime,
2. stop blind global refinement,
3. allocate compute locally around discontinuities.

---

## Why industry wastes compute (mechanism, not slogan)

### The waste pattern

Past `N1`, adding global spectral resolution increases full-domain cost, but most remaining error is discontinuity-local.

Define:

- `p_N = |Omega_N| / |domain|` (fraction of domain tagged as jump-zone), typically `p_N = O(1/N)`.
- `F_N(alpha)` (fraction of residual L2 energy inside those zones), empirically high and `N`-stable for fixed `alpha` in jump signals.

When `p_N` is tiny but `F_N(alpha)` is large, global refinement spends almost all incremental compute to improve a very small subset of the domain.

### Algorithmic example (backing the claim)

For odd-harmonic square-wave mode, zone width scales as `~pi/(2N+1)`.  
At large `N`, zone coverage is `O(1/N)` while residual concentration remains near `~0.89` for `alpha=1` in repo tests.

Concrete scaling example (illustrative, not universal):

- if there are two non-overlapping jump neighborhoods, `p_N ~= 2/(2N+1)`,
- at `N=256`, `p_N ~= 2/513 ~= 0.0039` (about `0.39%` of the domain),
- yet `F_N(1)` is near `0.89` in this repo’s square-wave experiments.

So roughly 89% of residual error mass can sit in well under 1% of domain area/length.

If a global spectral stage scales like `O(N log N)`, doubling `N` from `256` to `512` increases that stage cost by about

`(512*log2(512)) / (256*log2(256)) = 2 * 9/8 = 2.25x`,

while the geometry of the difficult region remains sparse and gets narrower (`~1/N`).

Interpretation:

- error geography is highly sparse (tiny zones),
- but error mass is concentrated there,
- therefore uniform global work is poorly matched to error geometry.

This is exactly the condition where local routing beats global brute force.

---

## Why Gibbs-Invariant awareness enables more efficient implementations

### 1) Add a cheap regime detector

Use Theorem 2 online signal:

- compute rolling `Delta_N = R(2N)-R(N)` or equivalent modal-tail proxy,
- if normalized score remains above threshold (repo default rule uses `~0.2`), classify as jump-active.

Source: [Theorem 2 exposition](docs/theorem_2_technical_exposition.md).

### 2) Enforce a crossover guard

Use `N1` (or estimated analog per signal class) as guardrail:

- below `N1`: global spectral refinement is still useful,
- above `N1` + jump-active: taper/freeze global refinement.

Source: [README](README.md), [Theorem 1 exposition](docs/theorem_1_technical_exposition.md).

### 3) Route compute into a local edge path

Switch from one-budget optimization to two-budget optimization:

- smooth-region budget,
- edge-region budget.

Theorem 1 justifies this split because the residual is not uniformly distributed in jump regimes.

### 4) Evaluate with two metrics, not one

Single global MSE/PSNR/RMS can look improved while edge quality is stagnant.  
Track:

- smooth metric (bulk-domain fidelity),
- edge metric (zone-local fidelity).

This creates an objective aligned with invariant structure.

---

## Forward-looking claims and how they are backed

1. **Claim:** Invariant-gated hybrid pipelines can reduce average compute cost without degrading edge-critical quality.  
   **Backing:** Theorem 1 concentration structure + Theorem 2 jump detector + current heuristics already doing partial gating in production domains ([README](README.md), [Theorem 1](docs/theorem_1_energy_invariant.md), [Theorem 2](docs/theorem_2_radius_invariant.md)).

2. **Claim:** Radius-delta gating is practical for real systems because it is cheap relative to full re-optimization passes.  
   **Backing:** It uses coefficient magnitudes already present in spectral pipelines and relies on a scalar trend (`Delta_N`) rather than expensive segmentation ([Theorem 2 exposition](docs/theorem_2_technical_exposition.md)).

3. **Claim:** Two-budget quality control is a better optimization target than a single global metric for jump-heavy data.  
   **Backing:** `F_N(alpha)->C(alpha)` directly states persistent edge-local error concentration; global metrics can hide this concentration ([Theorem 1 proof sketch](docs/theorem_1_proof_sketch.md), [Theorem 1 exposition](docs/theorem_1_technical_exposition.md)).

4. **Claim:** The same optimization pattern should transfer across MRI/audio/compression/CFD/ML/control with domain-specific adapters.  
   **Backing:** Shared spectral mechanism and shared heuristic workarounds already observed across domains ([README](README.md), [Industrial Implications](docs/industry/gibbs_industrial_implications.docx.md)).

---

## Contributor Playbook (LLM-ready)

When contributing code, prioritize this sequence:

1. Instrument current pipeline with:
   - `Delta_N` (or nearest proxy),
   - optional `F_N(alpha)` probe in evaluation runs.
2. Implement `jump_active` gating + `N1` guard.
3. Split heavy path into:
   - global smooth path,
   - localized discontinuity path.
4. Add benchmarks:
   - compute (runtime, FLOPs, cycles/frame, memory),
   - quality (smooth metric + edge metric).
5. Report A/B deltas with explicit failure cases.

Deliverable standard for each PR:

- one runtime claim,
- one quality claim,
- one failure mode,
- all with reproducible command lines.

---

## Conventions and guardrails

- Do not assume universal constants outside stated normalization.
- Keep `alpha`, truncation convention, and normalization explicit.
- Treat strong industry statements as engineering hypotheses unless benchmarked in-repo.
- Prefer falsifiable statements and decision rules over narrative claims.

---

## Bottom line

This project’s goal is to convert Gibbs behavior from a known artifact into an optimization control signal:

- **Theorem 1** tells us where residual error lives.
- **Theorem 2** tells us when jump structure is active.
- Together they define when to stop paying for uniform global refinement and start paying for targeted local correction.
