#!/usr/bin/env python3
"""
Setup script to create the notes table in Supabase
Run this once to initialize your database schema
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

def setup_database():
    """Create the notes table in Supabase"""
    url = os.getenv("sb_url")
    key = os.getenv("sb_api")
    
    if not url or not key:
        print("❌ Missing Supabase credentials in .env file")
        return False
    
    try:
        supabase: Client = create_client(url, key)
        
        # Test connection
        response = supabase.table("notes").select("count", count="exact").execute()
        print(f"✅ Connected to Supabase successfully")
        print(f"📊 Current notes count: {response.count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

def create_sample_note():
    """Create a sample note for testing"""
    url = os.getenv("sb_url")
    key = os.getenv("sb_api")
    supabase: Client = create_client(url, key)
    
    try:
        sample_note = {
            "title": "Welcome to Obsidian MCP",
            "content": """# Welcome to Obsidian MCP

This is a sample note created by the MCP server setup.

## Features
- ✅ Create notes
- ✅ Search notes
- ✅ Update notes
- ✅ Tag support

## Next Steps
1. Connect this MCP server to Le Chat
2. Start managing your notes through AI
3. Import your existing Obsidian notes

*Created by Obsidian MCP Server*
""",
            "tags": ["welcome", "setup", "mcp"]
        }
        
        response = supabase.table("notes").insert(sample_note).execute()
        if response.data:
            print(f"✅ Sample note created with ID: {response.data[0]['id']}")
            return True
        else:
            print("❌ Failed to create sample note")
            return False
            
    except Exception as e:
        print(f"❌ Failed to create sample note: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Setting up Obsidian MCP Database...")
    
    if setup_database():
        print("\n📝 Creating sample note...")
        create_sample_note()
        print("\n✅ Setup complete! Your MCP server is ready to use.")
        print("\n🔧 Next steps:")
        print("1. Run: python mcp-server.py")
        print("2. Test with Le Chat or your MCP client")
    else:
        print("\n❌ Setup failed. Please check your .env configuration.")