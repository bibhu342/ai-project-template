from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.deps import get_db  # ✅ correct source
from app.schemas.customer import CustomerCreate, CustomerOut, CustomerUpdateEmail
from app.repositories.customer_repo import (
    create_customer,
    get_customer_by_id,
    get_customers,
    update_customer_email,
    delete_customer,
)

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok"}

@router.post("/customers", response_model=CustomerOut, status_code=201)
def create_customer_ep(payload: CustomerCreate, db: Session = Depends(get_db)):
    row = create_customer(db, payload.name, payload.email)
    if row is None:
        # if IntegrityError path returned None, fetch existing
        # (optional: you can just return 409 instead—your call)
        raise HTTPException(status_code=409, detail="Email already exists")
    return row

@router.get("/customers", response_model=list[CustomerOut])
def list_customers_ep(db: Session = Depends(get_db)):
    return get_customers(db)

@router.get("/customers/{customer_id}", response_model=CustomerOut)
def get_customer_ep(customer_id: int, db: Session = Depends(get_db)):
    row = get_customer_by_id(db, customer_id)
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    return row

@router.patch("/customers/{customer_id}", response_model=CustomerOut)
def update_email_ep(customer_id: int, payload: CustomerUpdateEmail, db: Session = Depends(get_db)):
    row = update_customer_email(db, customer_id, new_email=payload.email)
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    return row

@router.delete("/customers/{customer_id}", status_code=204)
def delete_customer_ep(customer_id: int, db: Session = Depends(get_db)):
    ok = delete_customer(db, customer_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Not found")
    return
