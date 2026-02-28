# Sprint Backlog: mozjpeg (Genuine Optimization Track)

## Objective

Establish whether Gibbs-inspired block routing can improve `mozjpeg` encode efficiency without perceptual regressions.

## Scope (Sprint 1)

- No behavior change by default.
- Instrumentation first, then guarded routing behind a feature flag.
- Report measured results only.

## Work Items

1. Add block instrumentation
- Compute per-block cheap features during encode analysis:
  - AC magnitude sum (`l1_ac`)
  - Gradient energy proxy (`grad_energy`) if source pixels available at that stage
- Log per-image histograms and per-block summaries to CSV/JSON.
- Acceptance: metrics emitted for full corpus with negligible crash risk.

2. Add diagnostic labels and thresholds
- Define temporary block classes: `smooth`, `mixed`, `edge`.
- Build an offline threshold calibration script using dev corpus.
- Acceptance: threshold config file produced with ROC/F1 summary.

3. Add feature flag and guarded routing
- New flag example: `--gibbs-routing=[off|log|on]`.
- `off`: baseline behavior.
- `log`: compute + log decisions, no encode behavior change.
- `on`: route only high-confidence `edge` blocks to expensive optimization path.
- Acceptance: bit-identical output for `off`; stable encode for `log` and `on`.

4. Benchmark harness
- Automate runs across corpora:
  - natural photos
  - text/UI screenshots
  - line art / edge-heavy images
- Collect:
  - wall-clock encode time
  - output size (bpp)
  - perceptual metrics (Butteraugli and/or SSIMULACRA2)
- Acceptance: single command generates reproducible benchmark table.

5. Evaluate promotion criteria
- Promotion requires all:
  - encode time improvement on aggregate corpus
  - no perceptual regression beyond agreed tolerance
  - no pathological regression on text/UI subset
- Acceptance: pass/fail decision documented from held-out test split.

## Suggested Task Breakdown

1. Engineering
- Implement instrumentation and flag plumbing.
- Implement routing branch and safe fallback.

2. Data/Benchmark
- Build corpus manifest and split into `dev/test/stress`.
- Run calibration and locked-threshold test.

3. Reporting
- Produce one-page results summary:
  - baseline vs `log` vs `on`
  - percentile latency deltas
  - bitrate/perceptual tradeoff plots

## Risks and Controls

- Risk: false edge positives route too many blocks to expensive path.
- Control: cap routed-block ratio and fail closed to baseline.

- Risk: metric gains hide visual regressions in UI/text.
- Control: separate UI/text gate with stricter perceptual threshold.

- Risk: noisy benchmark results.
- Control: fixed machine, repeated runs, median + p95 reporting.

## Definition of Done

- Feature flag merged with default `off`.
- Reproducible benchmark pipeline committed.
- Thresholds frozen from `dev` only.
- Final decision from held-out `test` documented as one of:
  - promote `on`
  - keep diagnostic `log` only
  - reject routing and keep baseline
