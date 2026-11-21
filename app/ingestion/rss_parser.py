import datetime
import time
from typing import Optional, Dict, Any, List
import feedparser
from app.ingestion.normalizer import clean_html_text, canonicalize_url, generate_content_hash
from app.core.logging import logger


class ParsedArticle:
    def __init__(
        self,
        headline: str,
        original_url: str,
        canonical_url: str,
        publisher: str,
        published_at: Optional[datetime.datetime],
        short_description: str,
        content_hash: str,
        thumbnail_url: Optional[str] = None,
        language: str = "en"
    ):
        self.headline = headline
        self.original_url = original_url
        self.canonical_url = canonical_url
        self.publisher = publisher
        self.published_at = published_at
        self.short_description = short_description
        self.content_hash = content_hash
        self.thumbnail_url = thumbnail_url
        self.language = language

    def to_dict(self) -> Dict[str, Any]:
        return {
            "headline": self.headline,
            "original_url": self.original_url,
            "canonical_url": self.canonical_url,
            "publisher": self.publisher,
            "published_at": self.published_at,
            "short_description": self.short_description,
            "content_hash": self.content_hash,
            "thumbnail_url": self.thumbnail_url,
            "language": self.language
        }


def parse_rss_feed(feed_content: str, source_name: str, default_language: str = "en") -> List[ParsedArticle]:
    """
    Parses raw RSS/Atom feed XML using feedparser.
    Extracts article metadata, handles date formats, and normalizes excerpts.
    """
    articles: List[ParsedArticle] = []

    try:
        parsed = feedparser.parse(feed_content)
    except Exception as exc:
        logger.error("Failed to parse feed for source %s: %s", source_name, exc)
        return articles

    for entry in parsed.entries:
        headline = clean_html_text(entry.get("title", ""))
        original_url = entry.get("link", "").strip()

        if not headline or not original_url:
            continue

        canonical_url = canonicalize_url(original_url)

        # Parse publication date
        published_at = None
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            try:
                published_at = datetime.datetime.fromtimestamp(
                    time.mktime(entry.published_parsed),
                    tz=datetime.timezone.utc
                ).replace(tzinfo=None)
            except Exception:
                published_at = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
        elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
            try:
                published_at = datetime.datetime.fromtimestamp(
                    time.mktime(entry.updated_parsed),
                    tz=datetime.timezone.utc
                ).replace(tzinfo=None)
            except Exception:
                published_at = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)

        # Extract description / summary
        summary_raw = entry.get("summary", "") or entry.get("description", "")
        short_desc = clean_html_text(summary_raw)

        # Truncate short description reasonably
        if len(short_desc) > 500:
            short_desc = short_desc[:497] + "..."

        # Extract thumbnail if present (enclosures or media_content)
        thumbnail_url = None
        if hasattr(entry, "enclosures") and entry.enclosures:
            for enc in entry.enclosures:
                if enc.get("type", "").startswith("image/"):
                    thumbnail_url = enc.get("href")
                    break

        if not thumbnail_url and hasattr(entry, "media_content") and entry.media_content:
            for media in entry.media_content:
                if media.get("medium") == "image" or media.get("type", "").startswith("image/"):
                    thumbnail_url = media.get("url")
                    break

        content_hash = generate_content_hash(headline)

        article = ParsedArticle(
            headline=headline,
            original_url=original_url,
            canonical_url=canonical_url,
            publisher=source_name,
            published_at=published_at,
            short_description=short_desc,
            content_hash=content_hash,
            thumbnail_url=thumbnail_url,
            language=default_language
        )
        articles.append(article)

    return articles
