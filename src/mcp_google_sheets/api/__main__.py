"""
Entry point for running the HTTP API server
"""

import argparse
from .http_server import start_server


def main():
    parser = argparse.ArgumentParser(description='MCP Google Sheets HTTP API Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=8080, help='Port to bind to (default: 8080)')
    parser.add_argument('--reload', action='store_true', help='Enable auto-reload for development')

    args = parser.parse_args()

    print(f"Starting MCP Google Sheets HTTP API server on {args.host}:{args.port}")
    print(f"API documentation will be available at http://{args.host}:{args.port}/docs")

    start_server(host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    main()