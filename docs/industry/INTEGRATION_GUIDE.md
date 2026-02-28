# Integration Guide (Evidence-First)

This guide replaces speculative claims with a benchmark-first plan for identifying real performance improvements in candidate software from [github_candidate_software_list.md](./github_candidate_software_list.md).

## Scope

What is validated in this repository:

- Theorem 1 behavior on canonical Fourier examples (error concentration near jumps).
- Theorem 2 behavior on canonical Fourier examples (persistent radius-growth for jump signals).

What is not validated here yet:

- Universal thresholds for JPEG DCT blocks, MDCT audio frames, MRI k-space, or CFD fields.
- Direct percentage gains (speed, bitrate, quality) in third-party production codebases.

Because of that, this guide treats Gibbs-invariant signals as routing features that must earn their keep under A/B benchmarks.

## Ground Rules for "Genuine Improvement"

Use this promotion sequence for every target application:

1. Instrument only: compute features and log them, but do not change behavior.
2. Calibrate thresholds per corpus: choose thresholds by ROC/F1 or business KPI, not by copying `0.2` or `N1=26`.
3. Add guarded routing: only switch to expensive/cheap paths when confidence is high.
4. Ship only if benchmark gates pass on held-out data.

If gates do not pass, keep the diagnostic feature but do not claim optimization.

## Candidate Integrations

## 1) mozjpeg or libjpeg-turbo

Primary goal: improve encode efficiency (time and/or bitrate-quality tradeoff) with minimal risk.

Integration seam:

- Block-level decision step before expensive rate-distortion work (trellis/iterative tuning).

Practical integration:

1. Compute a cheap block score from quantized AC magnitudes or gradient energy.
2. Bucket blocks into `smooth`, `mixed`, `edge`.
3. Apply expensive optimization only to `edge` blocks; keep fast path for `smooth`.
4. Keep baseline mode as fallback flag.

Benchmark gates:

- Runtime gate: faster encode wall-time without perceptual regression.
- Compression gate: lower bitrate at matched perceptual quality.
- Minimum reporting: wall-time, bpp, SSIMULACRA2 or Butteraugli, and failure-rate on text/UI images.

Why this is credible:

- It targets known expensive encoder paths and uses a cheap classifier.
- It does not assume Theorem 2 constants transfer directly to single 8x8 blocks.

## 2) libopus

Primary goal: reduce encoder analysis CPU on non-transient content while preserving transient quality.

Integration seam:

- Transient/window-decision path in CELT analysis.

Practical integration:

1. Add a cheap transient prior from MDCT magnitude dynamics (frame-local, streaming-safe).
2. If prior is confidently low for consecutive frames, skip deeper transient analysis.
3. If prior is high/uncertain, run existing full detector unchanged.
4. Log disagreement rate between prior and full detector.

Benchmark gates:

- CPU gate: lower cycles per encoded second on speech + music corpus.
- Quality gate: no increased pre-echo on transient-heavy clips.
- Minimum reporting: RTF/cycles, objective score (PEAQ/POLQA where applicable), and ABX listening outcomes.

Why this is credible:

- It avoids replacing the mature detector outright.
- It uses the new feature as a safe early-exit signal first.

## 3) CompressAI

Primary goal: improve rate-distortion (quality at fixed bitrate, or bitrate at fixed quality) with controlled complexity.

Integration seam:

- Loss function and training sample policy.

Practical integration:

1. Start with architecture unchanged.
2. Add edge-aware distortion weighting from deterministic masks (Sobel/Canny-based).
3. Optionally oversample edge-rich patches during training.
4. Compare against stock MSE or MS-SSIM baselines under identical training budget.

Benchmark gates:

- RD gate: negative BD-rate on Kodak and CLIC.
- Cost gate: no material inference latency increase for the same deployed model.
- Minimum reporting: BD-rate (PSNR and MS-SSIM), training time, inference latency.

Why this is credible:

- It targets the objective directly and keeps model risk low in v1.
- It produces a clear accept/reject decision using standard codec metrics.

## 4) BART or DIRECT (MRI)

Primary goal: reduce unnecessary global de-ringing work and protect edge sharpness.

Integration seam:

- Post-reconstruction Gibbs-correction stage (diagnostic then selective correction).

Practical integration:

1. Build an edge-confidence mask from reconstruction-domain and k-space-tail features.
2. Run local correction in high-confidence zones only.
3. Keep global correction path as fallback.
4. Evaluate on phantoms first, then retrospective clinical datasets.

Benchmark gates:

- Runtime gate: lower post-processing time per slice/volume.
- Image gate: non-inferior global quality with improved boundary sharpness metrics.
- Minimum reporting: runtime, edge spread metrics, and blinded reader preference if available.

Why this is credible:

- It changes correction scope, not core reconstruction physics.
- It limits risk through fallback and phased validation.

## Quick Calibration Template

Use this template for every application before optimization claims:

1. Assemble three datasets: `dev`, `test`, `stress` (edge-heavy/transient-heavy cases).
2. Log candidate score + current pipeline decision + final KPI outcome.
3. Tune threshold(s) on `dev`.
4. Freeze thresholds and report on `test`.
5. Confirm robustness on `stress`.

Only after passing this process should any gain be called "real."

## What to Avoid

- Treating `N1 = 26` as a universal constant outside the square-wave normalization.
- Reusing `threshold = 0.2` without calibration on the target domain.
- Claiming fixed gains (for example "30-50%") before measured A/B evidence.
- Replacing stable production heuristics in one step instead of adding guarded routing.

## Recommended First Sprint

If you want one low-risk, high-signal starting path:

1. Implement diagnostic-only logging in `mozjpeg` (or `libjpeg-turbo`) and `libopus`.
2. Run corpus benchmarks and produce threshold calibration plots.
3. Enable selective routing behind feature flags.
4. Promote only the path that passes quality and performance gates.
