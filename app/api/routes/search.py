from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database.models import Article

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("")
def search_intelligence(
    q: str = Query(..., min_length=2, description="Search keyword"),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Full search across headlines, descriptions, summaries, and why-it-matters."""
    term = f"%{q.strip()}%"
    results = db.query(Article).filter(
        or_(
            Article.headline.ilike(term),
            Article.short_description.ilike(term),
            Article.summary_en.ilike(term),
            Article.why_it_matters_en.ilike(term),
            Article.summary_kn.ilike(term),
            Article.why_it_matters_kn.ilike(term)
        )
    ).order_by(Article.published_at.desc().nullslast()).limit(limit).all()

    articles = []
    for a in results:
        articles.append({
            "id": a.id,
            "headline": a.headline,
            "publisher": a.publisher,
            "original_url": a.original_url,
            "published_at": a.published_at.isoformat() if a.published_at else None,
            "summary_en": a.summary_en or a.short_description,
            "summary_kn": a.summary_kn or a.summary_en,
            "why_it_matters_en": a.why_it_matters_en,
            "why_it_matters_kn": a.why_it_matters_kn,
            "is_bookmarked": a.is_bookmarked,
            "categories": [{"id": c.id, "name_en": c.name_en, "name_kn": c.name_kn} for c in a.categories]
        })

    return {
        "query": q,
        "count": len(articles),
        "articles": articles
    }
