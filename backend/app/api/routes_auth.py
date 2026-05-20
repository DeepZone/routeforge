from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.auth import create_session_token, require_authenticated_user
from app.core.security import hash_password, validate_password_strength, verify_password
from app.database import get_db
from app.models import User

router = APIRouter(prefix="/api/auth", tags=["auth"])

class SetupRequest(BaseModel):
    username: str
    email: str | None = None
    password: str
    password_confirm: str

class LoginRequest(BaseModel):
    username: str
    password: str

@router.get('/setup-required')
def setup_required(db: Session = Depends(get_db)):
    return {"setup_required": db.query(User).count() == 0}

@router.post('/setup')
def setup(payload: SetupRequest, response: Response, db: Session = Depends(get_db)):
    if db.query(User).count() > 0:
        raise HTTPException(status_code=403, detail='Setup already completed')
    if payload.password != payload.password_confirm:
        raise HTTPException(status_code=400, detail='Password confirmation mismatch')
    errs = validate_password_strength(payload.password)
    if errs:
        raise HTTPException(status_code=400, detail='; '.join(errs))
    user = User(username=payload.username.strip(), email=payload.email, password_hash=hash_password(payload.password), role='admin', is_active=True)
    db.add(user); db.commit(); db.refresh(user)
    token = create_session_token(user)
    response.set_cookie('routeforge_session', token, httponly=True, samesite='lax')
    return {"user": {"id": user.id, "username": user.username, "email": user.email, "role": user.role}}

@router.post('/login')
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.password_hash) or not user.is_active:
        raise HTTPException(status_code=401, detail='Invalid credentials')
    user.last_login_at = datetime.utcnow(); db.commit()
    token = create_session_token(user)
    response.set_cookie('routeforge_session', token, httponly=True, samesite='lax')
    return {"user": {"id": user.id, "username": user.username, "email": user.email, "role": user.role}}

@router.post('/logout')
def logout(response: Response):
    response.delete_cookie('routeforge_session')
    return {"ok": True}

@router.get('/me')
def me(user: User = Depends(require_authenticated_user)):
    return {"user": {"id": user.id, "username": user.username, "email": user.email, "role": user.role}}
