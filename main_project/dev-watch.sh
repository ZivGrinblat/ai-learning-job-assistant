#!/usr/bin/env bash
set -euo pipefail

if [[ ! -x ".venv/bin/ptw" ]]; then
  echo "Missing pytest-watch. Install with:"
  echo "  source .venv/bin/activate && pip install -r requirements-dev.txt"
  exit 1
fi

exec .venv/bin/ptw app tests -- -q
