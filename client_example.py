#!/usr/bin/env python3
"""
Example client for MCP Google Sheets HTTP API
Demonstrates how to use the API from any LLM or application
"""

import requests
import json
from typing import List, Dict, Any, Optional


class MCPGoogleSheetsClient:
    """Client for interacting with MCP Google Sheets HTTP API"""

    def __init__(self, api_url: str, api_key: str):
        """
        Initialize the client

        Args:
            api_url: Base URL of the API (e.g., "http://localhost:8080")
            api_key: API key for authentication
        """
        self.api_url = api_url.rstrip('/')
        self.headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }

    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make HTTP request to the API"""
        url = f"{self.api_url}{endpoint}"

        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers)
            elif method == "POST":
                response = requests.post(url, json=data, headers=self.headers)
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            raise

    def health_check(self) -> Dict:
        """Check if the API is healthy"""
        return self._make_request("GET", "/health")

    def get_sheet_data(
        self,
        spreadsheet_id: str,
        sheet: str,
        range: Optional[str] = None,
        include_grid_data: bool = False
    ) -> Dict:
        """
        Get data from a specific sheet

        Args:
            spreadsheet_id: The ID of the spreadsheet
            sheet: The name of the sheet
            range: Optional cell range in A1 notation
            include_grid_data: Include cell formatting and metadata

        Returns:
            Sheet data
        """
        data = {
            "spreadsheet_id": spreadsheet_id,
            "sheet": sheet,
            "range": range,
            "include_grid_data": include_grid_data
        }
        return self._make_request("POST", "/tools/get_sheet_data", data)

    def get_sheet_formulas(
        self,
        spreadsheet_id: str,
        sheet: str,
        range: Optional[str] = None
    ) -> Dict:
        """Get formulas from a sheet"""
        data = {
            "spreadsheet_id": spreadsheet_id,
            "sheet": sheet,
            "range": range
        }
        return self._make_request("POST", "/tools/get_sheet_formulas", data)

    def update_cells(
        self,
        spreadsheet_id: str,
        sheet: str,
        range: str,
        data: List[List[Any]]
    ) -> Dict:
        """
        Update cells in a spreadsheet

        Args:
            spreadsheet_id: The ID of the spreadsheet
            sheet: The name of the sheet
            range: Cell range in A1 notation
            data: 2D array of values to update

        Returns:
            Update result
        """
        request_data = {
            "spreadsheet_id": spreadsheet_id,
            "sheet": sheet,
            "range": range,
            "data": data
        }
        return self._make_request("POST", "/tools/update_cells", request_data)

    def batch_update_cells(
        self,
        spreadsheet_id: str,
        updates: List[Dict[str, Any]]
    ) -> Dict:
        """Batch update multiple ranges"""
        data = {
            "spreadsheet_id": spreadsheet_id,
            "updates": updates
        }
        return self._make_request("POST", "/tools/batch_update_cells", data)

    def add_rows(
        self,
        spreadsheet_id: str,
        sheet: str,
        rows: List[List[Any]],
        append: bool = True
    ) -> Dict:
        """Add rows to a sheet"""
        data = {
            "spreadsheet_id": spreadsheet_id,
            "sheet": sheet,
            "rows": rows,
            "append": append
        }
        return self._make_request("POST", "/tools/add_rows", data)

    def create_spreadsheet(self, title: str) -> Dict:
        """Create a new spreadsheet"""
        data = {"title": title}
        return self._make_request("POST", "/tools/create_spreadsheet", data)

    def create_sheet(self, spreadsheet_id: str, title: str) -> Dict:
        """Create a new sheet in a spreadsheet"""
        data = {
            "spreadsheet_id": spreadsheet_id,
            "title": title
        }
        return self._make_request("POST", "/tools/create_sheet", data)

    def list_spreadsheets(self) -> Dict:
        """List all accessible spreadsheets"""
        return self._make_request("GET", "/tools/list_spreadsheets")

    def list_sheets(self, spreadsheet_id: str) -> Dict:
        """List all sheets in a spreadsheet"""
        return self._make_request("GET", f"/tools/list_sheets/{spreadsheet_id}")

    def share_spreadsheet(
        self,
        spreadsheet_id: str,
        email_addresses: List[str],
        role: str = "reader",
        send_notification: bool = True
    ) -> Dict:
        """Share a spreadsheet with email addresses"""
        data = {
            "spreadsheet_id": spreadsheet_id,
            "email_addresses": email_addresses,
            "role": role,
            "send_notification": send_notification
        }
        return self._make_request("POST", "/tools/share_spreadsheet", data)

    def rename_sheet(
        self,
        spreadsheet_id: str,
        old_name: str,
        new_name: str
    ) -> Dict:
        """Rename a sheet"""
        data = {
            "spreadsheet_id": spreadsheet_id,
            "old_name": old_name,
            "new_name": new_name
        }
        return self._make_request("POST", "/tools/rename_sheet", data)

    def copy_sheet(
        self,
        src_spreadsheet: str,
        src_sheet: str,
        dst_spreadsheet: str,
        dst_sheet: Optional[str] = None
    ) -> Dict:
        """Copy a sheet to another spreadsheet"""
        data = {
            "src_spreadsheet": src_spreadsheet,
            "src_sheet": src_sheet,
            "dst_spreadsheet": dst_spreadsheet,
            "dst_sheet": dst_sheet
        }
        return self._make_request("POST", "/tools/copy_sheet", data)


# Example usage for integration with LLMs
class LLMGoogleSheetsTools:
    """Wrapper for LLM tool calling"""

    def __init__(self, api_url: str, api_key: str):
        self.client = MCPGoogleSheetsClient(api_url, api_key)

    def get_tools_definition(self) -> List[Dict]:
        """Return OpenAI-compatible tools definition"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_sheet_data",
                    "description": "Get data from a Google Spreadsheet",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "spreadsheet_id": {"type": "string", "description": "The spreadsheet ID"},
                            "sheet": {"type": "string", "description": "The sheet name"},
                            "range": {"type": "string", "description": "Optional cell range"}
                        },
                        "required": ["spreadsheet_id", "sheet"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_cells",
                    "description": "Update cells in a Google Spreadsheet",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "spreadsheet_id": {"type": "string"},
                            "sheet": {"type": "string"},
                            "range": {"type": "string"},
                            "data": {"type": "array", "items": {"type": "array"}}
                        },
                        "required": ["spreadsheet_id", "sheet", "range", "data"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_spreadsheet",
                    "description": "Create a new Google Spreadsheet",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "Title of the spreadsheet"}
                        },
                        "required": ["title"]
                    }
                }
            }
        ]

    def execute_tool(self, tool_name: str, parameters: Dict) -> Dict:
        """Execute a tool call from an LLM"""
        if tool_name == "get_sheet_data":
            return self.client.get_sheet_data(**parameters)
        elif tool_name == "update_cells":
            return self.client.update_cells(**parameters)
        elif tool_name == "create_spreadsheet":
            return self.client.create_spreadsheet(**parameters)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")


def main():
    """Example usage"""
    # Initialize client
    client = MCPGoogleSheetsClient(
        api_url="http://localhost:8080",
        api_key="sk-default-key-change-this"  # Replace with your API key
    )

    # Check health
    print("Health check:")
    print(json.dumps(client.health_check(), indent=2))

    # Example: List spreadsheets
    print("\nListing spreadsheets:")
    spreadsheets = client.list_spreadsheets()
    print(json.dumps(spreadsheets, indent=2))

    # Example: Get sheet data
    # Replace with actual spreadsheet ID
    # spreadsheet_id = "your-spreadsheet-id"
    # sheet_data = client.get_sheet_data(spreadsheet_id, "Sheet1")
    # print(json.dumps(sheet_data, indent=2))

    # Example for LLM integration
    llm_tools = LLMGoogleSheetsTools(
        api_url="http://localhost:8080",
        api_key="sk-default-key-change-this"
    )

    print("\nTools definition for LLMs:")
    print(json.dumps(llm_tools.get_tools_definition(), indent=2))


if __name__ == "__main__":
    main()