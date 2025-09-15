# Setup Guide for MCP Google Sheets Server API

This guide will help you set up the MCP Google Sheets Server API for development and usage.

## Prerequisites

- Python 3.10 or higher
- Google Cloud Platform account
- Google Drive and Google Sheets APIs enabled

## Installation

### Option 1: Using uvx (Recommended for users)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh  # macOS/Linux
# or
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"  # Windows

# Run the server
uvx mcp-google-sheets@latest
```

### Option 2: Development Setup

```bash
# Clone the repository
git clone https://github.com/luiso2/mcp-google-sheets-server-api.git
cd mcp-google-sheets-server-api

# Install dependencies using uv
uv sync

# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate  # Windows
```

## Configuration

### 1. Google Cloud Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - Google Drive API
   - Google Sheets API
4. Create a Service Account:
   - Go to IAM & Admin > Service Accounts
   - Click "Create Service Account"
   - Download the JSON key file
   - Save it as `credentials/service-account.json`

### 2. Environment Variables

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` with your actual values:

```env
SERVICE_ACCOUNT_PATH=./credentials/service-account.json
DRIVE_FOLDER_ID=your-actual-drive-folder-id
```

### 3. Claude Desktop Configuration

Copy and modify the Claude configuration:

```bash
cp claude_config.json ~/.config/claude/claude_desktop_config.json  # Linux/macOS
# or copy to appropriate location on Windows
```

Update the paths and folder ID in the configuration file.

## Usage

### Running the MCP Server

```bash
# Development mode
python -m mcp_google_sheets

# API server mode
python -m mcp_google_sheets.api.http_server
```

### Running with Docker

```bash
# Build the image
docker build -t mcp-google-sheets .

# Run with docker-compose
docker-compose up
```

## Testing

```bash
# Test authentication
python test_auth.py

# Test client example
python client_example.py
```

## Troubleshooting

### Common Issues

1. **Authentication Error**: Make sure your service account JSON file is correctly placed and the path is correct in your environment variables.

2. **Permission Denied**: Ensure your service account has access to the Google Drive folder you're trying to use.

3. **API Not Enabled**: Verify that Google Drive API and Google Sheets API are enabled in your Google Cloud project.

### Getting Help

If you encounter issues:

1. Check the logs for detailed error messages
2. Verify your Google Cloud setup
3. Ensure all environment variables are correctly set
4. Open an issue on GitHub if the problem persists

## Development

### Project Structure

```
src/mcp_google_sheets/
├── __init__.py          # Main entry point
├── __main__.py          # CLI entry point
├── server.py            # MCP server implementation
└── api/                 # HTTP API implementation
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.