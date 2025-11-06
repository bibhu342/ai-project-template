# app/schemas/note.py
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class NoteCreate(BaseModel):
    """Schema for creating a new note."""

    content: str


class NoteUpdate(BaseModel):
    """Schema for updating an existing note."""

    content: str


class NoteOut(BaseModel):
    """Schema for note responses."""

    model_config = ConfigDict(from_attributes=True)  # pydantic v2

    id: int
    customer_id: int
    user_id: int
    content: str
    created_at: datetime
    updated_at: datetime


class NoteListResponse(BaseModel):
    """Schema for paginated note list responses."""

    items: list[NoteOut]
    total: int
    limit: int
    offset: int
    has_more: bool
