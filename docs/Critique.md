# Critique and validation

## Theorem 2 — radius budget
Claim: docs/theorem_2_radius_invariant.md
Assumption: periodic f with jump(s) and bounded variation.
Conclusion: R(N)=sum_{k<=N}|c_k| diverges like const*log N; for the unit square wave, doubling increment limit (2/pi) log 2.
Proof outline: jump -> Fourier coefficients decay like |c_k| ~ K/k; harmonic numbers.

## Theorem 1 — energy concentration
Claim: docs/theorem_1_energy_invariant.md
Definition: Gibbs zone width pi/(2N+1) (factor 1.0) around each discontinuity; metric computed in gibbs_invariant.py via energy_concentration_fraction(...).
Classical: Gibbs scaling/overshoot follows from the Dirichlet kernel.
Needs formal closure: specify function class + truncation definition + zone definition, and prove
lim_{N->infty} (zone L2 error)/(total L2 error) = C(zone width factor).
Note: C depends on the zone-width factor; show robustness via zone_width_factor in {0.5, 1, 2}.

## Crossover N1
Claim (square wave): N1 ≈ 26 computed in gibbs_invariant.py.
Interpretation: diagnostic threshold; depends on RMS normalization.

## Minimal precision upgrades
1. Add explicit function-class assumptions (bounded variation / piecewise C1) to both theorem docs.
2. State normalization / truncation conventions.
3. Add one additional discontinuous example beyond the square wave.
