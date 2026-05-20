from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import require_authenticated_user, require_operator_or_admin
from app.core.audit import write_audit_log
from app.database import get_db
from app.models import ChangeCase, WatchRun, WatchTarget
from app.schemas import WatchRunRead, WatchTargetCreate, WatchTargetRead, WatchTargetUpdate
from app.services.watch_service import WatchService

router = APIRouter(prefix='/api/watch-targets', tags=['watch'])

@router.get('', response_model=list[WatchTargetRead])
def list_targets(db: Session = Depends(get_db), user=Depends(require_authenticated_user)):
    return db.query(WatchTarget).order_by(WatchTarget.created_at.desc()).all()

@router.post('', response_model=WatchTargetRead)
def create_target(payload: WatchTargetCreate, db: Session = Depends(get_db), user=Depends(require_operator_or_admin)):
    if payload.change_case_id is not None and not db.query(ChangeCase).filter(ChangeCase.id == payload.change_case_id).first():
        raise HTTPException(status_code=404, detail='Change Case not found')
    target = WatchTarget(**payload.model_dump(), created_by_user_id=user.id)
    db.add(target); db.commit(); db.refresh(target)
    write_audit_log(db, user_id=user.id, action='watch_target_created', target_type='watch_target', target_id=str(target.id), details_json={'watch_type': target.watch_type})
    return target

@router.get('/{target_id}', response_model=WatchTargetRead)
def get_target(target_id:int, db:Session=Depends(get_db), user=Depends(require_authenticated_user)):
    t=db.query(WatchTarget).filter(WatchTarget.id==target_id).first()
    if not t: raise HTTPException(status_code=404, detail='Watch target not found')
    return t

@router.patch('/{target_id}', response_model=WatchTargetRead)
def patch_target(target_id:int,payload:WatchTargetUpdate,db:Session=Depends(get_db),user=Depends(require_operator_or_admin)):
    t=db.query(WatchTarget).filter(WatchTarget.id==target_id).first()
    if not t: raise HTTPException(status_code=404, detail='Watch target not found')
    for k,v in payload.model_dump(exclude_unset=True).items(): setattr(t,k,v)
    db.commit(); db.refresh(t)
    write_audit_log(db, user_id=user.id, action='watch_target_updated', target_type='watch_target', target_id=str(t.id), details_json={})
    return t

@router.delete('/{target_id}')
def delete_target(target_id:int, db:Session=Depends(get_db), user=Depends(require_operator_or_admin)):
    t=db.query(WatchTarget).filter(WatchTarget.id==target_id).first()
    if not t: raise HTTPException(status_code=404, detail='Watch target not found')
    db.delete(t); db.commit()
    write_audit_log(db, user_id=user.id, action='watch_target_deleted', target_type='watch_target', target_id=str(target_id), details_json={})
    return {'ok': True}

@router.get('/{target_id}/runs', response_model=list[WatchRunRead])
def list_runs(target_id:int, db:Session=Depends(get_db), user=Depends(require_authenticated_user)):
    return db.query(WatchRun).filter(WatchRun.watch_target_id==target_id).order_by(WatchRun.created_at.desc()).all()

@router.post('/{target_id}/run', response_model=WatchRunRead)
def run_target(target_id:int, db:Session=Depends(get_db), user=Depends(require_operator_or_admin)):
    t=db.query(WatchTarget).filter(WatchTarget.id==target_id).first()
    if not t: raise HTTPException(status_code=404, detail='Watch target not found')
    run=WatchService(db).run_target(t, user.id)
    write_audit_log(db, user_id=user.id, action='watch_target_run', target_type='watch_target', target_id=str(target_id), details_json={'run_id': run.id})
    if run.changed: write_audit_log(db, user_id=user.id, action='watch_target_status_changed', target_type='watch_target', target_id=str(target_id), details_json={'previous_status': run.previous_status, 'status': run.status})
    return run

@router.post('/run-due')
def run_due(db:Session=Depends(get_db), user=Depends(require_operator_or_admin)):
    now=datetime.utcnow(); targets=db.query(WatchTarget).filter(WatchTarget.is_active==True).all()
    due=[t for t in targets if t.next_run_at is None or t.next_run_at <= now]
    results=[]; changed=0; failed=0
    for t in due:
        try:
            run=WatchService(db).run_target(t, user.id)
            results.append({'watch_target_id': t.id, 'run_id': run.id, 'status': run.status, 'changed': run.changed})
            if run.changed: changed += 1
        except Exception as exc:
            failed += 1; results.append({'watch_target_id': t.id, 'error': str(exc)})
    write_audit_log(db, user_id=user.id, action='watch_targets_run_due', target_type='watch_target', target_id=None, details_json={'executed': len(due), 'changed': changed, 'failed': failed})
    return {'executed': len(due), 'changed': changed, 'failed': failed, 'results': results}
