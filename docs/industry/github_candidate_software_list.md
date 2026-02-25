# Build a list of good candidate software that is on github - this would make it even easier for me to get started.

Here is a concrete list of good candidates on GitHub that line up well with your invariants and are realistically hackable.

### Image codecs and tools

- **libjpeg‑turbo**
    - Repo: https://github.com/libjpeg-turbo/libjpeg-turbo
    - Why good: Drop‑in JPEG, C code, widely used, great for adding edge‑aware metrics or post‑processing.
- **mozjpeg**
    - Repo: https://github.com/mozilla/mozjpeg
    - Why good: JPEG encoder tuned for perceptual quality; natural place to add a two‑budget (edge/smooth) metric and see if RD‑optimization changes.
- **libpng**
    - Repo: https://github.com/glennrp/libpng
    - Why good: Simple image path, good for experimenting with Gibbs‑aware filtering or analysis tools rather than core compression.
- **ImageMagick**
    - Repo: https://github.com/ImageMagick/ImageMagick
    - Why good: High‑level wrapper over many codecs; easy to plug in your metrics and filters, then batch‑test lots of images.
- **libwebp**
    - Repo: https://github.com/webmproject/libwebp
    - Why good: Modern image codec; you can test whether explicit edge handling or two‑budget metrics help at equal bitrates.
- **libheif (HEIF/AVIF)**
    - Repo: https://github.com/strukturag/libheif[^1]
    - Why good: HEIF/AVIF encoder/decoder stack; good place to test edge‑aware RD or side‑channel edge encoding.


### Audio codecs

- **Opus reference implementation (libopus)**
    - Repo: https://github.com/xiph/opus[^2][^3]
    - Why good: Modern audio codec, explicit transient handling; ideal to replace the transient detector with an $N_1$ / radius‑style test and measure pre‑echo changes.
- **LAME MP3 encoder**
    - Repo: https://github.com/RoRoche/lame (active mirror of LAME)
    - Why good: Classic psychoacoustic pipeline; you can tune low‑pass / windowing / bit‑allocation based on Gibbs‑zone awareness.


### Neural image models / compression

- **CompressAI (learned image compression)**
    - Repo: https://github.com/InterDigitalInc/CompressAI
    - Why good: Standard PyTorch baselines; you can drop in a two‑budget loss (edge vs smooth) and compare reconstructions at equal bitrate.
- **OpenMMLab image compression (mmediting / mmdetection side projects)**
    - Example: https://github.com/open-mmlab/mmediting
    - Why good: Lots of image‑to‑image models; easy to plug in your loss and edge‑zone diagnostics.


### MRI reconstruction

- **direct (Deep learning framework for MRI reconstruction)**
    - Repo: https://github.com/NKI-AI/direct[^4]
    - Why good: Modular; you can add a Gibbs‑zone detector (via coefficient decay) and compare global apodization vs edge‑localized correction.
- **BART (Berkeley Advanced Reconstruction Toolbox)**
    - Repo: https://github.com/mrirecon/bart
    - Why good: Widely used MRI recon toolbox; good for adding Gibbs‑aware diagnostics and localized boundary repair modes.


### CFD / PDE codes

- **OpenFOAM (community mirror)**
    - Repo: https://github.com/OpenFOAM/OpenFOAM-11 (or latest mainline)[^5]
    - Why good: Heavier, but has shock‑capturing; you can prototype an $N_1$‑style criterion for switching schemes near shocks.
- **opensbli**
    - Repo: https://github.com/opensbli/opensbli[^6]
    - Why good: Framework for finite difference solvers; good place to test spectral vs non‑spectral switching driven by your invariants.


### Educational / Fourier visualization

- **fourier-drawing (example JS epicycle demo)**
    - Repo: https://github.com/jesseyb/root-two-fourier (or any of several “fourier drawing” repos)
    - Why good: Ideal sandbox to implement your radius‑budget and per‑doubling increment test directly and demonstrate Theorem 2 visually.

If you want the lowest‑friction starting trio from this list, I would suggest:

- libjpeg‑turbo or mozjpeg,
- xiph/opus,
- InterDigitalInc/CompressAI.

All three are on GitHub, actively maintained, and have clear benchmark stories for “before and after Gibbs‑aware patch.”

<div align="center">⁂</div>

[^1]: https://github.com/strukturag/libheif

[^2]: https://github.com/xiph/opus

[^3]: http://github.com/xiph/opus

[^4]: https://github.com/NKI-AI/direct

[^5]: https://www.openfoam.com

[^6]: http://github.com/opensbli/opensbli

