# mozjpeg Sprint-3 Guardrail Prototype Notes

This captures a Sprint-3 adjustment to the routing prototype to reduce size inflation while retaining some speedup.

## Guardrail Change

`--gibbs-routing=on` routing policy changed from:

- Sprint-2: expensive trellis only for `edge`; skip for `smooth` + `mixed`

to:

- Sprint-3 guardrail: expensive trellis for `mixed` + `edge`; skip only for `smooth`

This is a conservative policy intended to reduce output-size regression.

## Artifacts

- Full patch: `docs/industry/mozjpeg_sprint3_guardrail_full.patch`
- Benchmark table: `docs/industry/mozjpeg_sprint3_guardrail_benchmark.tsv`

## Benchmark Setup

- args: `-quality 85 -optimize -progressive`
- images:
  - `testimages/testorig.ppm`
  - `testimages/monkey16.ppm`
  - `testimages/vgl_5674_0098.bmp`
- runs per row: `60`

## Result Summary

Mean values (`on` vs `off`):

- time: `8.333 ms` vs `8.667 ms`  -> `-3.8%` faster
- output size: `8899.0 B` vs `8683.7 B` -> `+2.5%` larger

Compared to Sprint-2 (`+5.9%` size increase), Sprint-3 significantly reduced the size penalty at the cost of smaller speedup.

## Recommendation

Use Sprint-3 as the new safer baseline for further tuning, then add dynamic caps:

1. Maximum allowed size delta (auto-fallback to full trellis).
2. Per-image adaptive skip-rate based on observed block-class distribution.
3. Extended corpus + perceptual metrics before any production claim.
