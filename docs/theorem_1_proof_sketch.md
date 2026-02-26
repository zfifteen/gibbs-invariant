# Theorem 1 Proof Sketch: Energy Concentration Limit

This note provides the proof bridge for Theorem 1:
\[
F_N(\alpha)=\frac{E_{\text{zone}}(N,\alpha)}{E_{\text{tot}}(N)}\to C(\alpha)\in(0,1),
\]
under the repository assumptions:

- \(f\) is \(2\pi\)-periodic and piecewise \(C^1\) (BV is sufficient),
- \(f\) has finitely many jumps \(\{(x_j,\Delta_j)\}\),
- truncation convention is encoded by \(K(N)\) (odd-harmonic vs full-harmonic).

## 1) Global Fourier tail energy scales as \(1/K(N)\)

For BV functions with jumps, standard coefficient asymptotics give
\[
\hat f(k)=\sum_j \frac{\Delta_j}{2\pi i k}e^{-ikx_j}+O\!\left(\frac{1}{k^2}\right),\quad |k|\to\infty.
\]
By Parseval, the truncation error energy is
\[
E_{\text{tot}}(N)=\sum_{|k|>N}|\hat f(k)|^2.
\]
Substituting the asymptotic and summing \(\sum_{k>N}k^{-2}\sim 1/N\) yields
\[
E_{\text{tot}}(N)=\frac{C_{\text{tot}}}{K(N)}+o\!\left(\frac{1}{K(N)}\right),
\]
where \(C_{\text{tot}}\) depends on jump data and normalization constants, but not on \(N\). Smooth-background contributions are higher order.

## 2) Near each jump, error follows a universal scaled Gibbs profile

Using the Dirichlet-kernel representation
\[
S_N f(x)=\frac{1}{2\pi}\int_{-\pi}^{\pi}f(y)\,D_N(x-y)\,dy,
\]
decompose \(f\) into jump part + smooth remainder. Standard Gibbs scaling gives
\[
e_N(x)=f(x)-S_N f(x)=\sum_j \Delta_j\,G_N(x-x_j)+\text{(smaller remainder)}.
\]
With local variable \(u=K(N)(x-x_j)\), the jump kernel has the scaling form
\[
G_N(x-x_j)\approx g(u),
\]
for a fixed profile \(g\) determined by the truncation convention. The profile is universal across the signal class; jump heights/locations enter only through \(\Delta_j,x_j\).

## 3) Zone energy and total energy share the same \(1/K(N)\) scale

The jump-zone half-width is
\[
w_N(\alpha)=\alpha\frac{\pi}{K(N)}.
\]
In each zone, substitute \(x=x_j+u/K(N)\), so \(dx=du/K(N)\). Then
\[
E_{\text{zone}}(N,\alpha)
=\sum_j\int_{|u|\le \alpha\pi}\left(\Delta_j g(u)+\text{small}\right)^2\frac{du}{K(N)}
=\frac{C_{\text{zone}}(\alpha)}{K(N)}+o\!\left(\frac{1}{K(N)}\right),
\]
with
\[
C_{\text{zone}}(\alpha)=\sum_j \Delta_j^2\int_{-\alpha\pi}^{\alpha\pi}g(u)^2\,du.
\]
Likewise
\[
E_{\text{tot}}(N)=\frac{C_{\text{tot}}}{K(N)}+o\!\left(\frac{1}{K(N)}\right),
\]
where (up to the same normalization convention)
\[
C_{\text{tot}}=\sum_j \Delta_j^2\int_{-\infty}^{\infty}g(u)^2\,du.
\]

## 4) Ratio convergence

Since numerator and denominator have the same leading-order scale,
\[
F_N(\alpha)=\frac{E_{\text{zone}}(N,\alpha)}{E_{\text{tot}}(N)}
\to
\frac{C_{\text{zone}}(\alpha)}{C_{\text{tot}}}
=C(\alpha)\in(0,1).
\]
Hence the limit is \(N\)-stable for fixed \(\alpha\), while depending on:

- \(\alpha\) (zone definition),
- truncation convention (through \(g\) and \(K(N)\)),
- jump data (with common \(\sum_j\Delta_j^2\)-type factors canceling in the ratio under the same normalization).

## Minimal theorem-grade bridge (repo usage)

To keep statements concise while theorem-grade:

1. state \(f\in BV\) with finitely many jumps,
2. cite coefficient asymptotics \(\Rightarrow E_{\text{tot}}(N)\sim C_{\text{tot}}/K(N)\),
3. cite Dirichlet-kernel Gibbs scaling \(\Rightarrow E_{\text{zone}}(N,\alpha)\sim C_{\text{zone}}(\alpha)/K(N)\),
4. conclude \(F_N(\alpha)\to C(\alpha)\).
