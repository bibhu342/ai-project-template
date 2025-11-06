from fastapi import FastAPI
from .api import router as api

app = FastAPI(title="AI Project API", version="0.1.15")
app.include_router(api, prefix="/api")
