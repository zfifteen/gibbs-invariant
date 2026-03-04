# Documentation

This directory contains technical documentation for the Gibbs invariants.

## Contents

### Technical Note

**`technical_note.tex`** - Comprehensive technical note titled "Two Computable Invariants for Fourier Approximation of Piecewise-Smooth Signals" by Big D (March 2026).

This LaTeX document provides:
- Formal statements of both invariants with closed-form constants
- Energy concentration invariant: $C(1) \approx 0.89$ for unit square wave
- Radius budget invariant: $\Delta R \to (2/\pi)\ln 2 \approx 0.4413$
- Crossover criterion: $N_1 \approx 26$ harmonics
- Complete numerical verification methodology
- Operational decision rules for adaptive signal processing
- Three appendices with mathematical derivations

### Individual Theorem Documentation

- `theorem_1_energy_invariant.md` - Overview of the energy concentration invariant
- `theorem_1_proof_sketch.md` - Mathematical proof outline
- `theorem_1_technical_exposition.md` - Technical details and analysis
- `theorem_2_radius_invariant.md` - Overview of the radius budget invariant
- `theorem_2_technical_exposition.md` - Technical details and derivations

### Industry Documentation

The `industry/` subdirectory contains engineering-focused documentation for practitioners.

## Building the Technical Note

### Prerequisites

You'll need a LaTeX distribution installed:
- **macOS**: MacTeX (`brew install --cask mactex`)
- **Linux**: TeX Live (`sudo apt-get install texlive-full`)
- **Windows**: MiKTeX or TeX Live

### Compilation

```bash
# Change to docs directory
cd docs

# Compile the technical note (runs pdflatex twice for references)
pdflatex technical_note.tex
pdflatex technical_note.tex

# Clean up auxiliary files
rm -f technical_note.aux technical_note.log technical_note.out
```

Alternatively, using the provided Makefile:

```bash
cd docs
make                 # Build PDF
make clean          # Remove auxiliary files
make cleanall       # Remove all generated files including PDF
```

### Output

The compilation produces `technical_note.pdf`, a publication-ready document suitable for:
- Academic submission (6-8 pages body + appendices)
- Technical reference material
- Preprint server posting (arXiv, etc.)

## Verification

All numerical claims in the technical note can be verified by running:

```bash
python3 gibbs_invariant.py
```

This generates:
- Console output with verification tables
- Plots saved to `assets/` directory
- Numerical confirmation of all stated constants

## Citation Format

If referencing this work:

```bibtex
@techreport{bigd2026gibbs,
  author = {Big D},
  title = {Two Computable Invariants for Fourier Approximation of Piecewise-Smooth Signals},
  institution = {GitHub},
  year = {2026},
  month = {March},
  url = {https://github.com/zfifteen/gibbs-invariant}
}
```

## Related Resources

- Main repository: [github.com/zfifteen/gibbs-invariant](https://github.com/zfifteen/gibbs-invariant)
- Reference implementation: `gibbs_invariant.py`
- Mission statement: `MISSION.md`
- Contributing guidelines: `CONTRIBUTING.md`
