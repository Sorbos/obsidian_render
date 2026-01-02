import os
from supabase import create_client, Client
from dotenv import load_dotenv
from schemas import Note, NoteCreate
from typing import List, Optional

load_dotenv()
url: str = os.getenv("sb_url")
key: str = os.getenv("sb_api")
supabase: Client = create_client(url, key)

async def get_notes():
    """Get all notes from the database"""
    response = supabase.table("notes").select("*").execute()
    return response

async def get_note(note_id: int):
    """Get a specific note by ID"""
    response = supabase.table("notes").select("*").eq("id", note_id).single().execute()
    return response

async def create_note(title: str, content: str = "", tags: Optional[List[str]] = None):
    """Create a new note"""
    note_data = {
        "title": title,
        "content": content,
        "tags": tags or []
    }
    response = supabase.table("notes").insert(note_data).execute()
    return response

async def update_note(note_id: int, title: str = None, content: str = None, tags: Optional[List[str]] = None):
    """Update an existing note"""
    update_data = {}
    if title is not None:
        update_data["title"] = title
    if content is not None:
        update_data["content"] = content
    if tags is not None:
        update_data["tags"] = tags
    
    response = supabase.table("notes").update(update_data).eq("id", note_id).execute()
    return response

async def search_notes(query: str):
    """Search notes by title or content"""
    response = supabase.table("notes").select("*").or_(
        f"title.ilike.%{query}%,content.ilike.%{query}%"
    ).execute()
    return response

async def search_notes_by_tags(tags: List[str]):
    """Search notes by tags"""
    response = supabase.table("notes").select("*").contains("tags", tags).execute()
    return response