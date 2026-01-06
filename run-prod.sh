#!/bin/bash
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"

pushd "$ROOT/services/backend" >/dev/null
./run-prod.sh
popd >/dev/null

pushd "$ROOT/services/frontend" >/dev/null
./run-prod.sh
popd >/dev/null

echo "Prod backend: http://localhost:9010"
echo "Prod frontend: http://localhost:9011"
