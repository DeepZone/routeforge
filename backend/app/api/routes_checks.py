from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.core.auth import require_operator_or_admin
from app.core.audit import write_audit_log
from app.database import get_db
from app.models import ChangeCase, Check, Report
from app.schemas import AsnCheckRequest, AsnRpkiBatchRequest, BgpVisibilityCheckRequest, CheckResponse, PrefixCheckRequest, PreflightCheckRequest, RoaPreflightCheckRequest
from app.services.asn_checker import AsnChecker
from app.services.bgp_visibility_service import BgpVisibilityService
from app.services.prefix_checker import PrefixChecker
from app.services.preflight_checker import PreflightChecker
from app.services.report_renderer import render_report
from app.services.roa_planner_service import RoaPlannerService
from app.services.ripe_stat_client import RipeStatClient

router = APIRouter(prefix="/api/check", tags=["checks"])


@router.post('/asn', response_model=CheckResponse)
def check_asn(payload: AsnCheckRequest, db: Session = Depends(get_db), user=Depends(require_operator_or_admin)) -> CheckResponse:
    try:
        result = AsnChecker(RipeStatClient(db)).check(payload.asn)
        return _store_and_respond(db, "asn", payload.asn, None, result, user.id, payload.change_case_id)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"ASN check failed: {exc}") from exc


@router.post('/asn-rpki', response_model=CheckResponse)
def check_asn_rpki(payload: AsnRpkiBatchRequest, db: Session = Depends(get_db), user=Depends(require_operator_or_admin)) -> CheckResponse:
    try:
        result = AsnChecker(RipeStatClient(db)).check_rpki_batch(payload.asn, payload.limit)
        return _store_and_respond(db, "asn-rpki", payload.asn, None, result, user.id, payload.change_case_id)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"ASN RPKI batch check failed: {exc}") from exc


@router.post('/prefix', response_model=CheckResponse)
def check_prefix(payload: PrefixCheckRequest, db: Session = Depends(get_db), user=Depends(require_operator_or_admin)) -> CheckResponse:
    try:
        result = PrefixChecker(RipeStatClient(db)).check(payload.prefix, payload.origin_as)
        return _store_and_respond(db, "prefix", payload.prefix, payload.origin_as, result, user.id, payload.change_case_id)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Prefix check failed: {exc}") from exc





@router.post('/bgp-visibility', response_model=CheckResponse)
def check_bgp_visibility(payload: BgpVisibilityCheckRequest, db: Session = Depends(get_db), user=Depends(require_operator_or_admin)) -> CheckResponse:
    try:
        result = BgpVisibilityService(RipeStatClient(db)).check(payload.prefix, payload.expected_origin_as)
        response = _store_and_respond(db, "bgp-visibility", payload.prefix, payload.expected_origin_as, result, user.id, payload.change_case_id)
        write_audit_log(db, user_id=user.id, action='bgp_visibility_checked', target_type='check', target_id=str(response.report_id), details_json={'prefix': payload.prefix, 'expected_origin_as': payload.expected_origin_as, 'change_case_id': payload.change_case_id})
        return response
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"BGP visibility check failed: {exc}") from exc

@router.post('/roa-preflight', response_model=CheckResponse)
def check_roa_preflight(payload: RoaPreflightCheckRequest, db: Session = Depends(get_db), user=Depends(require_operator_or_admin)) -> CheckResponse:
    try:
        result = RoaPlannerService(RipeStatClient(db)).check(payload.prefix, payload.origin_as, payload.max_length)
        response = _store_and_respond(db, "roa-preflight", payload.prefix, payload.origin_as, result, user.id, payload.change_case_id)
        write_audit_log(db, user_id=user.id, action='roa_preflight_checked', target_type='check', target_id=str(response.report_id), details_json={'prefix': payload.prefix, 'origin_as': payload.origin_as, 'max_length': payload.max_length, 'change_case_id': payload.change_case_id})
        return response
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"ROA preflight check failed: {exc}") from exc


@router.post('/preflight', response_model=CheckResponse)
def check_preflight(payload: PreflightCheckRequest, db: Session = Depends(get_db), user=Depends(require_operator_or_admin)) -> CheckResponse:
    try:
        result = PreflightChecker(RipeStatClient(db)).check(payload.prefix, payload.planned_origin_as)
        return _store_and_respond(db, "preflight", payload.prefix, payload.planned_origin_as, result, user.id, payload.change_case_id)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Preflight check failed: {exc}") from exc


def _store_and_respond(db: Session, ctype: str, resource: str, origin_as: str | None, result: dict, user_id: int | None = None, change_case_id: int | None = None) -> CheckResponse:
    try:
        change_case = None
        if change_case_id is not None:
            change_case = db.query(ChangeCase).filter(ChangeCase.id == change_case_id).first()
            if not change_case:
                raise HTTPException(status_code=404, detail="Change Case not found")
        check = Check(check_type=ctype, input_resource=resource, origin_as=origin_as, status=result["status"], summary=result["summary"], created_by_user_id=user_id, change_case_id=change_case_id)
        db.add(check)
        db.commit()
        db.refresh(check)
        report_json, md, html = render_report({"check_id": check.id, "input_check_type": ctype, **result})
        report = Report(check_id=check.id, created_by_user_id=user_id, json_data=report_json, markdown=md, html=html)
        db.add(report)
        db.commit()
        db.refresh(report)
        write_audit_log(db, user_id=user_id, action='check_executed', target_type='check', target_id=str(check.id), details_json={'check_type': ctype, 'input_resource': resource, 'status': result.get('status')})
        write_audit_log(db, user_id=user_id, action='report_generated', target_type='report', target_id=str(report.id), details_json={'check_id': check.id, 'check_type': ctype})
        if change_case_id is not None:
            write_audit_log(db, user_id=user_id, action='check_attached_to_change_case', target_type='change_case', target_id=str(change_case_id), details_json={'check_id': check.id})
            write_audit_log(db, user_id=user_id, action='report_attached_to_change_case', target_type='change_case', target_id=str(change_case_id), details_json={'report_id': report.id})
        return CheckResponse(report_id=report.id, status=result["status"], summary=result["summary"], explanation=result.get("explanation"), risk=result.get("risk"), recommendations=result["recommendations"], input=result.get("input"), checks=result.get("checks"), details=result["details"], markdown=md, html=html)
    except OperationalError as exc:
        db.rollback()
        if "no column named created_by_user_id" in str(exc).lower():
            raise HTTPException(status_code=503, detail="Database schema is not up to date. Please run migrations: docker compose exec backend alembic upgrade head") from exc
        raise
