from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import Settings, get_settings
from app.core.database import Database
from app.utils.exceptions import AppError
from app.utils.responses import error_response


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        database = Database(settings=app_settings)
        database.initialize()
        app.state.settings = app_settings
        app.state.database = database
        yield

    app = FastAPI(
        title=app_settings.app_name,
        debug=app_settings.debug,
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router)

    @app.exception_handler(AppError)
    async def handle_app_error(_, exc: AppError):
        return error_response(
            error_code=exc.error_code,
            message=exc.message,
            details=exc.details,
            status_code=exc.status_code,
        )

    return app


app = create_app()
