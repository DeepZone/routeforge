from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.auth import require_admin
from app.core.security import hash_password, validate_password_strength
from app.database import get_db
from app.models import User

router = APIRouter(prefix='/api/users', tags=['users'])

class UserCreate(BaseModel):
    username: str
    email: str | None = None
    password: str
    role: str

class UserPatch(BaseModel):
    email: str | None = None
    role: str | None = None
    is_active: bool | None = None
    password: str | None = None

@router.get('')
def list_users(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.id.asc()).all()
    return [{"id":u.id,"username":u.username,"email":u.email,"role":u.role,"is_active":u.is_active,"created_at":u.created_at.isoformat(),"updated_at":u.updated_at.isoformat(),"last_login_at":u.last_login_at.isoformat() if u.last_login_at else None} for u in users]

@router.post('')
def create_user(payload: UserCreate, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    if payload.role not in {'admin','operator','viewer'}:
        raise HTTPException(status_code=400, detail='Invalid role')
    errs=validate_password_strength(payload.password)
    if errs: raise HTTPException(status_code=400, detail='; '.join(errs))
    user=User(username=payload.username.strip(), email=payload.email, password_hash=hash_password(payload.password), role=payload.role, is_active=True)
    db.add(user); db.commit(); db.refresh(user)
    return {"id":user.id,"username":user.username,"email":user.email,"role":user.role,"is_active":user.is_active,"created_at":user.created_at.isoformat(),"updated_at":user.updated_at.isoformat(),"last_login_at":user.last_login_at.isoformat() if user.last_login_at else None}

@router.patch('/{user_id}')
def patch_user(user_id:int,payload:UserPatch,_:User=Depends(require_admin),db:Session=Depends(get_db)):
    user=db.query(User).filter(User.id==user_id).first()
    if not user: raise HTTPException(status_code=404, detail='User not found')
    if payload.email is not None: user.email=payload.email
    if payload.role is not None:
        if payload.role not in {'admin','operator','viewer'}:
            raise HTTPException(status_code=400, detail='Invalid role')
        user.role=payload.role
    if payload.is_active is not None: user.is_active=payload.is_active
    if payload.password is not None:
        errs=validate_password_strength(payload.password)
        if errs: raise HTTPException(status_code=400, detail='; '.join(errs))
        user.password_hash=hash_password(payload.password)
    db.commit(); db.refresh(user)
    return {"id":user.id,"username":user.username,"email":user.email,"role":user.role,"is_active":user.is_active,"created_at":user.created_at.isoformat(),"updated_at":user.updated_at.isoformat(),"last_login_at":user.last_login_at.isoformat() if user.last_login_at else None}
