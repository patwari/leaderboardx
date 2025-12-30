#!/bin/bash

# Simple build and run script
set -e

echo "Building and starting LeaderboardX..."

# Build and run with docker-compose
docker-compose down
docker-compose build
docker-compose up -d

echo "LeaderboardX is running on http://localhost:8000"
echo "health is running on http://localhost:8000/health"