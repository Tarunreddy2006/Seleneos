from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.session import get_db
from app.database.models import Category, Article

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("")
def list_categories(db: Session = Depends(get_db)):
    """Lists all configured categories with their associated article counts."""
    categories = db.query(Category).filter(Category.is_active == True).order_by(Category.order_index).all()

    result = []
    for c in categories:
        art_count = len(c.articles)
        result.append({
            "id": c.id,
            "name_en": c.name_en,
            "name_kn": c.name_kn,
            "description": c.description,
            "order_index": c.order_index,
            "article_count": art_count
        })

    return {"categories": result}
