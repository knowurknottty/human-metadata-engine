#!/usr/bin/env bash
# Identity Resonance — one-command deploy.
#
#   ./deploy.sh            # install mandatory ephemeris, run tests, start on :8000
#   PORT=3000 ./deploy.sh  # custom port
#   ./deploy.sh --no-test  # skip the test suite
set -euo pipefail
cd "$(dirname "$0")"

echo "== Identity Resonance deploy =="

# Mandatory production ephemeris: pin the extension before tests or serving.
python3 -m pip install --require-hashes --no-cache-dir -r requirements.txt
python3 -c "import swisseph; print('pyswisseph: exact ephemeris available')"

if [[ "${1:-}" != "--no-test" ]]; then
  echo "== Running test suite =="
  python3 tools/run_tests.py --quiet
fi

echo "== Starting server on port ${PORT:-8000} =="
exec python3 webapp/server.py
