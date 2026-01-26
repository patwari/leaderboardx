#!/bin/bash
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"

pushd "$ROOT/services/frontend" >/dev/null
./run.sh
popd >/dev/null

pushd "$ROOT/services/backend" >/dev/null
./run.sh
popd >/dev/null

echo "Running backend: http://localhost:9010 (DB 9011, Redis 9012)"
echo "Running frontend: http://localhost:9020"
