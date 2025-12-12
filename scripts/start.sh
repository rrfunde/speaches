#!/bin/bash
# Speaches Server Startup Script
# Usage: ./scripts/start.sh [local|runpod]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Default to local if no argument provided
ENV_TYPE="${1:-local}"

case "$ENV_TYPE" in
    local)
        ENV_FILE="config/local.env"
        echo "Starting Speaches server for Apple Silicon M4 (CPU mode)..."
        ;;
    runpod|gpu)
        ENV_FILE="config/runpod.env"
        echo "Starting Speaches server for RunPod (CUDA GPU mode)..."
        ;;
    *)
        echo "Usage: $0 [local|runpod]"
        echo "  local  - Apple Silicon M4 (CPU mode)"
        echo "  runpod - RunPod NVIDIA GPU (CUDA mode)"
        exit 1
        ;;
esac

# Check if env file exists
if [ ! -f "$ENV_FILE" ]; then
    echo "Error: Environment file $ENV_FILE not found"
    exit 1
fi

# Activate virtual environment
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
else
    echo "Error: Virtual environment not found. Run 'uv sync' first."
    exit 1
fi

# Load environment variables
set -a
source "$ENV_FILE"
set +a

echo "Configuration loaded from $ENV_FILE"
echo "Server will be available at http://${UVICORN_HOST}:${UVICORN_PORT}"
echo "API docs at http://${UVICORN_HOST}:${UVICORN_PORT}/docs"
echo ""

# Start the server
exec uvicorn --factory --host "$UVICORN_HOST" --port "$UVICORN_PORT" speaches.main:create_app
