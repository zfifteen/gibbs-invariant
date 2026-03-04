# Release Verification: v0.1.0

## Publication Metadata

- Release tag: `v0.1.0` (pending tag creation)
- Release date target: 2026-03-04
- Repository: `https://github.com/zfifteen/gibbs-invariant`
- Technical note DOI (version): `10.5281/zenodo.18865671`
- Technical note DOI (concept): pending/not captured
- Software DOI (version): pending first software publication
- Software DOI (concept): pending first software publication

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
- [x] Technical note PDF generated (`docs/technical_note.pdf`)
- [x] Zenodo PDF metadata template added (`docs/zenodo_pdf_publication_metadata.md`)
- [x] Zenodo publish runbook added (`docs/zenodo_publish_runbook.md`)
- [ ] Annotated Git tag created and pushed
- [ ] GitHub release published
- [x] Zenodo technical-note publication draft reviewed and published
- [x] PDF DOI wired into `.zenodo.json`
- [ ] Zenodo software draft reviewed and published
- [ ] PDF/software bidirectional related identifiers verified
- [ ] DOI badge and links inserted into README
