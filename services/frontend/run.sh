#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
docker compose -f "$SCRIPT_DIR/docker-compose.yml" down
docker compose -p lx-frontend -f "$SCRIPT_DIR/docker-compose.yml" up --build --detach --remove-orphans
echo "Running frontend on http://localhost:9020"
