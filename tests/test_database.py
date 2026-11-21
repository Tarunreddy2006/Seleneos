import pytest
from app.database.models import Category, Source, Article, EducationalTopic


def test_core_categories_seeded(db_session):
    """Ensure all 7 required news categories are present with EN and KN names."""
    categories = db_session.query(Category).order_by(Category.order_index).all()
    assert len(categories) == 7

    cat_map = {c.id: c for c in categories}
    expected_ids = [
        "global-business",
        "global-politics",
        "indian-politics",
        "indian-economy",
        "karnataka-politics",
        "technology-science",
        "education"
    ]
    for cid in expected_ids:
        assert cid in cat_map
        assert cat_map[cid].name_en != ""
        assert cat_map[cid].name_kn != ""


def test_article_model_and_category_relationship(db_session):
    """Ensure articles can be saved, linked to categories, and retrieved."""
    category = db_session.query(Category).filter_by(id="technology-science").first()
    assert category is not None

    article = Article(
        id="test-article-1",
        headline="Breakthrough in Quantum Computing Architecture",
        original_url="https://example.com/quantum-breakthrough",
        publisher="Science Daily",
        language="en",
        short_description="Researchers achieve fault-tolerant qubit coherence.",
        summary_en="Researchers achieve sustained coherence in silicon qubits.",
        summary_kn="ಕ್ವಾಂಟಮ್ ಕಂಪ್ಯೂಟಿಂಗ್ ಕ್ಷೇತ್ರದಲ್ಲಿ ಹೊಸ ಸಂಶೋಧನೆ ಸಾಧಿಸಲಾಗಿದೆ.",
        why_it_matters_en="Accelerates commercialization of fault-tolerant quantum algorithms.",
        why_it_matters_kn="ದೋಷ-ಸಹಿಷ್ಣು ಕ್ವಾಂಟಮ್ ಕಂಪ್ಯೂಟಿಂಗ್ ಅಭಿವೃದ್ಧಿಗೆ ವೇಗ ನೀಡುತ್ತದೆ."
    )
    article.categories.append(category)
    db_session.add(article)
    db_session.flush()

    retrieved = db_session.query(Article).filter_by(id="test-article-1").first()
    assert retrieved is not None
    assert retrieved.headline == "Breakthrough in Quantum Computing Architecture"
    assert len(retrieved.categories) == 1
    assert retrieved.categories[0].id == "technology-science"
    assert retrieved.summary_kn is not None
