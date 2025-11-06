# app/repositories/note_repo.py
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..models.note import Note


def create_note(db: Session, customer_id: int, user_id: int, content: str) -> Note:
    """Create a new note for a customer."""
    note = Note(customer_id=customer_id, user_id=user_id, content=content)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


def get_notes_by_customer(
    db: Session, customer_id: int, limit: int = 100, offset: int = 0
) -> list[Note]:
    """Get all notes for a specific customer."""
    return (
        db.query(Note)
        .filter(Note.customer_id == customer_id)
        .order_by(Note.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def get_note_by_id(db: Session, note_id: int) -> Note | None:
    """Get a single note by ID."""
    return db.get(Note, note_id)


def update_note_content(db: Session, note_id: int, new_content: str) -> Note | None:
    """Update the content of an existing note."""
    note = db.get(Note, note_id)
    if not note:
        return None
    note.content = new_content
    # Manually trigger updated_at (in case onupdate doesn't fire)
    note.updated_at = text("now()")
    db.commit()
    db.refresh(note)
    return note


def delete_note(db: Session, note_id: int) -> bool:
    """Delete a note by ID."""
    note = db.get(Note, note_id)
    if not note:
        return False
    db.delete(note)
    db.commit()
    return True
