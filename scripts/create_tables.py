from sqlalchemy import create_engine
from app.models.customer import Base

engine = create_engine("postgresql+psycopg://bibhu:supersecure@localhost:5432/ai_lab")
Base.metadata.create_all(engine)
print("Tables synced ✅")
