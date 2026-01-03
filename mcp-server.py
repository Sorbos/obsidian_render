from mcp.server.fastmcp import FastMCP
from crud import get_notes, get_note, update_note, create_note, search_notes, search_notes_by_tags
from fastapi import HTTPException, Header, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional
import json
import os

# Create an MCP server
mcp = FastMCP("Obsidian")

# Security setup
security = HTTPBearer(auto_error=False)

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify API token - optional for development"""
    expected_token = os.getenv("MCP_API_TOKEN")
    
    # If no token is set in environment, allow all requests
    if not expected_token:
        return True
    
    # If token is set, verify it
    if not credentials or credentials.credentials != expected_token:
        raise HTTPException(status_code=401, detail="Invalid API token")
    
    return True

# Add CORS and authentication to the FastMCP app
@mcp.app.middleware("http")
async def add_cors_header(request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

# Add a health check endpoint
@mcp.app.get("/")
async def health_check():
    """Health check endpoint"""
    return JSONResponse({
        "status": "healthy",
        "service": "Obsidian MCP Server",
        "version": "1.0.0",
        "endpoints": {
            "mcp": "/mcp/message",
            "initialize": "/initialize",
            "tools_list": "/tools/list", 
            "tools_call": "/tools/call",
            "health": "/"
        },
        "message": "Server is running! Use POST endpoints for MCP requests.",
        "authentication": "Bearer token supported" if os.getenv("MCP_API_TOKEN") else "No authentication required",
        "mcp_protocol": "2024-11-05"
    })

@mcp.app.get("/health")
async def health():
    """Alternative health check endpoint"""
    return JSONResponse({"status": "healthy", "service": "Obsidian MCP Server"})

# Keep the original MCP message handler for backward compatibility
@mcp.app.post("/mcp/message")
async def handle_mcp_message(message: dict, token_valid: bool = Depends(verify_token)):
    """Handle MCP messages with optional authentication (backward compatibility)"""
    return await mcp._dispatch(message)

# Override the default MCP endpoints to be more compliant
@mcp.app.post("/initialize")
async def initialize_mcp(request: dict, token_valid: bool = Depends(verify_token)):
    """Initialize MCP connection"""
    return {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "tools": {},
            "prompts": {},
            "resources": {}
        },
        "serverInfo": {
            "name": "Obsidian Notes MCP Server",
            "version": "1.0.0"
        }
    }

@mcp.app.post("/tools/list")
async def list_tools_mcp(token_valid: bool = Depends(verify_token)):
    """List available tools"""
    tools = []
    for name, fn in mcp.tools.items():
        tools.append({
            "name": name,
            "description": fn.__doc__ or f"Tool: {name}",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        })
    return {"tools": tools}

@mcp.app.post("/tools/call")
async def call_tool_mcp(request: dict, token_valid: bool = Depends(verify_token)):
    """Call a specific tool"""
    name = request.get("name")
    arguments = request.get("arguments", {})
    
    if name not in mcp.tools:
        return {"error": f"Tool '{name}' not found"}
    
    try:
        fn = mcp.tools[name]
        if hasattr(fn, '__code__') and fn.__code__.co_flags & 0x80:  # Check if async
            result = await fn(**arguments)
        else:
            result = fn(**arguments)
        return {"content": [{"type": "text", "text": json.dumps(result)}]}
    except Exception as e:
        return {"error": str(e)}

# Add OPTIONS handlers for CORS
@mcp.app.options("/initialize")
async def options_initialize():
    return JSONResponse({"status": "ok"})

@mcp.app.options("/tools/list")
async def options_tools_list():
    return JSONResponse({"status": "ok"})

@mcp.app.options("/tools/call")
async def options_tools_call():
    return JSONResponse({"status": "ok"})

@mcp.app.options("/mcp/message")
async def options_mcp_message():
    return JSONResponse({"status": "ok"})

@mcp.prompt()
def obsidian(user_name: str = "User", user_title: str = "Note Taker") -> str:
    """Global instructions for Obsidian MCP"""
    return f"""# Obsidian Notes Assistant

You are an assistant helping {user_name} ({user_title}) manage their Obsidian notes stored in Supabase.

**Capabilities:**
- Search through notes by content or title
- Read specific notes by ID
- Create new notes in markdown format
- Update existing notes
- Search by tags
- List all notes

**Preferences:** 
- When creating or updating notes, use markdown formatting
- Be helpful and concise in responses
- Always confirm successful operations
"""

# Define tools
@mcp.tool()
async def list_all_notes():
    """Get all notes from the database"""
    try:
        response = await get_notes()
        if response.data:
            return {
                "success": True,
                "count": len(response.data),
                "notes": response.data
            }
        return {"success": True, "count": 0, "notes": []}
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def get_note_by_id(note_id: int):
    """Get a specific note by its ID"""
    try:
        response = await get_note(note_id)
        if response.data:
            return {"success": True, "note": response.data}
        return {"success": False, "error": "Note not found"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def create_new_note(title: str, content: str = "", tags: Optional[List[str]] = None):
    """Create a new note with title, content, and optional tags"""
    try:
        response = await create_note(title, content, tags)
        if response.data:
            return {"success": True, "note": response.data[0]}
        return {"success": False, "error": "Failed to create note"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def update_existing_note(note_id: int, title: str = None, content: str = None, tags: Optional[List[str]] = None):
    """Update an existing note's title, content, or tags"""
    try:
        response = await update_note(note_id, title, content, tags)
        if response.data:
            return {"success": True, "note": response.data[0]}
        return {"success": False, "error": "Note not found or update failed"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def search_notes_content(query: str):
    """Search notes by title or content using a text query"""
    try:
        response = await search_notes(query)
        if response.data:
            return {
                "success": True,
                "query": query,
                "count": len(response.data),
                "notes": response.data
            }
        return {"success": True, "query": query, "count": 0, "notes": []}
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def search_by_tags(tags: List[str]):
    """Search notes that contain any of the specified tags"""
    try:
        response = await search_notes_by_tags(tags)
        if response.data:
            return {
                "success": True,
                "tags": tags,
                "count": len(response.data),
                "notes": response.data
            }
        return {"success": True, "tags": tags, "count": 0, "notes": []}
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    import sys
    import os
    
    # Get port from environment (Render sets this)
    port = int(os.getenv("PORT", 8000))
    
    # Check if HTTP mode is requested or if PORT env var is set (Render deployment)
    if len(sys.argv) > 1 and sys.argv[1] == "--http" or os.getenv("PORT"):
        print("🌐 Starting Obsidian MCP Server on HTTP...")
        print(f"📡 Server will be available at: http://0.0.0.0:{port}")
        print("🔗 MCP endpoint: /mcp/message")
        print("🛑 Press Ctrl+C to stop the server")
        mcp.run(transport='http', host='0.0.0.0', port=port)
    else:
        print("📝 Starting Obsidian MCP Server on stdio...")
        print("🔗 Use --http flag for HTTP mode")
        mcp.run(transport='stdio')