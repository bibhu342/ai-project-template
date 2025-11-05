from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from ..db import get_db
from ..schemas.user import SignupIn, UserOut
from ..repositories.user_repo import get_user_by_email, create_user
from ..security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_token,
)

router = APIRouter(prefix="/auth", tags=["Auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@router.post("/signup", response_model=UserOut, status_code=201)
def signup(payload: SignupIn, db: Session = Depends(get_db)):
    if get_user_by_email(db, payload.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    user = create_user(db, payload.email, hash_password(payload.password))
    return UserOut.model_validate(user)


@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_email(db, form.username)
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(sub=str(user.id))
    return {"access_token": token, "token_type": "bearer"}


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> UserOut:
    data = decode_token(token)
    if not data:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    from ..models.user import User

    u = db.get(User, int(data["sub"]))
    if not u:
        raise HTTPException(status_code=401, detail="User not found")
    return UserOut.model_validate(u)


@router.get("/me", response_model=UserOut)
def me(current: UserOut = Depends(get_current_user)):
    return current
