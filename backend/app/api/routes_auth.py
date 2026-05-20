from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

import app.config as config
from app.core.audit import write_audit_log_for_request
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
def setup(payload: SetupRequest, request: Request, response: Response, db: Session = Depends(get_db)):
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
    response.set_cookie(config.settings.session_cookie_name, token, httponly=True, samesite=config.settings.cookie_samesite, secure=config.settings.cookie_secure)
    write_audit_log_for_request(db, request, action='initial_admin_setup', actor=user, target_type='user', target_id=str(user.id), details_json={'username': user.username, 'role': user.role})
    return {"user": {"id": user.id, "username": user.username, "email": user.email, "role": user.role}}

@router.post('/login')
def login(payload: LoginRequest, request: Request, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.password_hash) or not user.is_active:
        write_audit_log_for_request(db, request, action='login_failed', target_type='auth', details_json={'username': payload.username, 'reason': 'invalid_credentials'})
        raise HTTPException(status_code=401, detail='Invalid credentials')
    user.last_login_at = datetime.utcnow(); db.commit()
    token = create_session_token(user)
    response.set_cookie(config.settings.session_cookie_name, token, httponly=True, samesite=config.settings.cookie_samesite, secure=config.settings.cookie_secure)
    write_audit_log_for_request(db, request, action='login_success', actor=user, target_type='user', target_id=str(user.id), details_json={'username': user.username})
    return {"user": {"id": user.id, "username": user.username, "email": user.email, "role": user.role}}

@router.post('/logout')
def logout(request: Request, response: Response, user: User = Depends(require_authenticated_user), db: Session = Depends(get_db)):
    write_audit_log_for_request(db, request, action='logout', actor=user, target_type='user', target_id=str(user.id), details_json={'username': user.username})
    response.delete_cookie(config.settings.session_cookie_name, httponly=True, samesite=config.settings.cookie_samesite, secure=config.settings.cookie_secure)
    return {"ok": True}

@router.get('/me')
def me(user: User = Depends(require_authenticated_user)):
    return {"user": {"id": user.id, "username": user.username, "email": user.email, "role": user.role}}
