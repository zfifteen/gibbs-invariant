# Two Computable Invariants for Fourier Approximation of Piecewise-Smooth Signals

Author: Big D  
Date: 2026-03-04

## Abstract

This technical note consolidates two linked invariants for truncated Fourier representations of piecewise-smooth periodic signals with jump discontinuities. The first invariant is an energy-allocation law: for fixed zone-width factor `alpha`, the fraction of residual `L^2` error inside shrinking jump neighborhoods converges to a nonzero constant `C(alpha)` as truncation order grows. In the repository's canonical square-wave normalization, the `alpha=1` concentration level is empirically near `0.89`. The second invariant is a coefficient-budget law: the cumulative absolute Fourier budget grows logarithmically for true-jump signals, and its per-doubling increment converges to a nonzero constant. In the same normalization, `Delta_N = R(2N)-R(N)` converges to `(2/pi) ln(2) = 0.4412712...`.

Taken together, these invariants provide a practical control signal for algorithm design. Theorem 1 describes where residual error remains concentrated after global spectral refinement, and Theorem 2 describes whether jump-class structure is active in coefficient space. The code in this repository defines an operational crossover `N₁` as the first harmonic count where fixed pointwise Gibbs error (as a fraction of jump height) exceeds global RMS residual; in the canonical square-wave setting this occurs near `N₁ ~= 26`. This note summarizes definitions, asymptotic bridge arguments, numerical checks, and engineering interpretation under the repository's explicit normalization conventions.

## 1. Setup and notation

We work on the `2pi`-periodic torus `T = [-pi, pi)` with wrapped distance `|.|_T`. Let `f : T -> R` be piecewise `C^1` (bounded variation is sufficient) with finitely many jumps at locations `J = {x_j}` and jump heights `{Delta_j}`.

For a truncation order `N`, denote the truncated reconstruction by `S_N f`, and define the residual

`e_N(x) = S_N f(x) - f(x)`.

Two truncation conventions are used in this repository:

1. Odd-harmonic truncation (square-wave mode): first `N` odd harmonics.
2. Full-harmonic truncation: first `N` harmonics in the standard full Fourier band.

To keep formulas aligned across conventions, define

`K(N) = 2N+1` for odd-harmonic truncation, and `K(N) = N` for full-harmonic truncation.

This `K(N)` controls the jump-zone shrinkage rate and appears in all concentration statements.

Define total residual energy

`E_total(N) = integral_T |e_N(x)|^2 dx`.

For zone-width factor `alpha > 0`, define jump neighborhoods

`Omega_N(alpha) = union_{x_j in J} { x in T : |x-x_j|_T <= alpha*pi/K(N) }`.

Define zone energy

`E_zone(N, alpha) = integral_{Omega_N(alpha)} |e_N(x)|^2 dx`.

Define the concentration fraction

`F_N(alpha) = E_zone(N, alpha) / E_total(N)`.

Theorem 1 concerns the asymptotic behavior of `F_N(alpha)`.

For coefficient-space analysis, let `c_k` denote Fourier coefficient magnitudes under the chosen representation and define radius budget

`R(N) = sum_{k=1..N} |c_k|`.

Define the doubling increment

`Delta_N = R(2N) - R(N)`.

Theorem 2 concerns the asymptotic behavior of `R(N)` and `Delta_N`.

### Canonical normalization used throughout this note

All concrete numerical constants in this note correspond to the same normalization as [gibbs_invariant.py](../gibbs_invariant.py), [README](../README.md), [Theorem 1 statement](theorem_1_energy_invariant.md), and [Theorem 2 statement](theorem_2_radius_invariant.md):

- square-wave plateaus are `+/-1` (jump height `2`),
- square-wave truncation uses first `N` odd harmonics,
- overshoot fractions are reported relative to jump height,
- radius increments are reported in the same amplitude convention as code constants.

Outside this normalization, constant values can change even when the qualitative invariants remain valid.

## 2. Theorem 1 (Energy concentration invariant)

### Formal statement

For piecewise-smooth periodic signals with finite jump set `J`, fixed `alpha > 0`, and truncation convention encoded by `K(N)`, the concentration fraction

`F_N(alpha) = E_zone(N, alpha) / E_total(N)`

converges as `N -> infinity` to a nontrivial limit:

`F_N(alpha) -> C(alpha)` with `C(alpha) in (0,1)`.

