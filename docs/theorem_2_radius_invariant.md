# The Gibbs Invariant: Theorem 2 (Radius Budget Invariant)

In this spinning-circle build-up, a true jump in the target shape shows up as a “circle-length budget” that never levels off, even though the drawn wave stays within the same height.

Most people focus on the edge ringing or on how each added wiggle gets smaller, but those clues look local and can be hard to compare across different signals.

Instead, add up the radii of all circles used so far, and watch how much that total grows when you double the number of circles.

For the classic square-like wave in the image, doubling the number of circles should keep adding almost the same extra total radius, about 0.44 of the flat-top level, even when you go from 50 to 100 circles.

The mechanism is that a jump forces many tiny fast circles whose sizes shrink slowly, so you need an ever-growing total radius that is then held in check by cancellation between circles.

If you repeat the same measurement for a triangle-like wave or any version of the square wave with even a small amount of smoothing, the extra total radius added per doubling should quickly shrink toward zero instead of staying roughly constant.

This would be proven wrong if, for a sharp square wave, the added total radius per doubling decays steadily with more circles rather than settling near a constant.

Decision rule: when the added total radius per doubling stays above about 0.2 of the waveform’s plateau level beyond a few dozen circles, treat the underlying signal as containing real jumps; otherwise treat it as continuous and expect edge ringing to fade much faster with more circles.