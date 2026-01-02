from mcp.server.fastmcp import FastMCP
from crud import get_notes, get_note, update_note, create_note, search_notes, search_notes_by_tags
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from typing import List, Optional
import json

# Create an MCP server
mcp = FastMCP("Obsidian")

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
            "health": "/"
        },
        "message": "Server is running! Use POST /mcp/message for MCP requests."
    })

@mcp.app.get("/health")
async def health():
    """Alternative health check endpoint"""
    return JSONResponse({"status": "healthy", "service": "Obsidian MCP Server"})

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