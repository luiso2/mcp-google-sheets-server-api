"""
FastAPI HTTP Server for MCP Google Sheets
Exposes MCP tools as REST API endpoints
"""

import os
import json
import asyncio
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, Security, status
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Import the MCP server components
from ..server import (
    SpreadsheetContext,
    spreadsheet_lifespan as mcp_lifespan,
    mcp
)

# API Key configuration
API_KEYS_FILE = os.environ.get('API_KEYS_FILE', 'api_keys.json')
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# Store for API keys
API_KEYS: Dict[str, str] = {}

# Global context for spreadsheet services
spreadsheet_context: Optional[SpreadsheetContext] = None


# Pydantic models for request/response
class GetSheetDataRequest(BaseModel):
    spreadsheet_id: str = Field(..., description="The ID of the spreadsheet")
    sheet: str = Field(..., description="The name of the sheet")
    range: Optional[str] = Field(None, description="Cell range in A1 notation")
    include_grid_data: bool = Field(False, description="Include cell formatting and metadata")


class GetSheetFormulasRequest(BaseModel):
    spreadsheet_id: str = Field(..., description="The ID of the spreadsheet")
    sheet: str = Field(..., description="The name of the sheet")
    range: Optional[str] = Field(None, description="Cell range in A1 notation")


class UpdateCellsRequest(BaseModel):
    spreadsheet_id: str = Field(..., description="The ID of the spreadsheet")
    sheet: str = Field(..., description="The name of the sheet")
    range: str = Field(..., description="Cell range in A1 notation")
    data: List[List[Any]] = Field(..., description="2D array of values to update")


class BatchUpdateRequest(BaseModel):
    spreadsheet_id: str = Field(..., description="The ID of the spreadsheet")
    updates: List[Dict[str, Any]] = Field(..., description="List of update operations")


class AddRowsRequest(BaseModel):
    spreadsheet_id: str = Field(..., description="The ID of the spreadsheet")
    sheet: str = Field(..., description="The name of the sheet")
    rows: List[List[Any]] = Field(..., description="Rows of data to add")
    append: bool = Field(True, description="Append to end or insert at beginning")


class CreateSpreadsheetRequest(BaseModel):
    title: str = Field(..., description="Title of the new spreadsheet")


class ShareSpreadsheetRequest(BaseModel):
    spreadsheet_id: str = Field(..., description="The ID of the spreadsheet")
    email_addresses: List[str] = Field(..., description="Email addresses to share with")
    role: str = Field("reader", description="Permission role: reader, writer, commenter, or owner")
    send_notification: bool = Field(True, description="Send email notification")


class CreateSheetRequest(BaseModel):
    spreadsheet_id: str = Field(..., description="The ID of the spreadsheet")
    title: str = Field(..., description="Title of the new sheet")


class RenameSheetRequest(BaseModel):
    spreadsheet_id: str = Field(..., description="The ID of the spreadsheet")
    old_name: str = Field(..., description="Current name of the sheet")
    new_name: str = Field(..., description="New name for the sheet")


class CopySheetRequest(BaseModel):
    src_spreadsheet: str = Field(..., description="Source spreadsheet ID")
    src_sheet: str = Field(..., description="Source sheet name")
    dst_spreadsheet: str = Field(..., description="Destination spreadsheet ID")
    dst_sheet: Optional[str] = Field(None, description="Destination sheet name")


# Mock Context class for MCP tool compatibility
class MockContext:
    def __init__(self, spreadsheet_context):
        self.request_context = type('obj', (object,), {
            'lifespan_context': spreadsheet_context
        })()


def load_api_keys():
    """Load API keys from file"""
    global API_KEYS
    if os.path.exists(API_KEYS_FILE):
        try:
            with open(API_KEYS_FILE, 'r') as f:
                API_KEYS = json.load(f)
                print(f"Loaded {len(API_KEYS)} API keys")
        except Exception as e:
            print(f"Error loading API keys: {e}")
            API_KEYS = {}
    else:
        # Create default API keys file
        default_keys = {
            "default": "sk-default-key-change-this",
            "example_client": "sk-example-key-12345"
        }
        try:
            with open(API_KEYS_FILE, 'w') as f:
                json.dump(default_keys, f, indent=2)
            print(f"Created default API keys file: {API_KEYS_FILE}")
            API_KEYS = default_keys
        except Exception as e:
            print(f"Could not create API keys file: {e}")
            API_KEYS = {}