The limit depends on `alpha` and normalization choices, but for fixed setup it is asymptotically stable in `N`.

### Square-wave anchor in this repository

For the canonical square wave and `alpha=1`, the measured concentration level stabilizes near

`C(1) ~= 0.89`.

This is documented and cross-checked in [Theorem 1 statement](theorem_1_energy_invariant.md), [proof sketch](theorem_1_proof_sketch.md), and [Theorem 1 technical exposition](theorem_1_technical_exposition.md).

### Proof bridge (concise)

The repository's theorem bridge is:

1. **Tail-energy scale**: jump-class Fourier tails satisfy `|f_hat(k)| ~ 1/k`, so Parseval tail energy obeys
   `E_total(N) = C_total/K(N) + o(1/K(N))`.
2. **Jump-local scaling**: near each jump, residual follows a universal Gibbs profile under local variable `u = K(N)(x-x_j)`.
3. **Zone-energy scale**: integrating over neighborhoods of width `alpha*pi/K(N)` gives
   `E_zone(N, alpha) = C_zone(alpha)/K(N) + o(1/K(N))`.
4. **Ratio convergence**: numerator and denominator share the same leading scale `1/K(N)`, so their ratio converges:
   `F_N(alpha) -> C(alpha) = C_zone(alpha)/C_total`.

The full bridge appears in [Theorem 1 proof sketch](theorem_1_proof_sketch.md) with normalization caveats and references.

### Interpretation

Theorem 1 reframes Gibbs behavior from a local visualization artifact to an error-allocation law:

- Jump zones shrink geometrically like `O(1/N)`.
- Error density in those zones rises like `O(N)`.
- Their product (integrated energy share) remains asymptotically stable.

Operationally, this means global spectral refinement eventually spends substantial compute to reduce error that is geographically sparse but energetically concentrated near discontinuities.

## 3. Theorem 2 (Radius-budget invariant)

### Formal statement

For a periodic piecewise-smooth signal with at least one true jump and coefficient magnitudes `|c_k|`, define

`R(N) = sum_{k=1..N} |c_k|`.

When jumps are present, `|c_k| ~ K_coeff/k`, hence

`R(N) = K_coeff ln N + O(1)`.

Equivalently, the doubling increment converges to a nonzero plateau:

`Delta_N = R(2N) - R(N) -> K_coeff ln 2`.

Thus persistent nonzero per-doubling increment is a jump-class signature in coefficient space.

### Square-wave normalization in this repository

For canonical `+/-1` square-wave normalization with odd harmonics,

`r_m = 4/(pi*(2m-1))`, `m=1..N`,

so

`R(N) ~ (2/pi) ln N + C`,

and

`Delta_N -> (2/pi) ln(2) = 0.4412712...`.

This constant is encoded as `GIBBS_RADIUS_DELTA` in [gibbs_invariant.py](../gibbs_invariant.py) and discussed in [Theorem 2 statement](theorem_2_radius_invariant.md) and [Theorem 2 technical exposition](theorem_2_technical_exposition.md).

### Contrast with continuous controls

For continuous or corner-only controls (for example triangle-like `1/k^2` decay), absolute coefficient tails are summable:

- `R(N)` saturates toward a finite limit,
- `Delta_N` decays toward `0`.

This contrast is central to using Theorem 2 as a regime detector rather than a waveform-specific identity.

### Interpretation

Theorem 2 describes hidden representational cost. Even when pointwise waveform error away from jumps is moderate, true-jump signals continue to demand additional absolute spectral budget per doubling. Invariant-aware pipelines can use this as a low-dimensional feature for mode selection.

## 4. Operational crossover N₁ and decision use

### Crossover definition used in code/docs

The repository defines crossover `N₁` as the first truncation order `N` such that:

- fixed pointwise Gibbs error fraction of jump height exceeds
- global RMS residual at that same `N`.

In [gibbs_invariant.py](../gibbs_invariant.py), this appears in `estimate_crossover_harmonic(...)` using:

`fixed_point_error = (gibbs_overshoot(N) - 1.0)/2.0`

and

`rms = sqrt(mean((S_N f - f)^2))`.

For canonical square-wave normalization, the measured crossover is

`N₁ ~= 26`.

This value is documented in [README](../README.md), [Theorem 1 statement](theorem_1_energy_invariant.md), and [Theorem 1 technical exposition](theorem_1_technical_exposition.md).

