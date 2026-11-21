import pytest
from app.database.models import Article, Category, EducationalTopic
from app.education.seed_topics import seed_educational_topics


@pytest.fixture(autouse=True)
def seed_test_education(db_session):
    seed_educational_topics(db_session)


def test_list_articles_and_pagination(client, db_session):
    cat = db_session.query(Category).filter_by(id="indian-economy").first()
    art = Article(
        id="art-page-1",
        headline="Sensex rises 400 points as inflation cools",
        original_url="https://example.com/sensex-rises",
        publisher="Market Watch",
        language="en",
        short_description="Benchmark equity indices traded in the green.",
        summary_en="Sensex and Nifty posted gains.",
        summary_kn="ಸೆನ್ಸೆಕ್ಸ್ ಮತ್ತು ನಿಫ್ಟಿ ಏರಿಕೆ ಕಂಡಿವೆ."
    )
    if cat:
        art.categories.append(cat)
    db_session.add(art)
    db_session.commit()

    res = client.get("/api/articles?limit=10")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 1
    assert len(data["articles"]) >= 1


def test_article_detail_and_read_count(client, db_session):
    art = Article(
        id="art-read-1",
        headline="New Environmental Clearance Policy for Industries",
        original_url="https://example.com/env-policy",
        publisher="National Green Wire",
        language="en",
        short_description="Ministry of Environment revises rules.",
        summary_en="Revised environmental norms issued.",
        summary_kn="ಹೊಸ ಪರಿಸರ ನಿಯಮಾವಳಿಗಳು ಜಾರಿಯಾಗಿವೆ.",
        why_it_matters_en="Streamlines compliance for manufacturing plants.",
        why_it_matters_kn="ಉತ್ಪಾದನಾ ಘಟಕಗಳ ನಿಯಮಾವಳಿ ಸರಳಗೊಳಿಸುತ್ತದೆ.",
        read_count=0
    )
    db_session.add(art)
    db_session.commit()

    res = client.get("/api/articles/art-read-1")
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == "art-read-1"
    assert data["read_count"] == 1  # Incremented on view


def test_toggle_bookmark(client, db_session):
    art = Article(
        id="art-bm-1",
        headline="Breakthrough in Solar Cell Efficiency",
        original_url="https://example.com/solar-cell",
        publisher="Clean Energy News",
        language="en",
        is_bookmarked=False
    )
    db_session.add(art)
    db_session.commit()

    # Toggle to bookmarked
    res1 = client.post("/api/articles/art-bm-1/bookmark")
    assert res1.status_code == 200
    assert res1.json()["is_bookmarked"] is True

    # Toggle back
    res2 = client.post("/api/articles/art-bm-1/bookmark")
    assert res2.status_code == 200
    assert res2.json()["is_bookmarked"] is False


def test_search_intelligence(client, db_session):
    art = Article(
        id="art-search-1",
        headline="Karnataka Government Approves New Semiconductor Facility in Mysuru",
        original_url="https://example.com/mysuru-semi",
        publisher="State Wire",
        language="en",
        short_description="Semiconductor plant approved with state incentives."
    )
    db_session.add(art)
    db_session.commit()

    res = client.get("/api/search?q=Semiconductor")
    assert res.status_code == 200
    data = res.json()
    assert data["count"] >= 1
    assert any("Semiconductor" in a["headline"] for a in data["articles"])


def test_education_concept_of_the_day_and_topics(client):
    # Concept of the Day
    res = client.get("/api/education/concept-of-the-day")
    assert res.status_code == 200
    data = res.json()
    assert "title_en" in data
    assert "title_kn" in data
    assert len(data["terminology"]) > 0
    assert len(data["knowledge_check"]) > 0

    # Topic list
    res_list = client.get("/api/education/topics")
    assert res_list.status_code == 200
    topics = res_list.json()["topics"]
    assert len(topics) >= 2
