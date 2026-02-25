# The Gibbs Invariant: Theorem 1 (Energy Concentration Invariant)

Reconstruction error in a truncated Fourier series does not spread evenly across the waveform; instead, a fixed fraction of roughly 89% of all squared error concentrates inside a vanishingly narrow zone around each discontinuity, and this fraction holds steady regardless of how many harmonics you add.

This means the Gibbs phenomenon is not merely a local amplitude artifact (the well-known 9% overshoot). It is an energy-trapping structure: nearly nine-tenths of everything the series still "gets wrong" is permanently locked into shrinking neighborhoods around the edges.

What makes this non-obvious is the self-similar scaling. Each new harmonic shrinks the error zone by a factor proportional to 1/N, but simultaneously increases the error density inside that zone by the same factor. The product stays constant, producing a scale-invariant error architecture that persists from the first harmonic to the thousandth.

The mechanism is coherent superposition of the missing harmonics. At a discontinuity, every absent harmonic is in phase (constructive interference), so their collective absence hits hard. In smooth regions, the absent harmonics have scattered phases and partially cancel each other out, making their absence nearly invisible.

This implies a concrete crossover: around the 26th harmonic for a unit square wave, the fixed pointwise Gibbs error surpasses the global RMS error. Beyond that threshold, adding more global harmonics delivers less than 11% of the remaining error reduction to the 95%+ of the domain that is smooth.

The practical consequence is a decision boundary that standard Fourier analysis does not flag. Before N_c, adding harmonics improves the whole waveform. After N_c, you are pouring bandwidth almost entirely into a losing battle at the edges, and should switch to a localized repair strategy instead.
