from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database.models import EducationalTopic
import json

router = APIRouter(prefix="/education", tags=["Education"])


@router.get("/concept-of-the-day")
def get_concept_of_the_day(db: Session = Depends(get_db)):
    """Retrieves the featured Concept of the Day."""
    topic = db.query(EducationalTopic).filter(EducationalTopic.is_featured == True).first()
    if not topic:
        topic = db.query(EducationalTopic).first()

    if not topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No educational topics found")

    terminology = []
    if topic.important_terminology:
        try:
            terminology = json.loads(topic.important_terminology)
        except Exception:
            pass

    quiz = []
    if topic.knowledge_check:
        try:
            quiz = json.loads(topic.knowledge_check)
        except Exception:
            pass

    return {
        "id": topic.id,
        "title_en": topic.title_en,
        "title_kn": topic.title_kn,
        "category_id": topic.category_id,
        "simple_definition_en": topic.simple_definition_en,
        "simple_definition_kn": topic.simple_definition_kn,
        "background_en": topic.background_en,
        "background_kn": topic.background_kn,
        "how_it_works_en": topic.how_it_works_en,
        "how_it_works_kn": topic.how_it_works_kn,
        "real_world_example_en": topic.real_world_example_en,
        "real_world_example_kn": topic.real_world_example_kn,
        "current_events_connection_en": topic.current_events_connection_en,
        "current_events_connection_kn": topic.current_events_connection_kn,
        "terminology": terminology,
        "knowledge_check": quiz
    }


@router.get("/topics")
def list_topics(db: Session = Depends(get_db)):
    """Lists all educational concepts available in the knowledge library."""
    topics = db.query(EducationalTopic).order_by(EducationalTopic.created_at.desc()).all()
    return {
        "topics": [
            {
                "id": t.id,
                "title_en": t.title_en,
                "title_kn": t.title_kn,
                "category_id": t.category_id,
                "is_featured": t.is_featured
            }
            for t in topics
        ]
    }


@router.get("/topics/{topic_id}")
def get_topic_detail(topic_id: str, db: Session = Depends(get_db)):
    """Full detail for an educational topic, including glossary and knowledge-check."""
    topic = db.query(EducationalTopic).filter(EducationalTopic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found")

    terminology = []
    if topic.important_terminology:
        try:
            terminology = json.loads(topic.important_terminology)
        except Exception:
            pass

    quiz = []
    if topic.knowledge_check:
        try:
            quiz = json.loads(topic.knowledge_check)
        except Exception:
            pass

    return {
        "id": topic.id,
        "title_en": topic.title_en,
        "title_kn": topic.title_kn,
        "category_id": topic.category_id,
        "simple_definition_en": topic.simple_definition_en,
        "simple_definition_kn": topic.simple_definition_kn,
        "background_en": topic.background_en,
        "background_kn": topic.background_kn,
        "how_it_works_en": topic.how_it_works_en,
        "how_it_works_kn": topic.how_it_works_kn,
        "real_world_example_en": topic.real_world_example_en,
        "real_world_example_kn": topic.real_world_example_kn,
        "current_events_connection_en": topic.current_events_connection_en,
        "current_events_connection_kn": topic.current_events_connection_kn,
        "terminology": terminology,
        "knowledge_check": quiz
    }
