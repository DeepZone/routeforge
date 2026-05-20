from fastapi import APIRouter

from app.core.system_status import get_database_status
from app.database import engine

router = APIRouter()


@router.get('/health')
def health() -> dict:
    return {"status": "ok", "version": "v0.9.1-rc", "database": get_database_status(engine).get("status", "unknown")}
