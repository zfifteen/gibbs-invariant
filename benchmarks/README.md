# Benchmark Signals (v1)

This folder contains deterministic 1D benchmark fixtures used by the v1 experiment and falsification gates.

- `step_function/signal.npy`
- `square_wave/signal.npy`
- `bandlimited_edge/signal.npy`
- `noisy_discontinuity/signal.npy`

Regenerate with:

```bash
python3 benchmarks/generate_benchmarks.py
```
