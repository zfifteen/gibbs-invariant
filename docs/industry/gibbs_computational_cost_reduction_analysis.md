# Gibbs-Invariant Computational Cost Reduction Analysis

## Scope

This note translates the findings in:

- `docs/theorem_1_energy_invariant.md`
- `docs/theorem_1_proof_sketch.md`
- `docs/theorem_1_technical_exposition.md`
- `docs/theorem_2_radius_invariant.md`
- `docs/theorem_2_technical_exposition.md`
- `docs/industry/gibbs_industrial_implications.docx.md`

into concrete software cost-reduction strategies.

## The Findings That Matter for Cost

### 1) Energy concentration invariant (Theorem 1)

For jump signals under Fourier truncation:

- Gibbs-zone width shrinks as `O(1/K(N))`.
- A stable fraction `F_N(alpha) -> C(alpha)` of residual `L2` error stays in jump zones.
- In this repo, square wave with `alpha=1` stabilizes near `C(1) ~= 0.89`.

Operational implication:
after the crossover `N1`, increasing global harmonic count keeps spending compute on a tiny spatial/temporal subset (edge zones), not on the smooth majority.

### 2) Radius budget invariant (Theorem 2)

For jump signals:

- `R(N) = sum_{k<=N} |c_k| = K log N + O(1)`.
- Doubling increment `Delta_N = R(2N)-R(N) -> K log 2` (nonzero plateau).
- For repo square-wave normalization: `Delta_N -> (2/pi) log 2 ~= 0.4413`.

Operational implication:
when `Delta_N` stays nonzero, you are in a jump regime where global spectral enrichment is structurally expensive and asymptotically inefficient.

## Cost Model: Why Global Refinement Becomes Wasteful

Let:

- `C_global(N)` = per-step cost of global spectral processing (commonly `O(N log N)` or worse with iterative solvers).
- `p_N` = fraction of domain covered by jump zones (`p_N ~ O(1/N)`).
- `C(alpha)` = Gibbs residual concentration fraction (often high; ~0.89 here for one reference setup).

Beyond `N1`:

- Most residual error budget (`~C(alpha)`) is edge-localized.
- Global refinement increases full-domain cost, but only meaningfully targets a sparse region.

So the better asymptotic strategy is:

1. stop or slow global `N` growth near `N1`,
2. activate localized edge handling on `p_N << 1` subset,
3. keep smooth and edge budgets separate.

### Rule-of-thumb speedup bound

For any stage where cost is proportional to processed samples (`M`):

- global processing cost: `~M`,
- localized edge processing cost: `~p_N M + overhead`.

Approximate upper-bound speedup is therefore:

`speedup ~= 1 / (p_N + overhead/M)`.

When discontinuity zones occupy 1% to 10% of the domain, even with moderate routing overhead, practical speedups are typically in the low-single-digit to low-double-digit range depending on implementation.

## Runtime Policy Template (Domain-Agnostic)

1. Compute/update harmonic coefficients already available in the pipeline.
2. Track `Delta_N = R(2N)-R(N)` on a rolling window.
3. If normalized `Delta_N` is above threshold (repo default rule: `> 0.2` after scaling), classify as jump-active.
4. Estimate or cache crossover `N1` (repo square-wave convention currently gives `N1 ~= 26`; older documents may report different values under different normalization).
5. If current `N > N1` and jump-active:
   - freeze or taper global resolution growth,
   - route compute to edge-local module,
   - optimize against two metrics:
     - smooth-region error,
     - edge-zone error.

This turns a single expensive global loop into a guarded hybrid loop.

## Software Classes and Concrete Compute Savings Levers

### MRI reconstruction software (k-space inverse recon stacks)

Examples: BART-like pipelines, Gadgetron-like pipelines, custom hospital/vendor recon.

- Expensive pattern: repeated global resolution/iteration increases to reduce ringing.
- Invariant-guided change: detect jump-active boundaries from coefficient tails and run local de-ringing near detected edges only.
- Compute impact: fewer full-frame high-resolution recon passes; edge correction on sparse masks.

