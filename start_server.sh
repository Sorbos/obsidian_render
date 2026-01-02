#!/bin/bash
echo "🌐 Starting Obsidian MCP Server on HTTP..."
echo "📡 Server will be available at: http://localhost:8000"
echo "🔗 MCP endpoint: http://localhost:8000/mcp/message"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

# Activate virtual environment and start server in HTTP mode
source venv/bin/activate
python mcp-server.py --http