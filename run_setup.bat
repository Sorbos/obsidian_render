@echo off
echo Setting up Obsidian MCP Server...
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found. Please install Python 3.8+ from python.org
    echo Then run this script again.
    pause
    exit /b 1
)

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Setting up database...
python setup_database.py

echo.
echo Testing MCP server...
python test_mcp.py

echo.
echo Setup complete! 
echo To run the MCP server: python mcp-server.py
pause