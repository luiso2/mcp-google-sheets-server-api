@echo off
echo Starting MCP Google Sheets HTTP API Server...
echo.
echo The API will be available at http://localhost:8080
echo API Documentation: http://localhost:8080/docs
echo.

REM Set environment variables
set SERVICE_ACCOUNT_PATH=%~dp0credentials\service-account.json
set API_KEYS_FILE=%~dp0config\api_keys.json
set DRIVE_FOLDER_ID=1HhXICyqTYS7PQ-_y2QUkLHwaaZCILQRQ

REM Check if virtual environment exists
if exist .venv (
    echo Using existing virtual environment...
    call .venv\Scripts\activate
) else (
    echo Creating virtual environment...
    python -m venv .venv
    call .venv\Scripts\activate
    echo Installing dependencies...
    pip install -e .
)

REM Run the HTTP API server
echo.
echo Starting server...
python -m mcp_google_sheets.api --host 0.0.0.0 --port 8080

pause