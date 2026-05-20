# SPDX-License-Identifier: AGPL-3.0-or-later
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_checks import router as checks_router
from app.api.routes_health import router as health_router
from app.api.routes_reports import router as reports_router
from app.api.routes_system import router as system_router
from app.config import settings
from app.core.system_status import database_type_from_url
from app.database import Base, engine

logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))
logger = logging.getLogger("routeforge")

app = FastAPI(title="RouteForge", version="0.5.5")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    if settings.database_url.startswith("sqlite"):
        Base.metadata.create_all(bind=engine)

    logger.info(
        "RouteForge startup: version=%s mode=%s database_type=%s read_only=%s ripestat_cache_ttl=%s ripestat_timeout=%s ripestat_retries=%s",
        app.version,
        "DEMO" if settings.demo_mode else "LIVE",
        database_type_from_url(settings.database_url),
        True,
        settings.cache_ttl_seconds,
        settings.ripestat_timeout_seconds,
        settings.ripestat_max_retries,
    )


app.include_router(health_router)
app.include_router(checks_router)
app.include_router(reports_router)

app.include_router(system_router)
