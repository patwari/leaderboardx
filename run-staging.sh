#!/bin/bash
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"

pushd "$ROOT/services/backend" >/dev/null
./run-staging.sh
popd >/dev/null

pushd "$ROOT/services/frontend" >/dev/null
./run-staging.sh
popd >/dev/null

echo "Staging backend: http://localhost:7010 (DB 7015, Redis 7016)"
echo "Staging frontend: http://localhost:7011"
