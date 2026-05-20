# SPDX-License-Identifier: AGPL-3.0-or-later
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_checks import router as checks_router
from app.api.routes_health import router as health_router
from app.api.routes_reports import router as reports_router
from app.api.routes_system import router as system_router
from app.config import settings
from app.database import Base, engine

app = FastAPI(title="RouteForge", version="0.5.3")

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


app.include_router(health_router)
app.include_router(checks_router)
app.include_router(reports_router)

app.include_router(system_router)
