from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.core.auth import require_role
from app.database import get_db
from app.models import Check, Report
from app.services.report_renderer import render_plain_summary

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get('')
def list_reports(db: Session = Depends(get_db), _=Depends(require_role('viewer', 'operator', 'admin'))):
    rows = (
        db.query(Report, Check)
        .join(Check, Report.check_id == Check.id)
        .order_by(Report.created_at.desc())
        .limit(50)
        .all()
    )
    return [
        {
            'report_id': report.id,
            'check_id': check.id,
            'check_type': check.check_type,
            'input_resource': check.input_resource,
            'origin_as': check.origin_as,
            'status': check.status,
            'summary': check.summary,
            'holder': ((report.json_data or {}).get('details', {}).get('resource_holder', {}) or {}).get('holder'),
            'created_at': report.created_at.isoformat(),
        }
        for report, check in rows
    ]

def _report_or_404(db: Session, report_id: int) -> Report:
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

@router.get('/{report_id}')
def get_report(report_id: int, db: Session = Depends(get_db), _=Depends(require_role('viewer', 'operator', 'admin'))):
    r = _report_or_404(db, report_id)
    return r.json_data

@router.get('/{report_id}/markdown')
def get_report_markdown(report_id: int, db: Session = Depends(get_db), _=Depends(require_role('viewer', 'operator', 'admin'))):
    r = _report_or_404(db, report_id)
    return Response(content=r.markdown, media_type="text/markdown; charset=utf-8", headers={"Content-Disposition": f'attachment; filename="routeforge-report-{report_id}.md"'})

@router.get('/{report_id}/html')
def get_report_html(report_id: int, db: Session = Depends(get_db), _=Depends(require_role('viewer', 'operator', 'admin'))):
    r = _report_or_404(db, report_id)
    return Response(content=r.html, media_type="text/html; charset=utf-8", headers={"Content-Disposition": f'attachment; filename="routeforge-report-{report_id}.html"'})

@router.get('/{report_id}/summary')
def get_report_summary(report_id: int, db: Session = Depends(get_db), _=Depends(require_role('viewer', 'operator', 'admin'))):
    r = _report_or_404(db, report_id)
    return Response(content=render_plain_summary(r.json_data or {}), media_type="text/plain; charset=utf-8", headers={"Content-Disposition": f'attachment; filename="routeforge-summary-{report_id}.txt"'})
