#!/bin/bash
# test-docker.sh - Optional Docker integration testing
# Usage: ./test-docker.sh

set -e  # Exit on error

echo "🐳 Starting Docker Integration Tests"
echo "===================================="

# Configuration
IMAGE_NAME="bgchof-test"
CONTAINER_NAME="bgchof-test-container"
PORT="5000"

# Cleanup function
cleanup() {
    echo ""
    echo "🧹 Cleaning up..."
    docker stop "$CONTAINER_NAME" 2>/dev/null || true
    docker rm "$CONTAINER_NAME" 2>/dev/null || true
    docker rmi "$IMAGE_NAME" 2>/dev/null || true
    echo "✅ Cleanup complete"
}

# Set trap to cleanup on exit
trap cleanup EXIT

# Build Docker image
echo ""
echo "📦 Building Docker image..."
docker build -t "$IMAGE_NAME" .

# Start container
echo ""
echo "🚀 Starting container..."
docker run -d -p "$PORT:$PORT" --name "$CONTAINER_NAME" "$IMAGE_NAME"

# Wait for container to be ready
echo ""
echo "⏳ Waiting for container to be ready..."
sleep 5

# Check if container is running
if ! docker ps | grep -q "$CONTAINER_NAME"; then
    echo "❌ Container failed to start"
    docker logs "$CONTAINER_NAME"
    exit 1
fi

# Run integration tests
echo ""
echo "🧪 Running integration tests..."
pytest tests/test_docker_integration.py -v -s

echo ""
echo "✅ All Docker integration tests passed!"

# Made with Bob
