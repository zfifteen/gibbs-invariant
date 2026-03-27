# Gibbs Regime Switcher Demo

This demo turns Gibbs-invariant diagnostics into a live routing decision system with two modes:

- `Story`: scripted autoplay sequence across six scenes.
- `Explore`: manual scenario and time control.

## Run

```bash
python -m demo.app
```

Open `http://127.0.0.1:8050`.

## Replay

```bash
python -m demo.replay --scenario noisy_discontinuity
```

Save replay output:

```bash
python -m demo.replay --scenario step_function --output work/replay_step_function.json
```

## Scenario Files

Scenarios are JSON files in `demo/scenarios/`. They follow this contract:

```json
{
  "id": "string",
  "title": "string",
  "signal_family": "step|square|bandlimited_edge|noisy_discontinuity",
  "snr_db": 20.0,
  "jitter_fraction": 0.0,
  "n_values": [16, 32, 64, 96],
  "alpha": 1.0,
  "jump_threshold": 0.2,
  "cost_model": {"edge_weight": 1.0, "smooth_weight": 0.25},
  "script": [{"t_sec": 0.0, "action": "set_scene", "value": "invariant_convergence"}]
}
```

`bandlimited_edge` is a legacy family name kept for compatibility. In the current demo it is a closure-matched periodic smooth control, so it can serve as a true smooth negative case under the FFT's periodic wrap-around model.

## Evidence Inputs

The app validates and reads:

- `results/pipeline_summary.json`
- `results/gates_report.json`
- `results/constrained_metrics.json`
- `results/candidate_rankings.csv`

If any are missing or malformed, the UI shows a fail-fast ledger warning.
