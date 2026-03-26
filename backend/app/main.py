"""Nexus Multi-Agent Task Orchestrator — FastAPI application."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()

    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )

    app = FastAPI(
        title="Nexus Orchestrator",
        description="Multi-agent task orchestration powered by Claude",
        version="1.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router)

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    return app


app = create_app()
