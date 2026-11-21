import re
import hashlib
from typing import List, Tuple, Set
from sqlalchemy.orm import Session
from app.database.models import Article


def normalize_title_for_comparison(title: str) -> str:
    """Removes punctuation, numbers, and converts to lowercase tokens."""
    return re.sub(r"[^\w\s]", "", title.lower())


def calculate_jaccard_similarity(str1: str, str2: str) -> float:
    """Calculates token-based Jaccard similarity between two titles."""
    tokens1 = set(normalize_title_for_comparison(str1).split())
    tokens2 = set(normalize_title_for_comparison(str2).split())

    if not tokens1 or not tokens2:
        return 0.0

    intersection = len(tokens1.intersection(tokens2))
    union = len(tokens1.union(tokens2))
    return float(intersection) / float(union) if union > 0 else 0.0


class Deduplicator:
    """
    Identifies exact and near-duplicate news items across different publishers.
    Supports:
    1. Exact canonical URL matching.
    2. Content/Title hash matching.
    3. Title similarity clustering (Jaccard similarity threshold >= 0.65).
    """

    SIMILARITY_THRESHOLD = 0.65

    def is_exact_duplicate(self, db: Session, canonical_url: str, content_hash: str) -> bool:
        """Checks if an identical article is already persisted in the database."""
        existing = db.query(Article.id).filter(
            (Article.canonical_url == canonical_url) | (Article.content_hash == content_hash)
        ).first()
        return existing is not None

    def find_cluster_or_create(self, db: Session, headline: str, existing_recent_articles: List[Article]) -> str:
        """
        Determines if the article belongs to an existing event cluster
        by comparing its headline against recently collected articles (last 48 hours).
        Returns existing cluster_id if similarity >= 0.65, otherwise generates a new cluster_id.
        """
        for art in existing_recent_articles:
            if art.headline:
                sim = calculate_jaccard_similarity(headline, art.headline)
                if sim >= self.SIMILARITY_THRESHOLD:
                    return art.cluster_id or art.id

        # New distinct event
        new_cluster = hashlib.md5(headline.encode("utf-8")).hexdigest()[:16]
        return new_cluster