### Why `N₁` matters operationally

`N₁` is not a universal mathematical constant. It is an implementation convention that turns asymptotic structure into a decision boundary:

1. **Below `N₁`**: global harmonic refinement remains broadly productive.
2. **Near/above `N₁`**: additional global terms disproportionately service jump-local residual structure.
3. **Above `N₁` with jump-active signal**: prefer discontinuity-aware routing (edge-local correction, targeted metrics, guarded mode switching).

### Coupling Theorem 1 and Theorem 2 in a policy

A practical two-signal policy is:

- Use Theorem 2 feature (`Delta_N` or proxy) to detect jump-active regime.
- Use Theorem 1 crossover logic (`N₁` analog) to decide when global refinement should taper.

This gives a simple control rule: detect jump-class structure, then redirect compute from uniform global refinement toward local discontinuity treatment.

## 5. Numerical verification (canonical examples)

This repository provides direct numerical checks in [gibbs_invariant.py](../gibbs_invariant.py), including square wave, sawtooth, and zone-width sensitivity.

### Canonical constants recovered in verification

Under current normalization and current implementation:

- pointwise Gibbs error fraction of jump height converges near `0.08949`,
- `alpha=1` energy concentration stabilizes near `0.89`,
- per-doubling radius increment converges near `0.4412712`,
- operational crossover is `N₁ ~= 26`.

These are the key numeric anchors referenced across [README](../README.md), [Theorem 1 docs](theorem_1_energy_invariant.md), and [Theorem 2 docs](theorem_2_radius_invariant.md).

### Representative observed behavior

For increasing `N` (square-wave mode):

- overshoot-derived jump fraction quickly settles near `0.08949`,
- `E_zone/E_total` for `alpha=1` sits in a narrow band around `0.89-0.90`,
- `Delta_N` rapidly approaches `0.4412712`,
- jump classifier based on normalized recent `Delta_N` exceeds default threshold once enough scales are available.

Additional discontinuous control (periodic sawtooth) also shows persistent nonzero doubling increments and high jump-zone concentration, supporting that invariants track jump regularity class rather than one specific waveform.

### What should be interpreted as failure

The repository's claims are intentionally falsifiable and should be treated as such in every rerun:

- If `F_N(alpha)` for a sharp jump signal and fixed `alpha` decays persistently toward zero as `N` increases, Theorem 1 behavior is not supported for that setup.
- If `Delta_N` for a jump signal collapses toward zero with increasing `N`, Theorem 2 jump-class signature is not supported for that setup.
- If measured constants drift materially after code changes (beyond expected floating-point/platform variation), treat this as a regression candidate and inspect normalization/truncation conventions first.

The check is not whether every decimal is identical; the check is whether the asymptotic pattern remains stable and consistent with the declared convention.

### Zone-width robustness

The code also reports `alpha`-dependent concentration means for square wave (for example around `0.860` at `alpha=0.5`, around `0.895` at `alpha=1.0`, and around `0.948` at `alpha=2.0` in current runs). This is expected: Theorem 1 claims convergence to `C(alpha)`, not one universal constant across all `alpha`.

### Reproducibility command

```bash
python3 gibbs_invariant.py
```

The command prints verification tables and constants, then writes the two figures in `assets/`:

- `assets/energy_invariant.png`
- `assets/radius_budget_verification.png`

For faster CI-style regression checks, the repository also includes a headless smoke test in [CI workflow](../.github/workflows/ci.yml) that asserts theorem constants and crossover behavior directly from Python without relying on GUI plotting.

## 6. Practical implications and limits

### Practical implications

Across domains that already use Fourier-like or transform-like pipelines, the two invariants can be used as routing features:

- **Detection**: use Theorem 2 trend features (`Delta_N`-style) to identify jump-active segments or regions.
- **Budgeting**: use Theorem 1 concentration/crossover structure to split quality and compute budgets into smooth-region and edge-region paths.
- **Control**: combine both to gate expensive global refinement and trigger local correction only when justified.

This perspective aligns with the repository's [MISSION](../MISSION.md) and benchmark-oriented transfer framework in [integration guide](industry/INTEGRATION_GUIDE.md).

### Limits and non-claims

This note intentionally does **not** claim universal deployment thresholds. In particular:

