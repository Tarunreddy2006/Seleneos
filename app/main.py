from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config import settings, BASE_DIR
from app.core.logging import logger
from app.database.session import init_db, SessionLocal
from app.database.seed import seed_categories
from app.api.routes import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle orchestrator.
    Initializes database schema, seeds core categories,
    and sets up background services.
    """
    logger.info("Starting %s v%s in %s mode...", settings.APP_NAME, settings.APP_VERSION, settings.APP_ENV)

    if settings.APP_ENV != "testing":
        try:
            init_db()
            with SessionLocal() as db:
                seed_categories(db)
            logger.info("Database and core categories initialized successfully.")
        except Exception as exc:
            logger.error("Failed to initialize database: %s", exc, exc_info=True)
            raise

    yield

    logger.info("Shutting down %s...", settings.APP_NAME)


def create_app() -> FastAPI:
    """FastAPI application factory."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Personal News and Knowledge Intelligence Platform",
        lifespan=lifespan,
        docs_url="/api/docs" if settings.DEBUG else None,
        redoc_url=None
    )

    # Include API Routers
    app.include_router(api_router)

    # Mount static assets from frontend
    frontend_dir = BASE_DIR / "app" / "frontend"
    if frontend_dir.exists():
        app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

    # Serve Main Frontend SPA Shell
    @app.get("/", include_in_schema=False)
    async def serve_index():
        index_file = frontend_dir / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        return {"message": f"{settings.APP_NAME} API running"}

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
