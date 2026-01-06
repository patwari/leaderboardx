#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
docker compose -f "$SCRIPT_DIR/docker-compose.prod.yml" down
docker compose -p lx-be-prod -f "$SCRIPT_DIR/docker-compose.prod.yml" up --build --detach --remove-orphans
echo "Prod backend on http://localhost:9010"
