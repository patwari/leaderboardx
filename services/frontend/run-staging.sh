#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
docker compose -f "$SCRIPT_DIR/docker-compose.staging.yml" down
docker compose -p lx-fe-staging -f "$SCRIPT_DIR/docker-compose.staging.yml" up --build --detach --remove-orphans
echo "Staging frontend on http://localhost:7011"
