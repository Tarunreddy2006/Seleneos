from fastapi import APIRouter
from app.api.routes.health import router as health_router
from app.api.routes.articles import router as articles_router
from app.api.routes.categories import router as categories_router
from app.api.routes.briefings import router as briefings_router
from app.api.routes.search import router as search_router
from app.api.routes.sources import router as sources_router
from app.api.routes.education import router as education_router

api_router = APIRouter(prefix="/api")
api_router.include_router(health_router)
api_router.include_router(articles_router)
api_router.include_router(categories_router)
api_router.include_router(briefings_router)
api_router.include_router(search_router)
api_router.include_router(sources_router)
api_router.include_router(education_router)

__all__ = ["api_router"]
