import os
from sqlalchemy import create_engine
from app.database import Base

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://bibhu:supersecure@localhost:5432/ai_lab",
)

engine = create_engine(DATABASE_URL, future=True)
Base.metadata.create_all(engine)
print("Tables synced ✅")
