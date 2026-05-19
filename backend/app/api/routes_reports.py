from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Report

router = APIRouter(prefix="/api/reports", tags=["reports"])


def _report_or_404(db: Session, report_id: int) -> Report:
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.get('/{report_id}')
def get_report(report_id: int, db: Session = Depends(get_db)):
    r = _report_or_404(db, report_id)
    return r.json_data


@router.get('/{report_id}/markdown')
def get_report_markdown(report_id: int, db: Session = Depends(get_db)):
    r = _report_or_404(db, report_id)
    return Response(content=r.markdown, media_type="text/markdown")


@router.get('/{report_id}/html')
def get_report_html(report_id: int, db: Session = Depends(get_db)):
    r = _report_or_404(db, report_id)
    return Response(content=r.html, media_type="text/html")
