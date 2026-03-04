# Release Verification: v0.1.0

## Publication Metadata

- Release tag: `v0.1.0` (pending tag creation)
- Release date target: 2026-03-04
- Repository: `https://github.com/zfifteen/gibbs-invariant`
- Zenodo concept DOI: pending first publication
- Zenodo version DOI: pending first publication

## Reproducibility Commands

```bash
python3 -m py_compile gibbs_invariant.py
MPLBACKEND=Agg python3 gibbs_invariant.py
```

## Expected Console Verification Markers

- `Theorem 2 delta-per-doubling target: 0.441271200305`
- `Theorem 1 overshoot target (plateau=1): 1.178979744472`
- `Theorem 1 pointwise error as jump fraction: 0.089489872236`
- `Estimated crossover N where pointwise Gibbs error > global RMS error: 26`

## Generated Assets

- `assets/energy_invariant.png`
- `assets/radius_budget_verification.png`

## Completion Checklist

- [x] MIT `LICENSE` added
- [x] `CITATION.cff` added
- [x] `.zenodo.json` added
- [x] README citation section updated for DOI placeholders
- [ ] Annotated Git tag created and pushed
- [ ] GitHub release published
- [ ] Zenodo draft reviewed and published
- [ ] DOI badge and links inserted into README