### Audio codec/processing software

Examples: Opus/AAC/MP3 encoders, FFmpeg transform pipelines.

- Expensive pattern: overuse of short windows or high-band refinement across non-transient frames.
- Invariant-guided change: use radius-delta plateau as transient/jump gate; switch windows or transient path only when jump-active.
- Compute impact: fewer short-window transforms and less high-frequency processing on stable frames.

### Image compression software

Examples: JPEG/mozjpeg-style encoders, DCT or transform codecs.

- Expensive pattern: spending bits/compute on global coefficient retention to chase edge ringing.
- Invariant-guided change: two-path allocation:
  - low-cost smooth path for most blocks,
  - explicit edge path (edge map + localized coefficient budget).
- Compute impact: reduced search/optimization in smooth blocks, targeted expensive processing in edge blocks.

### CFD and shock-capable simulation software

Examples: spectral solvers, hybrid spectral/finite-volume stacks, AMR frameworks.

- Expensive pattern: global polynomial-order or grid growth after shocks form.
- Invariant-guided change: use jump detection (`Delta_N`-style behavior in modal tails) to trigger local scheme switch near shocks.
- Compute impact: avoid full-domain over-refinement; preserve expensive high-order treatment where flow remains smooth.

### Telecom and signal reconstruction software

Examples: SDR pipelines, spectral channel reconstruction, filtering stacks.

- Expensive pattern: uniformly increasing bandwidth/order to reduce discontinuity artifacts.
- Invariant-guided change: encode or model discontinuity events explicitly (side channel / event stream) and reserve global spectral budget for smooth components.
- Compute impact: lower required global transform size and lower iterative equalization burden.

### ML training/inference software on piecewise-smooth signals

Examples: image/audio restoration, neural compression, super-resolution.

- Expensive pattern: global MSE-driven capacity inflation to improve edge behavior.
- Invariant-guided change: split architecture and loss into smooth/edge branches; activate heavy edge branch sparsely.
- Compute impact: lower average FLOPs per sample at inference, better training efficiency via targeted hard-region optimization.

### Scientific instrumentation reconstruction software

Examples: spectroscopy, aperture synthesis, tomography pipelines.

- Expensive pattern: global resolution increase to recover sharp-feature fidelity.
- Invariant-guided change: keep nominal global reconstruction moderate and apply super-resolution/local inversion only near inferred discontinuities.
- Compute impact: fewer global expensive inversion iterations and better compute-per-usable-detail ratio.

### Control and optimization software

Examples: MPC stacks with switching references, event-driven controllers.

- Expensive pattern: high-rate global solve even when discontinuities are absent.
- Invariant-guided change: jump-regime detector gates high-bandwidth/event solver; smooth regime uses cheaper baseline controller.
- Compute impact: reduced average solver frequency and lower CPU load without sacrificing switch-event performance.

## Implementation Checklist for Existing Codebases

1. Add two telemetry signals:
   - `F_N(alpha)` proxy or edge-zone residual ratio,
   - `Delta_N = R(2N)-R(N)` (or equivalent modal-tail indicator).
2. Add crossover guard:
   - conservative initial `N1`,
   - hard or soft cap on global refinement beyond `N1`.
3. Add local edge module:
   - edge/transient detection,
   - localized correction/reconstruction branch.
4. Replace single global quality KPI with two-budget KPI:
   - smooth-region metric,
   - edge-region metric.
5. Tune threshold and routing using offline sweeps, then enforce in production.

## Expected Outcome Pattern

When discontinuities are sparse (typical in piecewise-smooth real data), the hybrid policy consistently reduces wasted global computation. The strongest savings appear in pipelines currently spending significant runtime on global refinement past `N1`.

In short:

- Theorem 1 explains where residual error is trapped.
- Theorem 2 gives a cheap detector for when that trap is active.
- Together they justify replacing brute-force global spectral escalation with adaptive local handling, which is the main path to lower compute cost in the software classes listed in the industrial implications report.
