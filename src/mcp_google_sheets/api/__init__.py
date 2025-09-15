"""
HTTP API wrapper for MCP Google Sheets Server
Allows the MCP server to be accessed via REST API for non-Claude LLMs
"""

from .http_server import app, start_server

__all__ = ['app', 'start_server']