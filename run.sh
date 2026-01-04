#!/bin/bash
set -e

# Build and start both backend and frontend containers

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"

pushd "$PROJECT_ROOT/services/backend" >/dev/null
./run.sh
popd >/dev/null

pushd "$PROJECT_ROOT/services/frontend" >/dev/null
./run.sh
popd >/dev/null

echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:8010"
