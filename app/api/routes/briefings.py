from typing import Optional
from datetime import datetime, date, timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database.models import Briefing, BriefingItem, Article, Category

router = APIRouter(prefix="/briefings", tags=["Briefings"])


@router.get("/latest")
def get_latest_briefing(db: Session = Depends(get_db)):
    """Retrieves the most recent morning or evening intelligence briefing."""
    briefing = db.query(Briefing).order_by(Briefing.briefing_date.desc(), Briefing.created_at.desc()).first()
    if not briefing:
        return {
            "id": None,
            "briefing_type": "current",
            "date": date.today().isoformat(),
            "summary_en": "No formal briefing synthesized yet. New briefings are compiled at 6:00 AM and 6:00 PM IST.",
            "summary_kn": "ಇನ್ನೂ ಬ್ರೀಫಿಂಗ್ ಸಿದ್ಧಗೊಂಡಿಲ್ಲ. ಪ್ರತಿದಿನ ಬೆಳಗ್ಗೆ 6:00 ಮತ್ತು ಸಂಜೆ 6:00 ಕ್ಕೆ ಬ್ರೀಫಿಂಗ್ ಬಿಡುಗಡೆಯಾಗುತ್ತದೆ.",
            "articles": []
        }

    items = []
    for item in briefing.items:
        art = item.article
        if art:
            items.append({
                "id": art.id,
                "headline": art.headline,
                "publisher": art.publisher,
                "original_url": art.original_url,
                "summary_en": art.summary_en or art.short_description,
                "summary_kn": art.summary_kn or art.summary_en,
                "why_it_matters_en": art.why_it_matters_en,
                "why_it_matters_kn": art.why_it_matters_kn,
                "category_id": item.category_id
            })

    return {
        "id": briefing.id,
        "briefing_type": briefing.briefing_type,
        "date": briefing.briefing_date.isoformat(),
        "summary_en": briefing.summary_en,
        "summary_kn": briefing.summary_kn,
        "articles": items
    }
