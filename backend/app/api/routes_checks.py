from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import require_operator_or_admin
from app.database import get_db
from app.models import Check, Report
from app.schemas import AsnCheckRequest, AsnRpkiBatchRequest, CheckResponse, PrefixCheckRequest, PreflightCheckRequest
from app.services.asn_checker import AsnChecker
from app.services.prefix_checker import PrefixChecker
from app.services.preflight_checker import PreflightChecker
from app.services.report_renderer import render_report
from app.services.ripe_stat_client import RipeStatClient

router = APIRouter(prefix="/api/check", tags=["checks"])


@router.post('/asn', response_model=CheckResponse)
def check_asn(payload: AsnCheckRequest, db: Session = Depends(get_db), user=Depends(require_operator_or_admin)) -> CheckResponse:
    try:
        result = AsnChecker(RipeStatClient(db)).check(payload.asn)
        return _store_and_respond(db, "asn", payload.asn, None, result, user.id)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"ASN-Prüfung fehlgeschlagen: {exc}") from exc


@router.post('/asn-rpki', response_model=CheckResponse)
def check_asn_rpki(payload: AsnRpkiBatchRequest, db: Session = Depends(get_db), user=Depends(require_operator_or_admin)) -> CheckResponse:
    try:
        result = AsnChecker(RipeStatClient(db)).check_rpki_batch(payload.asn, payload.limit)
        return _store_and_respond(db, "asn-rpki", payload.asn, None, result, user.id)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"ASN-RPKI-Batchprüfung fehlgeschlagen: {exc}") from exc


@router.post('/prefix', response_model=CheckResponse)
def check_prefix(payload: PrefixCheckRequest, db: Session = Depends(get_db), user=Depends(require_operator_or_admin)) -> CheckResponse:
    try:
        result = PrefixChecker(RipeStatClient(db)).check(payload.prefix, payload.origin_as)
        return _store_and_respond(db, "prefix", payload.prefix, payload.origin_as, result, user.id)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Prefix-Prüfung fehlgeschlagen: {exc}") from exc



@router.post('/preflight', response_model=CheckResponse)
def check_preflight(payload: PreflightCheckRequest, db: Session = Depends(get_db), user=Depends(require_operator_or_admin)) -> CheckResponse:
    try:
        result = PreflightChecker(RipeStatClient(db)).check(payload.prefix, payload.planned_origin_as)
        return _store_and_respond(db, "preflight", payload.prefix, payload.planned_origin_as, result, user.id)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Preflight-Prüfung fehlgeschlagen: {exc}") from exc


def _store_and_respond(db: Session, ctype: str, resource: str, origin_as: str | None, result: dict, user_id: int | None = None) -> CheckResponse:
    check = Check(check_type=ctype, input_resource=resource, origin_as=origin_as, status=result["status"], summary=result["summary"], created_by_user_id=user_id)
    db.add(check)
    db.commit()
    db.refresh(check)
    report_json, md, html = render_report({"check_id": check.id, "input_check_type": ctype, **result})
    report = Report(check_id=check.id, created_by_user_id=user_id, json_data=report_json, markdown=md, html=html)
    db.add(report)
    db.commit()
    db.refresh(report)
    return CheckResponse(report_id=report.id, status=result["status"], summary=result["summary"], explanation=result.get("explanation"), risk=result.get("risk"), recommendations=result["recommendations"], input=result.get("input"), checks=result.get("checks"), details=result["details"], markdown=md, html=html)
