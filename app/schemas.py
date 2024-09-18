from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class NoteCreate(BaseModel):
    title: str
    content: str
    tags: List[str] = []


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: List[str] = []


class NoteInDB(BaseModel):
    id: int
    title: str
    content: str
    tags: List[str]
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
