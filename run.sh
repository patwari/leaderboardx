#!/bin/bash

# LeaderboardX - Docker Compose wrapper
# Simple wrapper around docker-compose for convenience

set -e

# Helper functions
log_info() {
    echo "[INFO] $1"
}

log_success() {
    echo "[SUCCESS] $1"
}

log_error() {
    echo "[ERROR] $1"
}

# Check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Main commands
case "${1:-}" in
    "up"|"start"|"")
        check_docker
        log_info "Starting LeaderboardX development stack..."
        docker-compose up --build -d
        log_success "Stack started successfully"
        log_info "API available at: http://localhost:8000"
        log_info "Health check: http://localhost:8000/health"
        log_info "API docs: http://localhost:8000/docs"
        ;;
    "down"|"stop")
        log_info "Stopping LeaderboardX stack..."
        docker-compose down
        log_success "Stack stopped"
        ;;
    "logs")
        docker-compose logs -f app
        ;;
    "restart")
        log_info "Restarting LeaderboardX stack..."
        docker-compose down
        docker-compose up --build -d
        log_success "Stack restarted"
        ;;
    "clean")
        log_info "Cleaning up containers and images..."
        docker-compose down --volumes --remove-orphans
        docker-compose build --no-cache
        log_success "Cleanup complete"
        ;;
    *)
        echo "LeaderboardX Development Commands:"
        echo "  ./run.sh [up|start]  - Start the development stack (default)"
        echo "  ./run.sh down|stop   - Stop the development stack"
        echo "  ./run.sh logs        - Show application logs"
        echo "  ./run.sh restart     - Restart the stack"
        echo "  ./run.sh clean       - Clean rebuild everything"
        echo ""
        echo "Or use docker-compose directly:"
        echo "  docker-compose up --build -d"
        echo "  docker-compose down"
        echo "  docker-compose logs -f app"
        ;;
esac