- `N₁ ~= 26` is tied to canonical square-wave normalization and this repository's crossover definition.
- `threshold = 0.2` in `has_true_jumps(...)` is a default operational heuristic, not a universal boundary.
- `0.89` concentration is an `alpha=1` anchor for specific conventions, not a context-free constant.

For application transfer (JPEG blocks, MDCT frames, MRI slices, PDE states), thresholds must be calibrated against corpus-specific objectives and failure modes, consistent with the "instrument -> calibrate -> guard -> benchmark" path in [industry integration guide](industry/INTEGRATION_GUIDE.md).

### Engineering stance

The right way to use these invariants is evidence-first:

1. Add diagnostics without behavior change.
2. Calibrate on development data and freeze thresholds.
3. Enable guarded routing behind fallback flags.
4. Promote only if held-out quality and runtime gates pass.

### Suggested transfer checklist for external systems

When adapting these diagnostics to production codebases, use the same sequence as [integration guide](industry/INTEGRATION_GUIDE.md) and keep each step measurable:

1. **Instrumentation-only phase**: log `Delta_N`-style features, edge-proxy features, and current pipeline decisions without changing behavior.
2. **Calibration phase**: fit thresholds on development corpus with explicit objective (ROC/F1, quality gate, business KPI).
3. **Guarded routing phase**: introduce mode switching behind flags and maintain baseline fallback paths.
4. **Hold-out validation phase**: verify that runtime improves while quality does not regress under edge-heavy/transient-heavy stress data.
5. **Production hardening**: monitor disagreement rates between heuristic gates and legacy logic, and maintain kill-switches.

This checklist matters because transfer failures are often not theorem failures. They are usually feature engineering or threshold portability failures caused by mismatched normalization, nonstationary data, or domain-specific quality criteria.

### Common implementation pitfalls

The following errors repeatedly produce misleading conclusions:

- Treating constants from canonical square-wave mode as domain-invariant magic numbers.
- Mixing odd-harmonic and full-harmonic conventions without updating `K(N)` and zone width definitions.
- Comparing metrics across amplitudes without re-normalizing jump height and plateau conventions.
- Reporting only one global quality score while claiming edge-quality improvement.

Explicitly documenting these assumptions in experiment logs is a low-cost way to prevent false positives.

That stance keeps the invariants useful as quantitative structure while avoiding overgeneralized claims.

## 7. Conclusion

The two invariants are complementary and computable:

- Theorem 1 answers where residual error lives after truncation.
- Theorem 2 answers whether jump-regime structure is active in coefficient space.

Together they define a practical optimization policy: once jump-class behavior is detected and crossover conditions are met, stop paying full price for uniform global refinement and shift effort to discontinuity-aware local treatment. The repository currently validates this policy in canonical Fourier examples with reproducible constants and explicit falsification criteria.

## Appendix A: Constants under current normalization

The table below collects constants used or verified in the canonical `+/-1` square-wave normalization used by [gibbs_invariant.py](../gibbs_invariant.py).

| Quantity | Exact / defining form | Numeric value (current) | Role |
|---|---|---|---|
| Wilbraham-Gibbs overshoot level (plateau basis) | `GIBBS_OVERSHOOT_LIMIT` | `1.178979744472167` | Pointwise asymptotic value near jump for plateau `1` |
| Overshoot as jump-height fraction | `(GIBBS_OVERSHOOT_LIMIT-1)/2` | `0.089489872236` (`~0.08949`) | Theorem 1 pointwise anchor used in crossover |
| Radius doubling invariant | `(2/pi) ln(2)` | `0.441271200305` (`~0.4412712`) | Theorem 2 asymptotic increment target |
| Radius asymptotic offset term | `(2/pi)*(2 ln(2)+gamma)` | `1.250009305807` | Constant in square-wave asymptotic fit |
| Energy concentration anchor (`alpha=1`) | empirical `C(1)` in current runs | `~0.89` | Theorem 1 zone-energy fraction anchor |
| Operational crossover harmonic count | first `N` with pointwise fraction > global RMS | `N₁ ~= 26` | Decision boundary in current implementation |

All values above are normalization-dependent. If amplitude scaling, jump height, truncation convention, or zone-width convention changes, constants may shift.

## Appendix B: Proof Sketch for Energy Concentration Stability

