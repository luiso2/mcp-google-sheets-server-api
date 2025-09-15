@echo off
echo ========================================
echo MCP Google Sheets Server
echo ========================================
echo.

REM Configurar las variables de entorno
set SERVICE_ACCOUNT_PATH=C:\MCPS\mcp-google-sheets\credentials\service-account.json
set DRIVE_FOLDER_ID=1HhXICyqTYS7PQ-_y2QUkLHwaaZCILQRQ

echo Configuracion:
echo - Service Account: %SERVICE_ACCOUNT_PATH%
echo - Drive Folder ID: %DRIVE_FOLDER_ID%
echo - Client Email: sheet-de-esencial-pack@absolute-codex-469116-k9.iam.gserviceaccount.com
echo.
echo Iniciando servidor...
echo ========================================
echo.

cd /d C:\MCPS\mcp-google-sheets
uv run mcp-google-sheets

pause
