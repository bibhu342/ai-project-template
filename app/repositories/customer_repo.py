from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ..models.customer import Customer


def create_customer(db: Session, name: str, email: str) -> Customer | None:
    row = Customer(name=name, email=email)
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # Return existing by email if unique violation
        return db.query(Customer).filter_by(email=email).first()
    db.refresh(row)
    return row


def get_customer_by_id(db: Session, customer_id: int) -> Customer | None:
    return db.get(Customer, customer_id)


def get_customers(db: Session, limit: int = 100, offset: int = 0) -> list[Customer]:
    return db.query(Customer).offset(offset).limit(limit).all()


def update_customer_email(
    db: Session, customer_id: int, new_email: str
) -> Customer | None:
    row = db.get(Customer, customer_id)
    if not row:
        return None
    row.email = new_email
    db.commit()
    db.refresh(row)
    return row


def delete_customer(db: Session, customer_id: int) -> bool:
    row = db.get(Customer, customer_id)
    if not row:
        return False
    db.delete(row)
    db.commit()
    return True
