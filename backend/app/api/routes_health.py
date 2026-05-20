from fastapi import APIRouter

router = APIRouter()


@router.get('/health')
def health() -> dict:
    return {"status": "ok", "version": "v0.5.0-beta"}
