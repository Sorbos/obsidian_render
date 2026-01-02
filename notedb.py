import os
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import APIKeyHeader
from typing import List
from crud import get_notes, get_note, update_note
from schemas import Note, NoteCreate
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

api_key_header = APIKeyHeader(name="X-API-Key")

async def get_api_key(api_key: str = Depends(api_key_header)):
    if api_key != os.getenv("secret_api_key"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )
    return api_key

@app.get("/notes", response_model=List[Note], dependencies=[Depends(get_api_key)])
async def read_notes():
    response = await get_notes()
    return response.data

@app.get("/notes/{note_id}", response_model=Note, dependencies=[Depends(get_api_key)])
async def read_note(note_id: int):
    response = await get_note(note_id)
    if not response.data:
        raise HTTPException(status_code=404, detail="Note not found")
    return response.data

@app.patch("/notes/{note_id}", response_model=Note, dependencies=[Depends(get_api_key)])
async def patch_note(note_id: int, content: str):
    response = await update_note(note_id, content)
    if not response.data:
        raise HTTPException(status_code=404, detail="Note not found")
    return response.data