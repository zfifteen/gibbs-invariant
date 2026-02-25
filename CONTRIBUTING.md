# Contributing

## Local Setup

Use Python `3.9+` with:

- `numpy`
- `matplotlib`

Quick sanity check:

```bash
python3 -m py_compile gibbs_invariant.py
MPLBACKEND=Agg python3 gibbs_invariant.py
```

## Generated Assets Policy

The files in `assets/` are generated outputs:

- `assets/energy_invariant.png`
- `assets/radius_budget_verification.png`

Rule:

- Regenerate these assets from `gibbs_invariant.py` only.
- Do not hand-edit generated images.
- Commit regenerated images only when the underlying computation, plotting logic, or presentation is intentionally changed.

