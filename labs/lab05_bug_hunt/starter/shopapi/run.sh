#!/usr/bin/env bash
# Start ShopAPI on http://localhost:8000 (macOS, Linux, WSL2, Codespaces).
# Resets the demo data every time you start it.
set -euo pipefail
cd "$(dirname "$0")"

if command -v uv >/dev/null 2>&1; then
  PY=(uv run python)
elif command -v python >/dev/null 2>&1; then
  PY=(python)
else
  PY=(python3)
fi

"${PY[@]}" seed.py
echo "ShopAPI: http://localhost:8000/docs   (stop with Ctrl+C)"
exec "${PY[@]}" -m uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000