async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """Verify API key from request header"""
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key required"
        )

    # Check if API key exists in our store
    client_id = None
    for cid, key in API_KEYS.items():
        if key == api_key:
            client_id = cid
            break

    if not client_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )

    return client_id


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    global spreadsheet_context

    # Load API keys
    load_api_keys()

    # Initialize MCP context
    print("Initializing Google Sheets services...")
    async for context in mcp_lifespan(None):
        spreadsheet_context = context
        print("Google Sheets services initialized")
        yield
        print("Shutting down Google Sheets services...")

    spreadsheet_context = None


# Create FastAPI app
app = FastAPI(
    title="MCP Google Sheets API",
    description="REST API wrapper for MCP Google Sheets Server",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "MCP Google Sheets API",
        "context_initialized": spreadsheet_context is not None
    }


# Tool endpoints
@app.post("/tools/get_sheet_data")
async def get_sheet_data(
    request: GetSheetDataRequest,
    client_id: str = Depends(verify_api_key)
):
    """Get data from a specific sheet in a Google Spreadsheet"""
    if not spreadsheet_context:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        # Import the original MCP tool function
        from ..server import get_sheet_data as mcp_get_sheet_data

        ctx = MockContext(spreadsheet_context)
        result = mcp_get_sheet_data(
            spreadsheet_id=request.spreadsheet_id,
            sheet=request.sheet,
            range=request.range,
            include_grid_data=request.include_grid_data,
            ctx=ctx
        )
        return {"client_id": client_id, "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/tools/get_sheet_formulas")
