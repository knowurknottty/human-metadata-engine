#!/usr/bin/env bash
# Identity Resonance — one-command deploy.
#
#   ./deploy.sh            # install optional deps, run tests, start on :8000
#   PORT=3000 ./deploy.sh  # custom port
#   ./deploy.sh --no-test  # skip the test suite
set -euo pipefail
cd "$(dirname "$0")"

echo "== Identity Resonance deploy =="

# Optional dependency: exact astrology/Human Design. The app degrades
# gracefully to deterministic stub charts without it.
if python3 -c "import swisseph" 2>/dev/null; then
  echo "pyswisseph: already installed (exact ephemeris)"
elif pip3 install pyswisseph 2>/dev/null; then
  echo "pyswisseph: installed (exact ephemeris)"
else
  echo "pyswisseph: unavailable — continuing with stub charts (reduced accuracy)"
fi

if [[ "${1:-}" != "--no-test" ]]; then
  echo "== Running test suite =="
  python3 tests/test_pythagorean.py >/dev/null
  python3 tests/test_extended.py   >/dev/null
  python3 tests/test_final.py      >/dev/null
  python3 tests/test_analytics.py  >/dev/null
  echo "All 118 tests passed."
fi

echo "== Starting server on port ${PORT:-8000} =="
exec python3 webapp/server.py
