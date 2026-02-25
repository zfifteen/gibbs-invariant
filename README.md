# The Gibbs Invariant

This repository develops two connected theorems under the shared framework **The Gibbs Invariant**.

## Documents

1. `docs/theorem_1_energy_invariant.md`  
   Brief statement of Theorem 1: for truncated Fourier reconstructions of jump-discontinuous signals, about 89% of squared error remains concentrated in shrinking edge neighborhoods (an energy concentration invariant), with an engineering crossover near \(N \approx 26\) for a unit square wave.

2. `docs/theorem_1_technical_exposition.md`  
   Detailed technical development of Theorem 1, including harmonic energy accounting, phase-coherence mechanism at discontinuities, crossover interpretation, decision-rule implications, and falsification criteria.

3. `docs/theorem_2_radius_invariant.md`  
   Brief statement of Theorem 2 in epicycle form: for true jumps, the cumulative circle-radius budget keeps growing and adds an approximately constant amount per doubling, while smooth signals show decaying increments.

4. `docs/theorem_2_technical_exposition.md`  
   Full derivation and exposition of Theorem 2: formal definition of the radius budget \(R(N)\), square-wave asymptotics, constant doubling increment \((2/\pi)\ln 2\), contrast cases (triangle/smoothed signals), mechanism, and applied decision rule.

5. `docs/industry/gibbs_industrial_implications.docx.md`  
   Industrial implications report connecting both theorems to practical systems (MRI, audio/video compression, CFD, telecom, ML, instrumentation, control), with strategy guidance based on the \(N_1\) crossover and edge-aware/localized methods.

## Suggested Reading Order

1. `docs/theorem_1_energy_invariant.md`
2. `docs/theorem_2_radius_invariant.md`
3. `docs/theorem_1_technical_exposition.md`
4. `docs/theorem_2_technical_exposition.md`
5. `docs/industry/gibbs_industrial_implications.docx.md`
