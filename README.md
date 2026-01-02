# Obsidian MCP Server

A Model Context Protocol (MCP) server that connects your Obsidian notes (stored in Supabase) to AI assistants like Le Chat.

## Features

- 📝 **Create Notes**: Add new notes with markdown content
- 🔍 **Search Notes**: Find notes by title, content, or tags
- ✏️ **Update Notes**: Modify existing notes
- 🏷️ **Tag Support**: Organize notes with tags
- 🔗 **Supabase Integration**: Cloud-hosted notes database

## Quick Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Supabase
1. Create a Supabase project at [supabase.com](https://supabase.com)
2. Create a `notes` table with this SQL:
```sql
CREATE TABLE notes (
  id BIGSERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  content TEXT DEFAULT '',
  tags TEXT[] DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS (Row Level Security)
ALTER TABLE notes ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all operations (adjust as needed)
CREATE POLICY "Allow all operations" ON notes FOR ALL USING (true);
```

### 3. Environment Setup
Update your `.env` file with your Supabase credentials:
```env
sb_url=your_supabase_project_url
sb_api=your_supabase_secret_key
secret_api_key=your_api_key_for_fastapi
```

### 4. Initialize Database
```bash
python setup_database.py
```

### 5. Test the Server
```bash
python test_mcp.py
```

### 6. Run the MCP Server
```bash
python mcp-server.py
```

## Connecting to Le Chat

1. Copy the `mcp-config.json` configuration
2. Add it to your Le Chat MCP configuration
3. The server will be available as "obsidian-notes"

## Available Tools

- `list_all_notes()` - Get all notes
- `get_note_by_id(note_id)` - Get specific note
- `create_new_note(title, content, tags)` - Create new note
- `update_existing_note(note_id, title, content, tags)` - Update note
- `search_notes_content(query)` - Search by text
- `search_by_tags(tags)` - Search by tags

## Example Usage

Once connected to Le Chat, you can:
- "Show me all my notes about Python"
- "Create a new note titled 'Meeting Notes' with today's agenda"
- "Update note 5 with the latest project status"
- "Find all notes tagged with 'important'"

## Tech Stack

- **Python** - Core language
- **FastMCP** - MCP server framework
- **Supabase** - PostgreSQL database hosting
- **Pydantic** - Data validation