from fastapi import FastAPI
from app.api import router as api

app = FastAPI(title="AI Project API")
app.include_router(api, prefix="/api")
