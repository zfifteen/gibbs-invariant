# applicability difference between the two theorems.

The two theorems are about the same underlying Gibbs structure, but they “plug in” at different levels and for different kinds of tasks.

### Very short summary

- **Theorem 1 (Energy Invariant):**
    - About where the *error* lives.
    - Best for deciding **when** to stop using global Fourier methods and **how** to measure quality (two‑budget metrics).[^1][^2]
- **Theorem 2 (Radius Invariant):**
    - About how much *resource* the representation is silently spending.
    - Best for **detecting** true discontinuities and steering algorithms in real time (mode switches, edge detectors).[^3][^4]

***

### Theorem 1: Energy Concentration Invariant – where to spend effort

Core statement:

- Roughly **89 percent** of the squared reconstruction error of a truncated Fourier series for a piecewise‑smooth signal lives in tiny zones around discontinuities, and that fraction is essentially invariant as you add more terms.[^2][^1]
- There is a crossover $N_1$: beyond it, adding harmonics mostly improves already smooth regions while the edge artifact stays structurally fixed in amplitude and only shrinks in width.[^5][^2]

What it is best for:

- **Global strategy and budgeting.**
    - Deciding when you have crossed from “global refinement is worthwhile” to “global refinement is wasteful; do something local at edges instead.”
    - Splitting quality metrics into **smooth‑region vs edge‑region budgets**, since global MSE/PSNR is structurally misleading past $N_1$.[^2][^5]

Where it is most applicable:

- **Algorithm design / evaluation:**
    - MRI: when to stop pushing k‑space resolution and instead run edge‑aware reconstruction.[^5]
    - Codecs: when more transform resolution just feeds ringing at edges instead of improving the picture or sound.[^5]
    - Neural nets: how to design loss functions and capacity allocation (two‑budget losses) so edges and smooth regions are weighted appropriately.[^5]

Think of Theorem 1 as:
> “Given a fixed Fourier‑like representation, it tells you how the remaining error is partitioned and when you must change tactics to be efficient.”

***

### Theorem 2: Radius Budget Invariant – how to detect true jumps

Core statement:

- In the spinning‑circle (epicycle) view, if the target has **true jump discontinuities**, the total radius sum $R_N$ over all circles never levels off.
- Each **doubling** of the number of circles adds almost the same extra amount to $R_N$, asymptotically about $2\ln 2 \approx 0.44$ relative to the plateau height.[^4][^3]
- For continuous or mildly singular signals, $R_N$ converges or its increments per doubling decay rapidly toward zero.[^4]

What it is best for:

- **Classification and detection.**
    - Distinguishing “real jumps” from “merely steep but smooth” or noisy signals, using only the coefficient magnitudes.[^3][^4]
    - Providing a **computable, scale‑free test** that can run cheaply in pipelines operating on spectral data.

Where it is most applicable:

- **Mode selection and control logic:**
    - Audio: real‑time transient detection by monitoring radius increments per doubling; then switching to short windows or special transient handling when the increment stays high.[^3][^5]
    - Image / video: automatically flagging regions that contain true edges versus texture, to drive edge‑specific coding or post‑processing.[^4][^5]
    - MRI \& sensors: detecting boundaries or regime changes (e.g., financial time‑series breaks) via the logarithmic growth signature.[^5]

Think of Theorem 2 as:
> “Given access to the coefficients, it tells you whether you are looking at a true jump and can drive real‑time decisions based on that.”

***

### How to choose which theorem to use

- If your question is **“Are we beyond the point where more global resolution makes sense, and how should we score quality?”**, use **Theorem 1**.
    - You use it to define $N_1$, and to build edge vs smooth error budgets.[^2][^5]
- If your question is **“Is this region / signal segment genuinely discontinuous, and should I switch modes here?”**, use **Theorem 2**.
    - You use it as a discontinuity detector or regime detector based on radius‑budget increments.[^3][^4]

They are complementary: Theorem 1 tells you *how bad the edge trap is and when to stop*, and Theorem 2 tells you *where the true edge regions actually are* so you can treat them separately.

<div align="center">⁂</div>

[^1]: theorem_1_energy_invariant.md

[^2]: theorem_1_technical_exposition.md

[^3]: theorem_2_radius_invariant.md

[^4]: theorem_2_technical_exposition.md

[^5]: gibbs_industrial_implications.docx.pdf

