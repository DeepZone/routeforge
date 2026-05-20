from fastapi import APIRouter

from app.config import settings
from app.core.system_status import build_system_status
from app.database import engine

router = APIRouter(prefix='/api/system', tags=['system'])


@router.get('/info')
def system_info():
    return {
        'name': 'RouteForge',
        'version': 'v0.5.2-beta',
        'demo_mode': settings.demo_mode,
        'read_only': True,
        'data_sources': ['RIPEstat', 'RIPEstat Whois/Registry'],
    }


@router.get('/status')
def system_status():
    return build_system_status(engine)
