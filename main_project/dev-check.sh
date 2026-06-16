#!/usr/bin/env bash
set -euo pipefail

if [[ ! -x ".venv/bin/python" ]]; then
  echo "Missing .venv. Create it first:"
  echo "  python -m venv .venv && source .venv/bin/activate && pip install -r requirements-dev.txt"
  exit 1
fi

echo "[1/3] Running pytest..."
.venv/bin/pytest -q

echo "[2/3] Running Python compile check..."
.venv/bin/python -m compileall app tests >/dev/null

echo "[3/3] Running dashboard JS syntax check..."
node --check "hardware_arm/unified_secure_dashboard/main.js"
node --check "hardware_arm/unified_secure_dashboard/preload.js"
node --check "hardware_arm/unified_secure_dashboard/renderer/renderer.js"
node --check "hardware_arm/unified_secure_dashboard/modules/stocks/service.js"

echo "All checks passed."
