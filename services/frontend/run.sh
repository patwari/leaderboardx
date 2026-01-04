#!/bin/bash

# Build and run the frontend console independently
set -e

echo "Building and starting LeaderboardX Console..."

docker compose down
docker compose build
docker compose up --detach --remove-orphans

echo "Frontend console is running on http://localhost:8010"
