#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/run_demo.sh [--skip-pipeline] [--no-launch] [--help]

Options:
  --skip-pipeline  Skip experiments/run_all.py refresh step.
  --no-launch      Run setup/pipeline only, do not start the web app.
  --help           Show this help message.
EOF
}

SKIP_PIPELINE=0
NO_LAUNCH=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --skip-pipeline)
      SKIP_PIPELINE=1
      shift
      ;;
    --no-launch)
      NO_LAUNCH=1
      shift
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="$ROOT_DIR/.venv/bin/python3.14"

if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="$ROOT_DIR/.venv/bin/python3"
fi

if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "No project venv Python found. Expected $ROOT_DIR/.venv/bin/python3.14 or python3" >&2
  exit 1
fi

if [[ "$SKIP_PIPELINE" -eq 0 ]]; then
  echo "[run_demo] Refreshing artifacts with experiments/run_all.py"
  "$PYTHON_BIN" "$ROOT_DIR/experiments/run_all.py"
fi

if [[ "$NO_LAUNCH" -eq 1 ]]; then
  echo "[run_demo] Setup complete. Skipping app launch due to --no-launch."
  exit 0
fi

echo "[run_demo] Starting demo app on http://127.0.0.1:8050"
cd "$ROOT_DIR"
exec "$PYTHON_BIN" -m demo.app
