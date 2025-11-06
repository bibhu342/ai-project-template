# app/routers/notes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..deps import get_db
from ..schemas.note import NoteCreate, NoteUpdate, NoteOut
from ..schemas.user import UserOut
from ..repositories.note_repo import (
    create_note,
    get_notes_by_customer,
    get_note_by_id,
    update_note_content,
    delete_note,
)
from ..repositories.customer_repo import get_customer_by_id
from .auth import get_current_user

router = APIRouter(tags=["Notes"])


@router.post("/customers/{customer_id}/notes", response_model=NoteOut, status_code=201)
def create_note_endpoint(
    customer_id: int,
    payload: NoteCreate,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user),
):
    """Create a new note for a customer. Requires authentication."""
    # Check if customer exists
    customer = get_customer_by_id(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Create note with current user as owner
    note = create_note(db, customer_id, current_user.id, payload.content)
    return note


@router.get("/customers/{customer_id}/notes", response_model=list[NoteOut])
def list_notes_endpoint(
    customer_id: int,
    db: Session = Depends(get_db),
):
    """List all notes for a customer. No authentication required."""
    # Check if customer exists
    customer = get_customer_by_id(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    notes = get_notes_by_customer(db, customer_id)
    return notes


@router.put("/notes/{note_id}", response_model=NoteOut)
def update_note_endpoint(
    note_id: int,
    payload: NoteUpdate,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user),
):
    """Update a note. Only the note owner can update it."""
    note = get_note_by_id(db, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    # Check ownership
    if note.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="You can only update your own notes"
        )

    updated_note = update_note_content(db, note_id, payload.content)
    return updated_note


@router.delete("/notes/{note_id}", status_code=204)
def delete_note_endpoint(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user),
):
    """Delete a note. Only the note owner can delete it."""
    note = get_note_by_id(db, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    # Check ownership
    if note.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="You can only delete your own notes"
        )

    delete_note(db, note_id)
    return None  # 204 No Content
