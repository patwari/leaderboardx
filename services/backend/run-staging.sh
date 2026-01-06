#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
docker compose -f "$SCRIPT_DIR/docker-compose.staging.yml" down
docker compose -p lx-be-staging -f "$SCRIPT_DIR/docker-compose.staging.yml" up --build --detach --remove-orphans
echo "Staging backend on http://localhost:7010 (Postgres 7015, Redis 7016)"
