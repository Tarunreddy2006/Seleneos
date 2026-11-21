from datetime import datetime, timezone
from fastapi import APIRouter, Depends, status
from sqlalchemy import text, func
from sqlalchemy.orm import Session

from app.config import settings
from app.database.session import get_db
from app.database.models import Article, Source, Category, CollectionRun

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", status_code=status.HTTP_200_OK)
def check_health(db: Session = Depends(get_db)):
    """
    Health and readiness probe.
    Verifies database connectivity, operational counts, and configuration state.
    """
    db_status = "connected"
    article_count = 0
    source_count = 0
    active_source_count = 0
    category_count = 0
    last_run_info = None

    try:
        # Check basic database query execution
        db.execute(text("SELECT 1"))

        # Gather quick counts
        article_count = db.query(func.count(Article.id)).scalar() or 0
        source_count = db.query(func.count(Source.id)).scalar() or 0
        active_source_count = db.query(func.count(Source.id)).filter(Source.is_enabled == True).scalar() or 0
        category_count = db.query(func.count(Category.id)).scalar() or 0

        # Retrieve last collection run
        last_run = db.query(CollectionRun).order_by(CollectionRun.started_at.desc()).first()
        if last_run:
            last_run_info = {
                "id": last_run.id,
                "status": last_run.status,
                "started_at": last_run.started_at.isoformat() if last_run.started_at else None,
                "completed_at": last_run.completed_at.isoformat() if last_run.completed_at else None,
                "articles_added": last_run.articles_added,
                "trigger_type": last_run.trigger_type
            }

    except Exception as exc:
        db_status = f"disconnected: {str(exc)}"

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "database": db_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "stats": {
            "articles": article_count,
            "sources_total": source_count,
            "sources_active": active_source_count,
            "categories": category_count,
            "last_collection": last_run_info
        },
        "briefing_schedule": {
            "morning_briefing": settings.MORNING_BRIEFING_TIME,
            "evening_briefing": settings.EVENING_BRIEFING_TIME,
            "timezone": settings.TIMEZONE,
            "auto_update_enabled": settings.AUTO_UPDATE_ENABLED
        },
        "providers": {
            "ai": settings.AI_PROVIDER,
            "translation": settings.TRANSLATION_PROVIDER
        }
    }
