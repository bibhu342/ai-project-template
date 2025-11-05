# app/api.py
from fastapi import APIRouter

from .routers.customers import router as customers_router

# If you built auth earlier, import it too:
# from app.routers.auth import router as auth_router

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


router.include_router(customers_router)  # -> /api/customers/...
# router.include_router(auth_router)      # -> /api/auth/...
