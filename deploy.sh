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
python3 -m pip install --no-cache-dir -r requirements.txt
python3 -c "import swisseph; print('pyswisseph: exact ephemeris available')"

if [[ "${1:-}" != "--no-test" ]]; then
  echo "== Running test suite =="
  python3 tests/test_pythagorean.py >/dev/null
  python3 tests/test_extended.py   >/dev/null
  python3 tests/test_final.py      >/dev/null
  python3 tests/test_analytics.py  >/dev/null
  python3 tests/test_symbolic_roadmap.py >/dev/null
  python3 tests/test_unicode_pipeline_integration.py >/dev/null
  python3 tests/test_integrated_prototypes.py >/dev/null
  python3 tests/test_symbolic_contract.py >/dev/null
  python3 tests/test_web_symbolic_surface.py >/dev/null
  python3 tests/test_ephemeris_packaging.py >/dev/null
  python3 tests/test_birth_validation.py >/dev/null
  python3 tests/test_reference_population.py >/dev/null
  python3 tests/test_web_hardening.py >/dev/null
  python3 tests/test_api_birth_contract.py >/dev/null
  python3 tests/test_build_revision.py >/dev/null
  python3 tests/test_sigil.py >/dev/null
  echo "All test suites passed."
fi

echo "== Starting server on port ${PORT:-8000} =="
exec python3 webapp/server.py
