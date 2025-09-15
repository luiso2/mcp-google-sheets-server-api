#!/bin/bash

echo "Starting MCP Google Sheets HTTP API Server..."
echo ""
echo "The API will be available at http://localhost:8080"
echo "API Documentation: http://localhost:8080/docs"
echo ""

# Set environment variables
export SERVICE_ACCOUNT_PATH="$(pwd)/credentials/service-account.json"
export API_KEYS_FILE="$(pwd)/config/api_keys.json"
export DRIVE_FOLDER_ID="1HhXICyqTYS7PQ-_y2QUkLHwaaZCILQRQ"

# Check if virtual environment exists
if [ -d ".venv" ]; then
    echo "Using existing virtual environment..."
    source .venv/bin/activate
else
    echo "Creating virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    echo "Installing dependencies..."
    pip install -e .
fi

# Run the HTTP API server
echo ""
echo "Starting server..."
python -m mcp_google_sheets.api --host 0.0.0.0 --port 8080