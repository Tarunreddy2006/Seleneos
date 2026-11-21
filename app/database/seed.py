from sqlalchemy.orm import Session
from app.database.models import Category
from app.core.logging import logger

# The 7 core categories as defined in Master Specification Section 2
INITIAL_CATEGORIES = [
    {
        "id": "global-business",
        "name_en": "Global Business",
        "name_kn": "ಜಾಗತಿಕ ವ್ಯಾಪಾರ",
        "description": "International business, global markets, trade, startups, corporate investments.",
        "order_index": 1,
    },
    {
        "id": "global-politics",
        "name_en": "Global Politics",
        "name_kn": "ಜಾಗತಿಕ ರಾಜಕೀಯ",
        "description": "Geopolitics, international relations, conflicts, elections, diplomatic developments.",
        "order_index": 2,
    },
    {
        "id": "indian-politics",
        "name_en": "Indian Politics",
        "name_kn": "ಭಾರತೀಯ ರಾಜಕೀಯ",
        "description": "Central government, parliament, elections, public policies, national developments.",
        "order_index": 3,
    },
    {
        "id": "indian-economy",
        "name_en": "Indian Economy",
        "name_kn": "ಭಾರತೀಯ ಆರ್ಥಿಕತೆ",
        "description": "RBI monetary policy, inflation, banking, budget, economic reforms, trade.",
        "order_index": 4,
    },
    {
        "id": "karnataka-politics",
        "name_en": "Karnataka Politics",
        "name_kn": "ಕರ್ನಾಟಕ ರಾಜಕೀಯ",
        "description": "Karnataka government, state policies, assembly, budget, regional administration.",
        "order_index": 5,
    },
    {
        "id": "technology-science",
        "name_en": "Technology & Science",
        "name_kn": "ತಂತ್ರಜ್ಞಾನ ಮತ್ತು ವಿಜ್ಞಾನ",
        "description": "Artificial intelligence, space exploration, robotics, semiconductors, energy, science.",
        "order_index": 6,
    },
    {
        "id": "education",
        "name_en": "Education",
        "name_kn": "ಶಿಕ್ಷಣ",
        "description": "Education policy, universities, research, competitive exams, scholarships, skill development.",
        "order_index": 7,
    },
]


def seed_categories(db: Session) -> None:
    """Ensure all core categories exist in the database."""
    for cat_data in INITIAL_CATEGORIES:
        existing = db.query(Category).filter(Category.id == cat_data["id"]).first()
        if not existing:
            cat = Category(
                id=cat_data["id"],
                name_en=cat_data["name_en"],
                name_kn=cat_data["name_kn"],
                description=cat_data["description"],
                order_index=cat_data["order_index"],
                is_active=True
            )
            db.add(cat)
            logger.info("Seeded category: %s (%s)", cat_data["name_en"], cat_data["id"])
        else:
            # Update names or order index if needed
            existing.name_en = cat_data["name_en"]
            existing.name_kn = cat_data["name_kn"]
            existing.order_index = cat_data["order_index"]
    db.commit()
