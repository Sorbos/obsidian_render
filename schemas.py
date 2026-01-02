from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Base Model for note creation and updates
class NoteBase(BaseModel):
    title: str
    content: Optional[str] = None
    tags: Optional[List[str]] = None
    size_bytes: Optional[int] = None

# Create Model
class NoteCreate(NoteBase):
    pass

# Full note model
class Note(NoteBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        json_encoders = {
            datetime:lambda v: v.isoformat(),
        }