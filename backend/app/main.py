from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .legacy.api import create_router
from .legacy.db import Database
from .legacy.orchestrator import Orchestrator
from .legacy.repository import Repository


db = Database()
db.init()
repo = Repository(db)
orchestrator = Orchestrator(repo)

app = FastAPI(title="AI Delivery Engine MVP", version="2.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(create_router(repo, orchestrator))


@app.get("/health")
def health() -> dict[str, object]:
    return {"success": True, "message": "ok", "data": {"status": "healthy"}}


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, KeyError):
        code = str(exc).strip("'")
        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "error_code": code,
                "message": "资源不存在",
                "details": {},
            },
        )
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": str(exc),
            "details": {"path": str(request.url.path)},
        },
    )
