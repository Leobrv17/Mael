from __future__ import annotations

from fastapi import FastAPI

from app.api import routes
from app.core.logging import setup_logging
from app.core.security import apply_middlewares

setup_logging()
app = FastAPI(title="SaaS Backend", version="1.0.0")
apply_middlewares(app)
app.include_router(routes.api_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
