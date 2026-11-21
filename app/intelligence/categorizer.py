import re
from typing import List, Dict, Tuple, Any
from app.database.models import Category

# Configurable keyword taxonomy for the 7 core categories
CATEGORY_TAXONOMY: Dict[str, Dict[str, Any]] = {
    "global-business": {
        "keywords": [
            "market", "stocks", "wall street", "nasdaq", "trade", "startup", "invest",
            "acquisition", "merger", "revenue", "profit", "earnings", "ceo", "shares",
            "global market", "corporate", "venture", "industry", "supply chain", "multinational"
        ],
        "weight": 1.0
    },
    "global-politics": {
        "keywords": [
            "geopolitics", "diplomacy", "treaty", "united nations", "un security council",
            "nato", "sanctions", "war", "conflict", "foreign policy", "president", "prime minister",
            "summit", "ambassador", "white house", "kremlin", "pentagon", "bilateral", "ceasefire"
        ],
        "weight": 1.0
    },
    "indian-politics": {
        "keywords": [
            "lok sabha", "rajya sabha", "parliament", "bjp", "congress", "aap", "election commission",
            "supreme court of india", "delhi", "chief minister", "central government", "prime minister modi",
            "modi", "cabinet", "governor", "assembly election", "ordinance", "bill passed"
        ],
        "weight": 1.2
    },
    "indian-economy": {
        "keywords": [
            "rbi", "reserve bank of india", "repo rate", "inflation", "cpi", "gdp", "fiscal deficit",
            "rupee", "sensex", "nifty", "sebi", "banking", "finance ministry", "budget", "taxation",
            "gst", "monetary policy", "exports", "fdi", "current account"
        ],
        "weight": 1.2
    },
    "karnataka-politics": {
        "keywords": [
            "karnataka", "bengaluru", "bangalore", "vidhana soudha", "siddaramaiah", "dk shivakumar",
            "bbmp", "cauvery", "karnataka government", "karnataka assembly", "kannada", "mysuru",
            "belagavi", "hubballi", "mangaluru", "karnataka high court"
        ],
        "weight": 1.5  # Higher weight for regional relevance
    },
    "technology-science": {
        "keywords": [
            "artificial intelligence", "ai", "machine learning", "deep learning", "robotics",
            "space", "isro", "nasa", "satellite", "quantum", "semiconductor", "chips", "hardware",
            "software", "cybersecurity", "telescope", "physics", "biotechnology", "energy", "solar"
        ],
        "weight": 1.0
    },
    "education": {
        "keywords": [
            "education", "university", "ugc", "cbse", "ncert", "iit", "iim", "neet", "jee",
            "upsc", "scholarship", "higher education", "curriculum", "students", "campus",
            "research paper", "phd", "academic", "skill development", "schools"
        ],
        "weight": 1.2
    }
}


class RuleBasedCategorizer:
    """
    Deterministic rule-based article classifier.
    Scores text against taxonomy keywords without requiring AI.
    """

    def classify(self, headline: str, description: str = "") -> List[Tuple[str, float]]:
        """
        Returns list of (category_id, score) sorted by relevance score descending.
        Only categories with score > 0 are returned.
        """
        combined_text = f"{headline} {description}".lower()
        scores: List[Tuple[str, float]] = []

        for cat_id, data in CATEGORY_TAXONOMY.items():
            keywords = data["keywords"]
            weight = data["weight"]
            match_count = 0

            for kw in keywords:
                # Word boundary match
                pattern = r"\b" + re.escape(kw) + r"\b"
                matches = len(re.findall(pattern, combined_text))
                if matches > 0:
                    # Headline matches carry triple weight
                    headline_matches = len(re.findall(pattern, headline.lower()))
                    match_count += matches + (headline_matches * 2)

            if match_count > 0:
                score = round(match_count * weight, 2)
                scores.append((cat_id, score))

        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores
