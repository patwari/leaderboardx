#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
docker compose -f "$SCRIPT_DIR/docker-compose.yml" down
docker compose -p lx-backend -f "$SCRIPT_DIR/docker-compose.yml" up --build --detach --remove-orphans
echo "Running backend on http://localhost:9010 (Postgres 9011, Redis 9012)"
