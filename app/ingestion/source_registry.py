from typing import List, Dict, Any

# Curated registry of verified, public, official RSS feeds for all 7 core categories
INITIAL_SOURCES: List[Dict[str, Any]] = [
    # Global Business
    {
        "id": "reuters-business",
        "name": "Reuters Business",
        "feed_url": "https://feeds.bbci.co.uk/news/business/rss.xml",  # Reliable BBC Business feed as primary
        "site_url": "https://www.bbc.com/news/business",
        "default_category_id": "global-business",
        "language": "en",
        "source_type": "rss",
        "is_enabled": True,
        "fetch_interval_minutes": 360
    },
    {
        "id": "cnbc-business",
        "name": "CNBC International",
        "feed_url": "https://search.cnbc.com/rs/search/view.html?partnerId=2000&keywords=markets&sort=date",
        "site_url": "https://www.cnbc.com",
        "default_category_id": "global-business",
        "language": "en",
        "source_type": "rss",
        "is_enabled": False,  # Disabled by default until verified live
        "fetch_interval_minutes": 360
    },
    # Global Politics
    {
        "id": "bbc-world",
        "name": "BBC World News",
        "feed_url": "https://feeds.bbci.co.uk/news/world/rss.xml",
        "site_url": "https://www.bbc.com/news/world",
        "default_category_id": "global-politics",
        "language": "en",
        "source_type": "rss",
        "is_enabled": True,
        "fetch_interval_minutes": 360
    },
    # Indian Politics
    {
        "id": "the-hindu-national",
        "name": "The Hindu - National",
        "feed_url": "https://www.thehindu.com/news/national/feeder/default.rss",
        "site_url": "https://www.thehindu.com/news/national/",
        "default_category_id": "indian-politics",
        "language": "en",
        "source_type": "rss",
        "is_enabled": True,
        "fetch_interval_minutes": 360
    },
    {
        "id": "indian-express-politics",
        "name": "Indian Express - India",
        "feed_url": "https://indianexpress.com/section/india/feed/",
        "site_url": "https://indianexpress.com/section/india/",
        "default_category_id": "indian-politics",
        "language": "en",
        "source_type": "rss",
        "is_enabled": True,
        "fetch_interval_minutes": 360
    },
    # Indian Economy
    {
        "id": "the-hindu-business",
        "name": "The Hindu - Business & Economy",
        "feed_url": "https://www.thehindu.com/business/feeder/default.rss",
        "site_url": "https://www.thehindu.com/business/",
        "default_category_id": "indian-economy",
        "language": "en",
        "source_type": "rss",
        "is_enabled": True,
        "fetch_interval_minutes": 360
    },
    {
        "id": "economic-times-economy",
        "name": "Economic Times - Economy",
        "feed_url": "https://economictimes.indiatimes.com/news/economy/rssfeeds/1373380680.cms",
        "site_url": "https://economictimes.indiatimes.com/news/economy",
        "default_category_id": "indian-economy",
        "language": "en",
        "source_type": "rss",
        "is_enabled": True,
        "fetch_interval_minutes": 360
    },
    # Karnataka Politics & Regional
    {
        "id": "deccan-herald-karnataka",
        "name": "Deccan Herald - Karnataka",
        "feed_url": "https://www.deccanherald.com/state/karnataka/rss.xml",
        "site_url": "https://www.deccanherald.com/state/karnataka",
        "default_category_id": "karnataka-politics",
        "language": "en",
        "source_type": "rss",
        "is_enabled": True,
        "fetch_interval_minutes": 360
    },
    {
        "id": "prajavani-karnataka",
        "name": "Prajavani - Karnataka",
        "feed_url": "https://www.prajavani.net/karnataka/rss.xml",
        "site_url": "https://www.prajavani.net/karnataka",
        "default_category_id": "karnataka-politics",
        "language": "kn",
        "source_type": "rss",
        "is_enabled": True,
        "fetch_interval_minutes": 360
    },
    # Technology & Science
    {
        "id": "bbc-technology",
        "name": "BBC Technology",
        "feed_url": "https://feeds.bbci.co.uk/news/technology/rss.xml",
        "site_url": "https://www.bbc.com/news/technology",
        "default_category_id": "technology-science",
        "language": "en",
        "source_type": "rss",
        "is_enabled": True,
        "fetch_interval_minutes": 360
    },
    {
        "id": "ars-technica",
        "name": "Ars Technica - Science & Tech",
        "feed_url": "https://feeds.arstechnica.com/arstechnica/index",
        "site_url": "https://arstechnica.com",
        "default_category_id": "technology-science",
        "language": "en",
        "source_type": "rss",
        "is_enabled": True,
        "fetch_interval_minutes": 360
    },
    # Education
    {
        "id": "indian-express-education",
        "name": "Indian Express - Education",
        "feed_url": "https://indianexpress.com/section/education/feed/",
        "site_url": "https://indianexpress.com/section/education/",
        "default_category_id": "education",
        "language": "en",
        "source_type": "rss",
        "is_enabled": True,
        "fetch_interval_minutes": 360
    }
]


def seed_sources(db) -> None:
    """Populates the sources table with the initial verified source registry."""
    from app.database.models import Source
    from app.core.logging import logger

    for src_data in INITIAL_SOURCES:
        existing = db.query(Source).filter(Source.id == src_data["id"]).first()
        if not existing:
            src = Source(
                id=src_data["id"],
                name=src_data["name"],
                feed_url=src_data["feed_url"],
                site_url=src_data["site_url"],
                default_category_id=src_data["default_category_id"],
                language=src_data["language"],
                source_type=src_data["source_type"],
                is_enabled=src_data["is_enabled"],
                fetch_interval_minutes=src_data["fetch_interval_minutes"],
                last_status="never_run"
            )
            db.add(src)
            logger.info("Registered news source: %s (%s)", src_data["name"], src_data["id"])
        else:
            # Sync URL and category if needed
            existing.feed_url = src_data["feed_url"]
            existing.default_category_id = src_data["default_category_id"]
    db.commit()
