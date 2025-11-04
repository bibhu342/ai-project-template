from sqlalchemy.orm import Session
from app.models.user import User


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, email: str, password_hash: str) -> User:
    u = User(email=email, password_hash=password_hash)
    db.add(u)
    db.commit()
    db.refresh(u)
    return u
