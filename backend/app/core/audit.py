import logging
from typing import Any

from fastapi import Request
from sqlalchemy.orm import Session

from app.models import AuditLog, User

logger = logging.getLogger("routeforge.audit")


def extract_request_meta(request: Request) -> tuple[str | None, str | None]:
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    return ip_address, user_agent


def write_audit_log(
    db: Session,
    *,
    user_id: int | None,
    action: str,
    target_type: str | None = None,
    target_id: str | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
    details_json: dict[str, Any] | None = None,
) -> None:
    try:
        entry = AuditLog(
            user_id=user_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details_json=details_json,
        )
        db.add(entry)
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("audit log write failed", extra={"action": action, "target_type": target_type, "target_id": target_id})


def write_audit_log_for_request(
    db: Session,
    request: Request,
    *,
    action: str,
    actor: User | None = None,
    target_type: str | None = None,
    target_id: str | None = None,
    details_json: dict[str, Any] | None = None,
) -> None:
    ip_address, user_agent = extract_request_meta(request)
    write_audit_log(
        db,
        user_id=actor.id if actor else None,
        action=action,
        target_type=target_type,
        target_id=target_id,
        ip_address=ip_address,
        user_agent=user_agent,
        details_json=details_json,
    )
