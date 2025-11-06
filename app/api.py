# app/api.py
from fastapi import APIRouter

from .routers.customers import router as customers_router
from .routers.notes import router as notes_router
from .routers.auth import router as auth_router

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


router.include_router(customers_router)  # -> /api/customers/...
router.include_router(notes_router)  # -> /api/customers/{id}/notes, /api/notes/{id}
router.include_router(auth_router)  # -> /api/auth/...
