from __future__ import annotations

import base64
import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import User


def _sign(data: str) -> str:
    return hmac.new(settings.secret_key.encode(), data.encode(), hashlib.sha256).hexdigest()


def create_session_token(user: User) -> str:
    payload = {
        "user_id": user.id,
        "username": user.username,
        "role": user.role,
        "exp": int((datetime.now(timezone.utc) + timedelta(hours=settings.session_expire_hours)).timestamp()),
    }
    raw = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    b64 = base64.urlsafe_b64encode(raw.encode()).decode()
    return f"{b64}.{_sign(b64)}"


def _decode_token(token: str) -> dict:
    try:
        b64, sig = token.split('.', 1)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="Invalid session") from exc
    if not hmac.compare_digest(_sign(b64), sig):
        raise HTTPException(status_code=401, detail="Invalid session")
    payload = json.loads(base64.urlsafe_b64decode(b64.encode()).decode())
    if int(payload.get("exp", 0)) < int(datetime.now(timezone.utc).timestamp()):
        raise HTTPException(status_code=401, detail="Session expired")
    return payload


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = request.cookies.get(settings.session_cookie_name)
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = _decode_token(token)
    user = db.query(User).filter(User.id == payload.get("user_id")).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User inactive or missing")
    return user


def require_authenticated_user(user: User = Depends(get_current_user)) -> User:
    return user


def require_role(*roles: str):
    def checker(request: Request, db: Session = Depends(get_db)):
        current = get_current_user(request, db)
        if current.role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient role")
        return current

    return checker


def require_admin(user: User = Depends(require_role("admin"))) -> User:
    return user


def require_operator_or_admin(user: User = Depends(require_role("operator", "admin"))) -> User:
    return user
