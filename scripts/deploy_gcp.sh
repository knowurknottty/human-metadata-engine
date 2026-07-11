#!/usr/bin/env bash
# Reproducible canary deployment for the GCP production VM.
#
# Required local prerequisites: authenticated gcloud, Docker on the VM, and a
# clean committed revision. This script intentionally does not open a public
# firewall port; use docs/cloudflare-tunnel-runbook.md before closing 8084.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PROJECT="${GCP_PROJECT:-biocapt}"
ZONE="${GCP_ZONE:-europe-west1-b}"
INSTANCE="${GCP_INSTANCE:-biocapt-ecosystem}"
REMOTE_DIR="${GCP_APP_DIR:-/home/knowurknot/apps/human-metadata-engine}"
REVISION="$(git rev-parse "${1:-HEAD}")"
SHORT_REVISION="${REVISION:0:12}"
IMAGE="human-metadata-engine:${SHORT_REVISION}"
CANARY_NAME="human-metadata-engine-canary"
PRODUCTION_NAME="human-metadata-engine"
ROLLBACK_NAME="human-metadata-engine-rollback-${SHORT_REVISION}"

ssh_vm() {
  gcloud compute ssh "$INSTANCE" --project="$PROJECT" --zone="$ZONE" --command="$1"
}

echo "Deploying $REVISION to $INSTANCE ($PROJECT/$ZONE)"
# Deployment is sourced exclusively from ``git archive $REVISION`` below, so
# unrelated local edits cannot accidentally reach the VM.

git archive --format=tar "$REVISION" | ssh_vm "tar -xf - -C '$REMOTE_DIR'"

ssh_vm "set -euo pipefail
cd '$REMOTE_DIR'
docker build --build-arg HME_BUILD_REVISION='$REVISION' -t '$IMAGE' .
docker rm -f '$CANARY_NAME' >/dev/null 2>&1 || true
docker run -d --name '$CANARY_NAME' --restart=no -p 127.0.0.1:8091:8080 '$IMAGE' >/dev/null
sleep 2
curl -fsS http://127.0.0.1:8091/api/health >/tmp/hme-canary-health.json
python3 - <<'PY'
import json
payload = json.load(open('/tmp/hme-canary-health.json'))
assert payload['ok'] and payload['reference_count'] >= 100 and not payload['reference_errors'], payload
PY
"

ssh_vm "set -euo pipefail
cd '$REMOTE_DIR'
docker stop '$PRODUCTION_NAME' >/dev/null
docker rename '$PRODUCTION_NAME' '$ROLLBACK_NAME'
if ! docker run -d --name '$PRODUCTION_NAME' --restart unless-stopped -p 8084:8080 '$IMAGE' >/dev/null; then
  docker rename '$ROLLBACK_NAME' '$PRODUCTION_NAME'
  docker start '$PRODUCTION_NAME' >/dev/null
  exit 1
fi
sleep 2
if ! curl -fsS http://127.0.0.1:8084/api/health >/tmp/hme-production-health.json; then
  docker rm -f '$PRODUCTION_NAME' >/dev/null
  docker rename '$ROLLBACK_NAME' '$PRODUCTION_NAME'
  docker start '$PRODUCTION_NAME' >/dev/null
  exit 1
fi
docker rm -f '$CANARY_NAME' >/dev/null
docker run --rm --user 0 -e HME_BUILD_REVISION='$REVISION' -v \"\$PWD/output:/app/output\" '$IMAGE' python3 tools/build_famous_people_index.py
docker run --rm --user 0 -v \"\$PWD/output:/app/output\" '$IMAGE' chown \$(id -u)\:\$(id -g) /app/output/famous_people.sqlite /app/output/famous_people_validation.json
cat /tmp/hme-production-health.json
"

echo "Deployment complete. Rollback container: $ROLLBACK_NAME"
