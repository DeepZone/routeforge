from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.auth import require_admin
from app.database import get_db
from app.models import AuditLog, User

router = APIRouter(prefix='/api/audit-log', tags=['audit'])

@router.get('')
def list_audit_log(
    action: str | None = Query(default=None),
    user_id: int | None = Query(default=None),
    target_type: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    query = db.query(AuditLog, User.username).outerjoin(User, AuditLog.user_id == User.id)
    if action:
        query = query.filter(AuditLog.action == action)
    if user_id is not None:
        query = query.filter(AuditLog.user_id == user_id)
    if target_type:
        query = query.filter(AuditLog.target_type == target_type)

    rows = query.order_by(AuditLog.created_at.desc(), AuditLog.id.desc()).offset(offset).limit(limit).all()
    return {
        'items': [
            {
                'id': audit.id,
                'created_at': audit.created_at.isoformat(),
                'user_id': audit.user_id,
                'username': username,
                'action': audit.action,
                'target_type': audit.target_type,
                'target_id': audit.target_id,
                'ip_address': audit.ip_address,
                'user_agent': audit.user_agent,
                'details_json': audit.details_json,
            }
            for audit, username in rows
        ],
        'limit': limit,
        'offset': offset,
    }
