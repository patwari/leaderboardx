#!/bin/bash

# LeaderboardX - Cross-Platform Build and Run Script
# Supports: Linux, macOS (Intel/Silicon), Windows WSL

set -e  # Exit on any error

# Project configuration
PROJECT_NAME="leaderboardx"
VERSION="0.0.1"
IMAGE_NAME="${PROJECT_NAME}:${VERSION}"
CONTAINER_NAME="${PROJECT_NAME}-app"
PORT=8000

# Helper functions
log_info() {
    echo "[INFO] $1"
}

log_success() {
    echo "[SUCCESS] $1"
}

log_warning() {
    echo "[WARNING] $1"
}

log_error() {
    echo "[ERROR] $1"
}

# Detect platform for cross-platform support
detect_platform() {
    local arch=$(uname -m)
    local os=$(uname -s)
    
    case $os in
        "Linux")
            if [[ $arch == "x86_64" ]]; then
                echo "linux/amd64"
            elif [[ $arch == "aarch64" ]]; then
                echo "linux/arm64"
            else
                echo "linux/amd64"  # Default fallback
            fi
            ;;
        "Darwin")
            if [[ $arch == "arm64" ]]; then
                echo "linux/arm64"  # Apple Silicon
            else
                echo "linux/amd64"  # Intel Mac
            fi
            ;;
        *)
            echo "linux/amd64"  # Default for Windows WSL
            ;;
    esac
}

# Check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    log_success "Docker is running"
}

# Stop and remove existing container
cleanup_container() {
    if docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
        log_warning "Stopping existing container: $CONTAINER_NAME"
        docker stop "$CONTAINER_NAME" >/dev/null 2>&1
    fi
    
    if docker ps -aq -f name="$CONTAINER_NAME" | grep -q .; then
        log_warning "Removing existing container: $CONTAINER_NAME"
        docker rm "$CONTAINER_NAME" >/dev/null 2>&1
    fi
}

# Build Docker image
build_image() {
    local platform=$(detect_platform)
    
    log_info "Building Docker image for platform: $platform"
    log_info "Image: $IMAGE_NAME"
    
    docker build \
        --platform "$platform" \
        --tag "$IMAGE_NAME" \
        --tag "${PROJECT_NAME}:latest" \
        .
    
    if [ $? -eq 0 ]; then
        log_success "Docker image built successfully: $IMAGE_NAME"
    else
        log_error "Failed to build Docker image"
        exit 1
    fi
}

# Run the container
run_container() {
    log_info "Starting container: $CONTAINER_NAME"
    log_info "Port mapping: localhost:$PORT -> container:8000"
    
    docker run \
        --name "$CONTAINER_NAME" \
        --publish "$PORT:8000" \
        --env DEBUG=true \
        --env APP_NAME="LeaderboardX Development" \
        --env SECRET_KEY="dev-secret-key-change-in-production" \
        --detach \
        --restart unless-stopped \
        "$IMAGE_NAME"
    
    if [ $? -eq 0 ]; then
        log_success "Container started successfully"
        log_info "API available at: http://localhost:$PORT"
        log_info "Health check: http://localhost:$PORT/health"
        log_info "API docs: http://localhost:$PORT/docs"
        
        # Wait a moment and check if container is still running
        sleep 3
        if docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
            log_success "Container is running healthy"
        else
            log_error "Container failed to start properly"
            log_info "Checking container logs..."
            docker logs "$CONTAINER_NAME"
            exit 1
        fi
    else
        log_error "Failed to start container"
        exit 1
    fi
}

# Show container logs
show_logs() {
    log_info "Showing container logs (Ctrl+C to exit):"
    docker logs -f "$CONTAINER_NAME"
}

# Main execution
main() {
    log_info "LeaderboardX - Build and Run Script"
    log_info "Platform: $(uname -s) $(uname -m)"
    
    # Check prerequisites
    check_docker
    
    # Build and run
    cleanup_container
    build_image
    run_container
    
    # Ask if user wants to see logs
    echo
    read -p "Show container logs? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        show_logs
    else
        log_info "Container is running in the background"
        log_info "View logs with: docker logs -f $CONTAINER_NAME"
        log_info "Stop container with: docker stop $CONTAINER_NAME"
    fi
}

# Handle script arguments
case "${1:-}" in
    "logs")
        show_logs
        ;;
    "stop")
        log_info "Stopping container: $CONTAINER_NAME"
        docker stop "$CONTAINER_NAME" 2>/dev/null || log_warning "Container not running"
        ;;
    "clean")
        cleanup_container
        log_info "Removing image: $IMAGE_NAME"
        docker rmi "$IMAGE_NAME" 2>/dev/null || log_warning "Image not found"
        ;;
    "build")
        check_docker
        cleanup_container
        build_image
        ;;
    *)
        main
        ;;
esac