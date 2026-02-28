# mozjpeg Core Integration Correction Report

## Executive Summary

The prior integration was **incorrect for core scope** because it modified trellis behavior in `on` mode, which changed compression outcomes (larger output size).

This corrected integration restores core scope:

- Keep Gibbs feature extraction, classification, and reporting.
- Do **not** change quantization/trellis/entropy behavior.
- Enforce byte-equivalence across `off`, `log`, `on`.

Result: output-size side effect is eliminated.

## Root Cause of Size Increase

The size increase came from Sprint-2/3 experimental logic in `compress_trellis_pass` that conditionally/segmentally invoked `quantize_trellis*()`.

That altered core rate-distortion optimization, including cross-block trellis context. It was outside the minimal Gibbs integration contract.

Evidence from controls:

- `--gibbs-routing=on` with trellis-path edits increased output size.
- When trellis is fully disabled (`-notrellis`), `off` and `on` outputs were identical.
- Therefore the size increase was caused by trellis behavior changes, not instrumentation/logging.

## Correct Integration Contract

For core integration:

1. `off`: baseline encoder behavior.
2. `log`: baseline behavior + Gibbs statistics logging.
3. `on`: same encoding behavior as `off`; may emit routing diagnostics, but no encode-path change.

All three modes must produce identical bytes for identical encode settings.

## Corrected Artifacts

- Core patch: [mozjpeg_core_integration.patch](/Users/velocityworks/IdeaProjects/gibbs-invariant/docs/industry/mozjpeg_core_integration.patch)
- Byte-equivalence table: [mozjpeg_core_equivalence_summary.tsv](/Users/velocityworks/IdeaProjects/gibbs-invariant/docs/industry/mozjpeg_core_equivalence_summary.tsv)
- Overhead table: [mozjpeg_core_overhead.tsv](/Users/velocityworks/IdeaProjects/gibbs-invariant/docs/industry/mozjpeg_core_overhead.tsv)

## Validation Results

### Byte-equivalence (3 images x 2 configs)

From [mozjpeg_core_equivalence_summary.tsv](/Users/velocityworks/IdeaProjects/gibbs-invariant/docs/industry/mozjpeg_core_equivalence_summary.tsv):

- `off_eq_log = yes` for all rows
- `off_eq_on = yes` for all rows
- Byte counts identical for `off/log/on` in all tested cases

### Runtime overhead

From [mozjpeg_core_overhead.tsv](/Users/velocityworks/IdeaProjects/gibbs-invariant/docs/industry/mozjpeg_core_overhead.tsv):

Mean across all rows:

- `off`: `7.896 ms`
- `log`: `7.812 ms` (`-1.055%` vs off)
- `on`: `7.854 ms` (`-0.528%` vs off)

Interpretation:
- No measurable performance penalty from core instrumentation in this test set.
- Small differences are within normal benchmark noise.

## Scope Separation Going Forward

- Core integration remains safe, byte-equivalent, and reproducible.
- Experimental optimization policies (routing that changes trellis behavior) must remain separate and explicitly labeled non-core.

## Recommendation

Accept this corrected core integration as the canonical implementation of your Gibbs invariant findings.

If optimization experiments continue, gate them behind separate experimental flags and require explicit size/quality constraints before claiming improvements.
