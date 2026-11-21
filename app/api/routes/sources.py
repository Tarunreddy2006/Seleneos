from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database.models import Source
from app.ingestion.collector import NewsCollector

router = APIRouter(prefix="/sources", tags=["Sources"])


@router.get("")
def list_sources(db: Session = Depends(get_db)):
    """Lists all configured news feeds with operational and health metrics."""
    sources = db.query(Source).all()
    return {
        "sources": [
            {
                "id": s.id,
                "name": s.name,
                "feed_url": s.feed_url,
                "default_category_id": s.default_category_id,
                "language": s.language,
                "is_enabled": s.is_enabled,
                "last_collected_at": s.last_collected_at.isoformat() if s.last_collected_at else None,
                "last_status": s.last_status,
                "consecutive_failures": s.consecutive_failures,
                "total_articles_collected": s.total_articles_collected,
                "last_error_message": s.last_error_message
            }
            for s in sources
        ]
    }


@router.post("/refresh")
async def trigger_manual_refresh(db: Session = Depends(get_db)):
    """Triggers an immediate manual news collection and processing run."""
    collector = NewsCollector(db)
    run = await collector.run_collection(trigger_type="manual")

    # Run intelligence pipeline on newly collected articles
    from app.intelligence.pipeline import IntelligencePipeline
    pipeline = IntelligencePipeline(db)
    processed_count = await pipeline.process_batch(limit=30)

    return {
        "run_id": run.id,
        "status": run.status,
        "articles_added": run.articles_added,
        "articles_deduplicated": run.articles_deduplicated,
        "articles_analyzed": processed_count,
        "sources_succeeded": run.sources_succeeded,
        "sources_failed": run.sources_failed
    }
