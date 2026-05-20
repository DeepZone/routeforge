from fastapi import APIRouter

from app.config import settings

router = APIRouter(prefix='/api/system', tags=['system'])


@router.get('/info')
def system_info():
    return {
        'name': 'RouteForge',
        'version': 'v0.2.0-alpha',
        'demo_mode': settings.demo_mode,
        'read_only': True,
        'data_sources': ['RIPEstat', 'RIPEstat Whois/Registry'],
    }
