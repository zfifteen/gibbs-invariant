# mozjpeg Gibbs-Routing Final Report

## Objective

Identify a fast, credible performance win candidate from the GitHub software list, implement staged integration in a temp clone, and quantify real performance impact.

## Candidate Selection

Selected target: **mozjpeg**.

Rationale:
- Fast local setup and build.
- Clear high-cost encoding path (trellis/optimize/progressive) suitable for selective routing.
- Straightforward CLI benchmarkability.

Temp clone used:
- Path: `/tmp/gibbs-fast-win/mozjpeg`
- Base commit: `0826579`

## Work Completed

1. Built and validated mozjpeg locally with 3 test cases.
2. Implemented Sprint-1 instrumentation (`--gibbs-routing=off|log|on`).
3. Produced baseline benchmark table.
4. Captured reproducibility artifacts in this repo.
5. Implemented Sprint-2 routing prototype (`on`: trellis only on `edge` blocks).
6. Benchmarked Sprint-2 and measured speed/size tradeoff.
7. Implemented Sprint-3 guardrail prototype (`on`: trellis on `mixed`+`edge`, skip only `smooth`).
8. Benchmarked Sprint-3 and compared against Sprint-2.

## Results Summary

### Sprint-1 (instrumentation only)
From [mozjpeg_sprint1_baseline.tsv](/Users/velocityworks/IdeaProjects/gibbs-invariant/docs/industry/mozjpeg_sprint1_baseline.tsv)

- Mean `off`: `8.750 ms`, `8683.7 B`
- Mean `on`: `8.833 ms`, `8683.7 B`

Interpretation:
- No behavior change intended; confirms instrumentation overhead is small.

### Sprint-2 (edge-only trellis in `on`)
From [mozjpeg_sprint2_routed_benchmark.tsv](/Users/velocityworks/IdeaProjects/gibbs-invariant/docs/industry/mozjpeg_sprint2_routed_benchmark.tsv)

- Mean `off`: `8.500 ms`, `8683.7 B`
- Mean `on`: `7.333 ms`, `9196.3 B`
- Delta (`on` vs `off`):
  - **Timing:** `-13.7%` (faster)
  - **Output size:** `+5.9%` (larger)

Interpretation:
- Strong speed gain, but size regression too high for production.

### Sprint-3 (guardrail)
From [mozjpeg_sprint3_guardrail_benchmark.tsv](/Users/velocityworks/IdeaProjects/gibbs-invariant/docs/industry/mozjpeg_sprint3_guardrail_benchmark.tsv)

- Mean `off`: `8.667 ms`, `8683.7 B`
- Mean `on`: `8.333 ms`, `8899.0 B`
- Delta (`on` vs `off`):
  - **Timing:** `-3.8%` (faster)
  - **Output size:** `+2.5%` (larger)

Interpretation:
- Guardrail significantly reduced size penalty, but also reduced speed gain.

## Technical Conclusion

The routing concept is validated as a real compute lever, but current heuristics still trade off bitrate/size.

- Sprint-2 proves headroom exists for meaningful speedups.
- Sprint-3 shows this can be moderated with conservative policy.
- Further policy/threshold control is required before claiming production readiness.

## Recommendation

Proceed to a Sprint-4 focused on constrained optimization:

1. Add explicit size cap/fallback in `on` mode (for example, auto-fallback if projected size drift exceeds target).
2. Calibrate thresholds on larger corpus (not 3 images).
3. Add perceptual gates (Butteraugli/SSIMULACRA2) and reject if quality regresses.
4. Choose target operating point (for example: <= +1.0% size for >= -3.0% time).

## Artifact Index

Sprint-1:
- [MOZJPEG_SPRINT1_REPRO.md](/Users/velocityworks/IdeaProjects/gibbs-invariant/docs/industry/MOZJPEG_SPRINT1_REPRO.md)
- [mozjpeg_sprint1_instrumentation.patch](/Users/velocityworks/IdeaProjects/gibbs-invariant/docs/industry/mozjpeg_sprint1_instrumentation.patch)
- [mozjpeg_sprint1_baseline.tsv](/Users/velocityworks/IdeaProjects/gibbs-invariant/docs/industry/mozjpeg_sprint1_baseline.tsv)

Sprint-2:
- [MOZJPEG_SPRINT2_ROUTING_NOTES.md](/Users/velocityworks/IdeaProjects/gibbs-invariant/docs/industry/MOZJPEG_SPRINT2_ROUTING_NOTES.md)
- [mozjpeg_sprint2_routing_full.patch](/Users/velocityworks/IdeaProjects/gibbs-invariant/docs/industry/mozjpeg_sprint2_routing_full.patch)
- [mozjpeg_sprint2_routed_benchmark.tsv](/Users/velocityworks/IdeaProjects/gibbs-invariant/docs/industry/mozjpeg_sprint2_routed_benchmark.tsv)

Sprint-3:
- [MOZJPEG_SPRINT3_GUARDRAIL_NOTES.md](/Users/velocityworks/IdeaProjects/gibbs-invariant/docs/industry/MOZJPEG_SPRINT3_GUARDRAIL_NOTES.md)
- [mozjpeg_sprint3_guardrail_full.patch](/Users/velocityworks/IdeaProjects/gibbs-invariant/docs/industry/mozjpeg_sprint3_guardrail_full.patch)
- [mozjpeg_sprint3_guardrail_benchmark.tsv](/Users/velocityworks/IdeaProjects/gibbs-invariant/docs/industry/mozjpeg_sprint3_guardrail_benchmark.tsv)

Related docs:
- [INTEGRATION_GUIDE.md](/Users/velocityworks/IdeaProjects/gibbs-invariant/docs/industry/INTEGRATION_GUIDE.md)
- [SPRINT_BACKLOG_MOZJPEG.md](/Users/velocityworks/IdeaProjects/gibbs-invariant/docs/industry/SPRINT_BACKLOG_MOZJPEG.md)

## Repo Commit Trail

- `00c610c` docs: add mozjpeg sprint-1 reproduction artifacts
- `6b47c67` docs: replace integration guide and add mozjpeg sprint backlog
- `b33d0a8` docs: add mozjpeg sprint-2 routing prototype artifacts
- `134e38f` docs: add mozjpeg sprint-3 guardrail artifacts
