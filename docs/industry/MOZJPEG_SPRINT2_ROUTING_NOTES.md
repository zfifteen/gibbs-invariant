# mozjpeg Sprint-2 Routing Prototype Notes

This note captures a Sprint-2 prototype built in a temp clone that extends Sprint-1 instrumentation into actual behavior in `--gibbs-routing=on` mode.

## Prototype Behavior

In `on` mode only:

- Trellis re-quantization is applied only to blocks classified as `edge`.
- `smooth` and `mixed` blocks keep baseline quantization from the first pass.

In `off` and `log` modes:

- Behavior remains baseline (with `log` adding instrumentation output).

## Implementation Artifact

- Full patch: `docs/industry/mozjpeg_sprint2_routing_full.patch`

This patch includes Sprint-1 instrumentation plus Sprint-2 routing changes.

## Benchmark Artifact

- Table: `docs/industry/mozjpeg_sprint2_routed_benchmark.tsv`

Configuration used:

- Args: `-quality 85 -optimize -progressive`
- Images:
  - `testimages/testorig.ppm`
  - `testimages/monkey16.ppm`
  - `testimages/vgl_5674_0098.bmp`
- Runs per row: `60`

## Observed Result (Prototype)

Mean encode time:

- `off`: 8.500 ms
- `log`: 8.611 ms
- `on`: 7.333 ms

Mean output size:

- `off`: 8683.7 bytes
- `log`: 8683.7 bytes
- `on`: 9196.3 bytes

Interpretation:

- The prototype produced a real speedup in `on` mode.
- It also increased output size, so this is not yet production-ready.

## Next Steps

1. Add quality/size guardrails:
- Cap `on`-mode block skipping by target size delta.
- Fall back to full trellis when projected size drift exceeds threshold.

2. Calibrate classifier thresholds on a representative corpus.

3. Expand benchmarks:
- More images/classes.
- Include perceptual metrics (Butteraugli / SSIMULACRA2).
