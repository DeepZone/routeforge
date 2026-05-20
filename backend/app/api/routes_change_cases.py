from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import require_role
from app.core.audit import write_audit_log
from app.database import get_db
from app.models import ChangeCase, Check, Report
from app.schemas import ChangeCaseCreate, ChangeCaseRead, ChangeCaseUpdate

router = APIRouter(prefix='/api/change-cases', tags=['change-cases'])
VALID = {'draft', 'in_review', 'approved', 'closed'}
TRANSITIONS = {
    'draft': {'in_review', 'closed'},
    'in_review': {'approved', 'draft', 'closed'},
    'approved': {'closed', 'in_review'},
    'closed': set(),
}

@router.get('')
def list_change_cases(db: Session = Depends(get_db), _=Depends(require_role('viewer','operator','admin'))):
    return db.query(ChangeCase).order_by(ChangeCase.updated_at.desc()).limit(100).all()

@router.post('', response_model=ChangeCaseRead)
def create_change_case(payload: ChangeCaseCreate, db: Session = Depends(get_db), user=Depends(require_role('operator','admin'))):
    cc = ChangeCase(title=payload.title.strip(), description=payload.description, status='draft', created_by_user_id=user.id)
    db.add(cc); db.commit(); db.refresh(cc)
    write_audit_log(db, user_id=user.id, action='change_case_created', target_type='change_case', target_id=str(cc.id), details_json={'status': cc.status})
    return cc

@router.get('/{change_case_id}', response_model=ChangeCaseRead)
def get_change_case(change_case_id: int, db: Session = Depends(get_db), _=Depends(require_role('viewer','operator','admin'))):
    cc = db.query(ChangeCase).filter(ChangeCase.id == change_case_id).first()
    if not cc: raise HTTPException(status_code=404, detail='Change Case not found')
    return cc

@router.patch('/{change_case_id}', response_model=ChangeCaseRead)
def patch_change_case(change_case_id: int, payload: ChangeCaseUpdate, db: Session = Depends(get_db), user=Depends(require_role('operator','admin'))):
    cc = db.query(ChangeCase).filter(ChangeCase.id == change_case_id).first()
    if not cc: raise HTTPException(status_code=404, detail='Change Case not found')
    old_status = cc.status
    if payload.title is not None: cc.title = payload.title.strip()
    if payload.description is not None: cc.description = payload.description
    if payload.status is not None:
        if payload.status not in VALID: raise HTTPException(status_code=400, detail='Invalid status')
        if payload.status != cc.status and payload.status not in TRANSITIONS.get(cc.status, set()):
            raise HTTPException(status_code=400, detail='Invalid status transition')
        cc.status = payload.status
    db.commit(); db.refresh(cc)
    write_audit_log(db, user_id=user.id, action='change_case_updated', target_type='change_case', target_id=str(cc.id), details_json={})
    if old_status != cc.status:
        write_audit_log(db, user_id=user.id, action='change_case_status_changed', target_type='change_case', target_id=str(cc.id), details_json={'from': old_status, 'to': cc.status})
    return cc

@router.get('/{change_case_id}/reports')
def list_change_case_reports(change_case_id: int, db: Session = Depends(get_db), _=Depends(require_role('viewer','operator','admin'))):
    cc = db.query(ChangeCase).filter(ChangeCase.id == change_case_id).first()
    if not cc: raise HTTPException(status_code=404, detail='Change Case not found')
    rows = db.query(Report, Check).join(Check, Report.check_id == Check.id).filter(Check.change_case_id == change_case_id).all()
    return [{'report_id': r.id, 'check_id': c.id, 'check_type': c.check_type, 'summary': c.summary, 'status': c.status, 'created_at': r.created_at.isoformat()} for r, c in rows]