async def get_sheet_formulas(
    request: GetSheetFormulasRequest,
    client_id: str = Depends(verify_api_key)
):
    """Get formulas from a specific sheet"""
    if not spreadsheet_context:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        from ..server import get_sheet_formulas as mcp_get_sheet_formulas

        ctx = MockContext(spreadsheet_context)
        result = mcp_get_sheet_formulas(
            spreadsheet_id=request.spreadsheet_id,
            sheet=request.sheet,
            range=request.range,
            ctx=ctx
        )
        return {"client_id": client_id, "formulas": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/tools/update_cells")
async def update_cells(
    request: UpdateCellsRequest,
    client_id: str = Depends(verify_api_key)
):
    """Update cells in a Google Spreadsheet"""
    if not spreadsheet_context:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        from ..server import update_cells as mcp_update_cells

        ctx = MockContext(spreadsheet_context)
        result = mcp_update_cells(
            spreadsheet_id=request.spreadsheet_id,
            sheet=request.sheet,
            range=request.range,
            data=request.data,
            ctx=ctx
        )
        return {"client_id": client_id, "result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/tools/batch_update_cells")
async def batch_update_cells(
    request: BatchUpdateRequest,
    client_id: str = Depends(verify_api_key)
):
    """Batch update cells in a spreadsheet"""
    if not spreadsheet_context:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        from ..server import batch_update_cells as mcp_batch_update

        ctx = MockContext(spreadsheet_context)
        result = mcp_batch_update(
            spreadsheet_id=request.spreadsheet_id,
            updates=request.updates,
            ctx=ctx
        )
        return {"client_id": client_id, "result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/tools/add_rows")
async def add_rows(
    request: AddRowsRequest,
    client_id: str = Depends(verify_api_key)
):
    """Add rows to a sheet"""
    if not spreadsheet_context:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        from ..server import add_rows as mcp_add_rows

        ctx = MockContext(spreadsheet_context)
        result = mcp_add_rows(
            spreadsheet_id=request.spreadsheet_id,
            sheet=request.sheet,
            rows=request.rows,
            append=request.append,
            ctx=ctx
        )
        return {"client_id": client_id, "result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/tools/create_spreadsheet")
async def create_spreadsheet(
    request: CreateSpreadsheetRequest,
    client_id: str = Depends(verify_api_key)
):
    """Create a new Google Spreadsheet"""
    if not spreadsheet_context:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        from ..server import create_spreadsheet as mcp_create_spreadsheet

        ctx = MockContext(spreadsheet_context)
        result = mcp_create_spreadsheet(
            title=request.title,
            ctx=ctx
        )
        return {"client_id": client_id, "spreadsheet": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/tools/create_sheet")
async def create_sheet(
    request: CreateSheetRequest,
    client_id: str = Depends(verify_api_key)
):
    """Create a new sheet in a spreadsheet"""
    if not spreadsheet_context:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        from ..server import create_sheet as mcp_create_sheet

        ctx = MockContext(spreadsheet_context)
        result = mcp_create_sheet(
            spreadsheet_id=request.spreadsheet_id,
            title=request.title,
            ctx=ctx
        )
        return {"client_id": client_id, "result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/tools/list_spreadsheets")
async def list_spreadsheets(
    client_id: str = Depends(verify_api_key)
):
    """List all accessible spreadsheets"""
    if not spreadsheet_context:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        from ..server import list_spreadsheets as mcp_list_spreadsheets

        ctx = MockContext(spreadsheet_context)
        result = mcp_list_spreadsheets(ctx=ctx)
        return {"client_id": client_id, "spreadsheets": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/tools/list_sheets/{spreadsheet_id}")
async def list_sheets(
    spreadsheet_id: str,
    client_id: str = Depends(verify_api_key)
):
    """List all sheets in a spreadsheet"""
    if not spreadsheet_context:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        from ..server import list_sheets as mcp_list_sheets

        ctx = MockContext(spreadsheet_context)
        result = mcp_list_sheets(
            spreadsheet_id=spreadsheet_id,
            ctx=ctx
        )
        return {"client_id": client_id, "sheets": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/tools/share_spreadsheet")
async def share_spreadsheet(
    request: ShareSpreadsheetRequest,
    client_id: str = Depends(verify_api_key)
):
    """Share a spreadsheet with specified email addresses"""
    if not spreadsheet_context:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        from ..server import share_spreadsheet as mcp_share_spreadsheet

        ctx = MockContext(spreadsheet_context)
        result = mcp_share_spreadsheet(
            spreadsheet_id=request.spreadsheet_id,
            email_addresses=request.email_addresses,
            role=request.role,
            send_notification=request.send_notification,
            ctx=ctx
        )
        return {"client_id": client_id, "result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/tools/rename_sheet")
async def rename_sheet(
    request: RenameSheetRequest,
    client_id: str = Depends(verify_api_key)
):
    """Rename a sheet in a spreadsheet"""
    if not spreadsheet_context:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        from ..server import rename_sheet as mcp_rename_sheet

        ctx = MockContext(spreadsheet_context)
        result = mcp_rename_sheet(
            spreadsheet=request.spreadsheet_id,
            old_name=request.old_name,
            new_name=request.new_name,
            ctx=ctx
        )
        return {"client_id": client_id, "result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/tools/copy_sheet")
async def copy_sheet(
    request: CopySheetRequest,
    client_id: str = Depends(verify_api_key)
):
    """Copy a sheet from one spreadsheet to another"""
    if not spreadsheet_context:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        from ..server import copy_sheet as mcp_copy_sheet

        ctx = MockContext(spreadsheet_context)
        result = mcp_copy_sheet(
            src_spreadsheet=request.src_spreadsheet,
            src_sheet=request.src_sheet,
            dst_spreadsheet=request.dst_spreadsheet,
            dst_sheet=request.dst_sheet,
            ctx=ctx
        )
        return {"client_id": client_id, "result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def start_server(host: str = "0.0.0.0", port: int = 8080, reload: bool = False):
    """Start the HTTP server"""
    uvicorn.run(
        "mcp_google_sheets.api.http_server:app",
        host=host,
        port=port,
        reload=reload
    )


if __name__ == "__main__":
    start_server()