import sys
import pathlib
import uuid

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from app.db import SessionLocal
from app.repositories.customer_repo import (
    create_customer,
    get_customer_by_id,
    get_customers,
    update_customer_email,
    delete_customer,
)


def main():
    db = SessionLocal()
    try:
        e1 = f"bibhu+{uuid.uuid4().hex[:6]}@example.com"
        e2 = f"aisha+{uuid.uuid4().hex[:6]}@example.com"

        a = create_customer(db, "Bibhu", e1)
        b = create_customer(db, "Aisha Khan", e2)
        print("Created IDs:", a.id, b.id)

        print("Get by id:", get_customer_by_id(db, a.id))
        print("List:", [c.email for c in get_customers(db)])

        u = update_customer_email(db, a.id, e1.replace("@", "+new@"))
        print("Updated:", u.email)

        ok = delete_customer(db, b.id)
        print("Deleted B:", ok)

        print("Remaining:", [c.email for c in get_customers(db)])
    finally:
        db.close()


if __name__ == "__main__":
    main()