This appendix outlines the three-step argument that establishes `F_N(alpha) -> C(alpha)` in Theorem 1. See [theorem_1_proof_sketch.md](theorem_1_proof_sketch.md) for full details.

**Step 1: Global tail energy scales as `1/K(N)`.**
For piecewise-`C^1` (BV-sufficient) signals with jumps, Fourier coefficient asymptotics give `|c_k| ~ K/k`. By Parseval's theorem, the total truncation error energy satisfies
`E_total(N) = C_tot / K(N) + o(1/K(N))`,
where `C_tot` depends on jump heights and normalization but not on `N`.

**Step 2: Near each jump, error follows a universal scaled Gibbs profile (Dirichlet-kernel scaling).**
Using the Dirichlet-kernel representation `S_N f(x) = (1/2pi) integral f(y) D_N(x-y) dy`, decompose `f` into jump part and smooth remainder. Standard Gibbs scaling gives `e_N(x_j + u/K(N)) -> -Delta_j * g(u)` at leading order near each jump `x_j`. Here `g` is a fixed profile determined by the truncation convention; jump heights and locations enter only through `Delta_j` and `x_j`. The smooth background contributes only `o(1/K(N))` to zone energy.
Away from jumps, the Dirichlet-kernel terms from distinct discontinuities carry oscillatory phase factors that decorrelate at leading order. This phase decorrelation makes mixed cross-terms negligible in the energy ratio, so the zone energy is asymptotically additive across jumps.

**Step 3: Zone and complement energies split with the same `1/K(N)` denominator.**
Substituting the scaled variable `x = x_j + u/K(N)` inside each zone of half-width `alpha*pi/K(N)`:
`E_zone(N, alpha) = C_zone(alpha) / K(N) + o(1/K(N))`,
where `C_zone(alpha) = sum_j Delta_j^2 * integral_{-alpha*pi}^{alpha*pi} g(u)^2 du`.
The complement carries the remaining energy at the same `1/K(N)` scale. Since numerator and denominator share the same leading-order scale,
`F_N(alpha) = E_zone(N, alpha) / E_total(N) -> C_zone(alpha) / C_tot = C(alpha) in (0,1)`.

## Appendix C: Mapping to repository functions

This appendix maps formal quantities in this note to implementation points in [gibbs_invariant.py](../gibbs_invariant.py).

| Concept | Formula / definition | Implementation mapping |
|---|---|---|
| Square-wave truncation | odd-harmonic partial sum for `N` terms | `square_wave_partial_sum(x, N, amplitude)` |
| Residual `e_N` | `S_N f - f` | computed inline in `verify_invariants()` and helper functions |
| Pointwise Gibbs level | local max near jump | `gibbs_overshoot(N, ...)` |
| Pointwise jump fraction | `(gibbs_overshoot(N)-1)/2` | derived in `plot_energy_invariant()` and `verify_invariants()` |
| Jump zones `Omega_N(alpha)` | wrapped neighborhoods of width `alpha*pi/K(N)` | `energy_concentration_fraction_for_signal(..., zone_width_factor, harmonic_bandwidth)` |
| Concentration fraction `F_N(alpha)` | `E_zone/E_total` | `energy_concentration_fraction(...)` (square-wave specialization) |
| Generic concentration (other jump signals) | same ratio with custom target and partial sum | `energy_concentration_fraction_for_signal(...)` |
| Sawtooth verification path | discontinuous non-square control | `sawtooth_wave`, `sawtooth_partial_sum`, `sawtooth_energy_concentration_fraction` |
| Radius budget `R(N)` | `sum_{k<=N} |c_k|` | `square_wave_radii`, `sawtooth_radii`, `cumulative_radius_budget` |
| Doubling increment `Delta_N` | `R(2N)-R(N)` | `radius_doubling_deltas(radii, min_n)` |
| Jump-active detector | normalized recent `Delta_N` trend | `has_true_jumps(radii, plateau, threshold)` |
| Operational crossover `N₁` | first `N` with pointwise fraction > global RMS | `estimate_crossover_harmonic(max_N)` |
| End-to-end verification and report | numerical tables + constants + robustness checks | `verify_invariants()` |

For theorem-level details behind these routines, see [Theorem 1 technical exposition](theorem_1_technical_exposition.md), [Theorem 1 proof sketch](theorem_1_proof_sketch.md), and [Theorem 2 technical exposition](theorem_2_technical_exposition.md).
