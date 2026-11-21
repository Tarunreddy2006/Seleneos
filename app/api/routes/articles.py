from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.database.models import Article, Category, Source, article_categories

router = APIRouter(prefix="/articles", tags=["Articles"])


@router.get("")
def list_articles(
    category: Optional[str] = Query(None, description="Category slug"),
    bookmarked: Optional[bool] = Query(None, description="Filter bookmarked articles"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Paginated list of intelligence articles with category and bookmark filtering."""
    query = db.query(Article)

    if category and category != "all":
        query = query.join(Article.categories).filter(Category.id == category)

    if bookmarked is not None:
        query = query.filter(Article.is_bookmarked == bookmarked)

    total = query.count()
    articles = query.order_by(Article.published_at.desc().nullslast(), Article.collected_at.desc()) \
                    .offset((page - 1) * limit) \
                    .limit(limit) \
                    .all()

    items = []
    for a in articles:
        items.append({
            "id": a.id,
            "headline": a.headline,
            "original_url": a.original_url,
            "publisher": a.publisher,
            "published_at": a.published_at.isoformat() if a.published_at else None,
            "language": a.language,
            "short_description": a.short_description,
            "summary_en": a.summary_en,
            "summary_kn": a.summary_kn,
            "why_it_matters_en": a.why_it_matters_en,
            "why_it_matters_kn": a.why_it_matters_kn,
            "thumbnail_url": a.thumbnail_url,
            "is_bookmarked": a.is_bookmarked,
            "read_count": a.read_count,
            "categories": [{"id": c.id, "name_en": c.name_en, "name_kn": c.name_kn} for c in a.categories]
        })

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit,
        "articles": items
    }


@router.get("/{article_id}")
def get_article(article_id: str, db: Session = Depends(get_db)):
    """Detailed article view including background, facts, and connected educational topics."""
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

    # Increment read counter
    article.read_count += 1
    article.last_read_at = datetime.now(timezone.utc).replace(tzinfo=None)
    db.commit()

    import json
    facts = []
    if article.important_facts:
        try:
            facts = json.loads(article.important_facts)
        except Exception:
            pass

    return {
        "id": article.id,
        "headline": article.headline,
        "original_url": article.original_url,
        "publisher": article.publisher,
        "published_at": article.published_at.isoformat() if article.published_at else None,
        "language": article.language,
        "short_description": article.short_description,
        "summary_en": article.summary_en,
        "summary_kn": article.summary_kn,
        "detailed_summary_en": article.detailed_summary_en,
        "detailed_summary_kn": article.detailed_summary_kn,
        "why_it_matters_en": article.why_it_matters_en,
        "why_it_matters_kn": article.why_it_matters_kn,
        "background_en": article.background_en,
        "background_kn": article.background_kn,
        "important_facts": facts,
        "thumbnail_url": article.thumbnail_url,
        "is_bookmarked": article.is_bookmarked,
        "read_count": article.read_count,
        "categories": [{"id": c.id, "name_en": c.name_en, "name_kn": c.name_kn} for c in article.categories],
        "topics": [{"id": t.id, "title_en": t.title_en, "title_kn": t.title_kn} for t in article.topics]
    }


@router.post("/{article_id}/bookmark")
def toggle_bookmark(article_id: str, db: Session = Depends(get_db)):
    """Toggles bookmark status on an article."""
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

    article.is_bookmarked = not article.is_bookmarked
    article.bookmarked_at = datetime.now(timezone.utc).replace(tzinfo=None) if article.is_bookmarked else None
    db.commit()

    return {
        "id": article.id,
        "is_bookmarked": article.is_bookmarked
    }
