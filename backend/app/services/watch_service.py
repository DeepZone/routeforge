from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import ChangeCase, Check, Report, WatchRun, WatchTarget
from app.services.asn_checker import AsnChecker
from app.services.bgp_visibility_service import BgpVisibilityService
from app.services.prefix_checker import PrefixChecker
from app.services.report_renderer import render_report
from app.services.roa_planner_service import RoaPlannerService
from app.services.ripe_stat_client import RipeStatClient


class WatchService:
    def __init__(self, db: Session):
        self.db = db

    def run_target(self, target: WatchTarget, user_id: int | None = None) -> WatchRun:
        result, ctype, resource, origin = self._execute_check(target)
        check = Check(check_type=ctype, input_resource=resource, origin_as=origin, status=result["status"], summary=result["summary"], created_by_user_id=user_id, change_case_id=target.change_case_id)
        self.db.add(check)
        self.db.commit()
        self.db.refresh(check)
        report_json, md, html = render_report({"check_id": check.id, "input_check_type": ctype, **result})
        report = Report(check_id=check.id, created_by_user_id=user_id, json_data=report_json, markdown=md, html=html)
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)

        prev = target.last_status
        changed = prev is not None and prev != result["status"]
        run = WatchRun(watch_target_id=target.id, report_id=report.id, previous_status=prev, status=result["status"], changed=changed, summary=result["summary"])
        self.db.add(run)
        target.last_status = result["status"]
        target.last_run_at = datetime.utcnow()
        target.next_run_at = target.last_run_at + timedelta(minutes=target.interval_minutes)
        self.db.commit()
        self.db.refresh(run)
        return run

    def _execute_check(self, target: WatchTarget):
        client = RipeStatClient(self.db)
        if target.watch_type == "bgp_visibility":
            return BgpVisibilityService(client).check(target.prefix or "", target.expected_origin_as), "bgp-visibility", target.prefix or "", target.expected_origin_as
        if target.watch_type == "roa_preflight":
            return RoaPlannerService(client).check(target.prefix or "", target.origin_as or "", target.max_length), "roa-preflight", target.prefix or "", target.origin_as
        if target.watch_type == "prefix":
            return PrefixChecker(client).check(target.prefix or "", target.origin_as), "prefix", target.prefix or "", target.origin_as
        if target.watch_type == "asn":
            return AsnChecker(client).check(target.asn or ""), "asn", target.asn or "", None
        raise HTTPException(status_code=400, detail="Unsupported watch_type")
