"""FastAPI application entrypoint."""

from __future__ import annotations

import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app import __version__
from app.api import router as system_router
from app.api.campaigns import router as campaigns_router
from app.api.documents import router as documents_router
from app.config import get_settings
from app.database import init_db

APP_DIR = Path(__file__).resolve().parent


def configure_logging() -> None:
    settings = get_settings()
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )


def create_app() -> FastAPI:
    configure_logging()
    settings = get_settings()

    app = FastAPI(
        title="Local AI Dungeon Master",
        version=__version__,
        description="Self-hosted AI DM — Milestone 2 (RAG)",
    )

    app.include_router(system_router)
    app.include_router(campaigns_router)
    app.include_router(documents_router)

    static_dir = APP_DIR / "static"
    templates_dir = APP_DIR / "templates"
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    templates = Jinja2Templates(directory=str(templates_dir))

    @app.on_event("startup")
    def _startup() -> None:
        init_db()
        logging.getLogger(__name__).info(
            "AI DM started (debug_panel=%s, model=%s)",
            settings.dm_debug_panel,
            settings.ollama_model,
        )

    @app.get("/", response_class=HTMLResponse)
    def index(request: Request) -> HTMLResponse:
        # Starlette 1.x: TemplateResponse(request, name, context)
        return templates.TemplateResponse(
            request,
            "index.html",
            {
                "dm_debug_panel": settings.dm_debug_panel,
                "version": __version__,
            },
        )

    @app.get("/campaign/{campaign_id}", response_class=HTMLResponse)
    def campaign_page(request: Request, campaign_id: str) -> HTMLResponse:
        return templates.TemplateResponse(
            request,
            "campaign.html",
            {
                "campaign_id": campaign_id,
                "dm_debug_panel": settings.dm_debug_panel,
                "version": __version__,
            },
        )

    return app


app = create_app()
