# The Gibbs Invariant: Theorem 2 Technical Exposition

## The Persistent Circle-Length Budget

### Abstract
Visualizations of Fourier series as sums of rotating circles (epicycles) beautifully illustrate how complex waveforms emerge from simple harmonic motions. While the Gibbs phenomenon—persistent overshoot near discontinuities—is well-known locally, this essay presents a complementary global diagnostic: the cumulative sum of the radii of all circles (the “circle-length budget”). For functions with true jump discontinuities, this budget grows without bound logarithmically, adding a nearly constant increment upon doubling the number of terms. This behavior distinguishes sharp jumps from continuous or merely non-differentiable functions, where the budget converges or grows sub-logarithmically. We formalize the observation, derive the asymptotics, and propose a practical decision rule for identifying genuine discontinuities in such animations or decompositions.

### Introduction
The Fourier series expansion decomposes a periodic function into an infinite sum of sines and cosines, or equivalently, a sum of rotating phasors or “spinning circles” of varying radii and frequencies. In popular visualizations, one watches the partial sums trace increasingly accurate approximations to the target waveform, such as the iconic square wave. Near jump discontinuities, the partial sums exhibit the Gibbs phenomenon: ringing oscillations whose amplitude approaches a fixed overshoot (approximately 8.95% of the jump height) even as the oscillations narrow with higher harmonics.

Observers typically focus on these local edge effects or the diminishing size of individual added wiggles. However, these clues are inherently local and can be difficult to compare across different signals or noise levels. A more robust indicator lies in a global property: the total “circle-length budget” — the sum of the radii of all circles employed up to a given truncation order. For a target shape containing true jumps, this budget never levels off, despite the reconstructed wave remaining bounded within fixed heights. The cancellations among the many fast, tiny circles maintain the flat regions while the budget itself grows steadily.

### Defining the Circle-Length Budget
Consider a 2π-periodic function f(θ) with Fourier series
f(θ) ≈ a₀/2 + ∑_{k=1}^N [a_k cos(kθ) + b_k sin(kθ)],
where the k-th harmonic corresponds to a circle of radius
r_k = √(a_k² + b_k²).  The circle-length budget after N terms is the partial ℓ¹-norm of the coefficients:
R(N) = ∑_{k=1}^N r_k.  In epicycle animations, R(N) represents the total “ink length” or path length available from all the rotating vectors. The partial sum trajectory remains bounded, but the resources required to construct it reveal the underlying regularity of f.

### Asymptotics for the Square Wave
For the canonical square wave (plateau level normalized to 1, jumps of height 2 at odd multiples of π/2), only odd harmonics appear:
b_{2k-1} = 4 / [π (2k−1)],   a_k = 0.  Thus r_k = 4 / [π (2k−1)] for k = 1,2,... and r_even = 0.  The cumulative budget is
R(M) = (4/π) ∑_{k=1}^M 1/(2k−1),
where M is the number of odd harmonics used.  This sum behaves asymptotically as
R(M) ∼ (2/π) ln(M) + C,
where C is a constant involving the Euler–Mascheroni constant γ and ln(2). The growth is purely logarithmic.

### Doubling Behavior and the Constant Increment
When the number of circles is doubled from M to 2M, the incremental budget is
ΔR(M) = R(2M) − R(M) → (2/π) ln(2) ≈ 0.44127
as M → ∞. This increment remains essentially constant even at moderate values (e.g., M=50 to M=100 yields ΔR ≈ 0.4413). Relative to the flat-top level of 1, each doubling persistently adds about 0.44 units of radius budget. This matches empirical observation in high-resolution animations and never decays, reflecting the 1/n decay rate of the coefficients necessitated by the discontinuity.

### Contrast with Continuous or Piecewise-Smooth Functions
For functions lacking jumps, the picture changes dramatically.

For the triangle wave (continuous, piecewise linear with corners), the Fourier coefficients decay as ~1/k². Consequently, R(N) converges to a finite value (approximately 1.23 for unit-height normalization). The added budget upon doubling shrinks rapidly: 50→100 yields ΔR ≲ 0.002; at 500→1000 the increment is orders of magnitude smaller.

Any smoothing of the square wave’s edges over a small width ε causes the high harmonics to decay faster beyond k ≈ 1/ε, at which point ΔR begins to drop toward zero. Thus, only genuine jump discontinuities produce the persistent logarithmic accumulation of radius budget.

Figure 1 below illustrates this contrast directly: the square-wave budget grows linearly on a log-M scale (constant Δ per doubling), while the triangle-wave increments decay steadily.

### The Underlying Mechanism
A sharp jump discontinuity in the target function requires infinitely many high-frequency components whose amplitudes decay slowly (harmonically, ~1/k). These tiny, fast circles largely cancel one another on the flat portions of the waveform through destructive interference, keeping the reconstructed height fixed at the plateau level. At the discontinuity, their phases align constructively to attempt the instantaneous transition. This cancellation “hides” the growing budget from the visible waveform height but makes the total radius sum diverge logarithmically.  In contrast, smoother functions permit faster coefficient decay, allowing the total budget to saturate. The local Gibbs ringing is the spatial manifestation of the same slow tail: the infinite high-frequency contribution always “pushes” the partial sum by a fixed fraction near the edge (Wilbraham–Gibbs constant).

### A Practical Decision Rule
Monitor R(N) while increasing the truncation order N in the epicycle build-up. Compute or estimate the incremental budget upon doubling N.  Decision criterion: If the added total radius per doubling remains above approximately 0.2 (relative to the waveform’s plateau level) even beyond a few dozen circles (N ≳ 50), the underlying signal contains true jump discontinuities. Otherwise, the function is continuous (or has milder singularities), and any observed edge ringing will diminish substantially faster with additional terms.  This rule is robust because it is global, less sensitive to visual scaling, and directly probes the decay rate of the Fourier coefficients. It can be implemented numerically by summing the absolute values of extracted coefficients or visually estimated in animations by tracking the “new ink” added at higher resolutions.

### Conclusion
The circle-length budget that never levels off provides an elegant, intuitive, and mathematically sound complement to classical local analysis of Fourier approximations. By shifting attention from the local ringing or individual wiggle sizes to the global accumulation of harmonic resources, one gains a clear signature of genuine discontinuities: a budget that refuses to level off. This perspective not only deepens understanding of why the Gibbs phenomenon persists but also offers a practical tool for signal classification in educational visualizations, numerical analysis, and beyond.  In the age of dynamic mathematical animations, such global invariants turn passive viewing into active discovery. The persistent growth of the circle-length budget stands as a testament to the profound difference between smooth curves and those harboring true leaps.
