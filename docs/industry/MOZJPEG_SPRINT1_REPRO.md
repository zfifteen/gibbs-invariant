# mozjpeg Sprint-1 Instrumentation Reproduction

This document captures exactly how to reproduce the Sprint-1 `--gibbs-routing=off|log|on` instrumentation work that was implemented in a temp clone.

## Artifacts Captured In This Repo

- Patch file: `docs/industry/mozjpeg_sprint1_instrumentation.patch`
- Baseline benchmark table: `docs/industry/mozjpeg_sprint1_baseline.tsv`

The patch was generated from this mozjpeg commit:

- `0826579`

## What The Patch Adds

The patch introduces:

1. New `cjpeg` options:
- `--gibbs-routing=off|log|on`
- `-gibbs-routing off|log|on`

2. Sprint-1 instrumentation only (no behavior change yet):
- Luma block-level coefficient feature extraction in `jccoefct.c`
- Block classification into `smooth` / `mixed` / `edge`
- Summary logging in `log`/`on` modes

3. New header:
- `gibbs_routing.h`

Important: `on` currently logs routing decisions but does not alter the encode path yet.

## Reproduction Prerequisites

- `git`
- `cmake`
- C compiler toolchain

## Reproduce From Scratch

1. Clone mozjpeg and checkout the exact commit:

```bash
TMP_BASE=/tmp/gibbs-fast-win-repro
mkdir -p "$TMP_BASE"
cd "$TMP_BASE"
git clone https://github.com/mozilla/mozjpeg.git
cd mozjpeg
git checkout 0826579
```

2. Apply the captured patch:

```bash
git apply /Users/velocityworks/IdeaProjects/gibbs-invariant/docs/industry/mozjpeg_sprint1_instrumentation.patch
```

3. Configure and build:

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build -j8
```

4. Smoke test each mode:

```bash
mkdir -p test_runs
./build/cjpeg --gibbs-routing=off -quality 85 testimages/testorig.ppm > test_runs/off.jpg 2> test_runs/off.log
./build/cjpeg --gibbs-routing=log -quality 85 testimages/testorig.ppm > test_runs/log.jpg 2> test_runs/log.log
./build/cjpeg --gibbs-routing=on  -quality 85 testimages/testorig.ppm > test_runs/on.jpg  2> test_runs/on.log

sed -n '1,5p' test_runs/log.log
sed -n '1,6p' test_runs/on.log
```

Expected:
- `off` mode: no gibbs-routing summary lines
- `log` mode: summary lines printed
- `on` mode: summary lines plus note that routing is not yet enforced

## Reproduce Baseline Benchmark Table

The benchmark settings used for the captured baseline are:

- modes: `off`, `log`, `on`
- images:
  - `testimages/testorig.ppm`
  - `testimages/monkey16.ppm`
  - `testimages/vgl_5674_0098.bmp`
- encode args: `-quality 85 -optimize -progressive`
- runs per row: `40`

Run this:

```bash
OUTDIR=/tmp/gibbs-fast-win-repro/mozjpeg/bench_baseline
mkdir -p "$OUTDIR"
RUNS=40
IMAGES=(testimages/testorig.ppm testimages/monkey16.ppm testimages/vgl_5674_0098.bmp)
ARGS=(-quality 85 -optimize -progressive)

printf "mode\timage\truns\ttotal_real_s\tavg_ms\toutput_bytes\tedge_pct\tsmooth_pct\n" > "$OUTDIR/baseline.tsv"

for mode in off log on; do
  for img in "${IMAGES[@]}"; do
    base=$(basename "$img")
    outjpg="$OUTDIR/${mode}_${base}.jpg"
    outlog="$OUTDIR/${mode}_${base}.log"

    ./build/cjpeg --gibbs-routing="$mode" "${ARGS[@]}" "$img" > "$outjpg" 2> "$outlog"
    size=$(wc -c < "$outjpg" | tr -d ' ')

    real_s=$( /usr/bin/time -p zsh -c "for i in {1..$RUNS}; do ./build/cjpeg --gibbs-routing=$mode -quality 85 -optimize -progressive '$img' > /dev/null 2>/dev/null; done" 2>&1 | awk '/^real /{print $2}' )
    avg_ms=$(awk -v t="$real_s" -v n="$RUNS" 'BEGIN{printf "%.3f", (t/n)*1000.0}')

    edge_pct="NA"
    smooth_pct="NA"
    if [ "$mode" != "off" ]; then
      edge_pct=$(awk -F'edge_pct=' '/gibbs-routing mode=/{split($2,a," "); print a[1]}' "$outlog" | head -n1)
      smooth_pct=$(awk -F'smooth_pct=' '/gibbs-routing mode=/{print $2}' "$outlog" | head -n1)
    fi

    printf "%s\t%s\t%d\t%s\t%s\t%s\t%s\t%s\n" "$mode" "$base" "$RUNS" "$real_s" "$avg_ms" "$size" "$edge_pct" "$smooth_pct" >> "$OUTDIR/baseline.tsv"
  done
done

cat "$OUTDIR/baseline.tsv"
```

## Verification Against Captured Result

Compare your generated table to:

- `docs/industry/mozjpeg_sprint1_baseline.tsv`

Minor runtime variance is expected across machines, but mode behavior and output sizes should match for the same toolchain and options.
