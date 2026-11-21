import asyncio
import datetime
import hashlib
import uuid
from typing import List, Dict, Any, Optional
import httpx
from sqlalchemy.orm import Session

from app.config import settings
from app.core.logging import logger
from app.database.models import Source, Article, CollectionRun, Category
from app.ingestion.rss_parser import parse_rss_feed, ParsedArticle
from app.ingestion.deduplicator import Deduplicator


class NewsCollector:
    """
    Asynchronous news collection engine.
    Collects RSS feeds from enabled sources with concurrency limits,
    retries, deduplication, and source health tracking.
    """

    def __init__(self, db: Session):
        self.db = db
        self.deduplicator = Deduplicator()

    async def collect_from_source(
        self,
        client: httpx.AsyncClient,
        source: Source,
        semaphore: asyncio.Semaphore
    ) -> Dict[str, Any]:
        """Collects articles from a single news source with timeout and error handling."""
        result = {
            "source_id": source.id,
            "success": False,
            "articles": [],
            "error": None
        }

        async with semaphore:
            try:
                headers = {"User-Agent": settings.USER_AGENT}
                response = await client.get(
                    source.feed_url,
                    headers=headers,
                    timeout=settings.REQUEST_TIMEOUT_SECONDS,
                    follow_redirects=True
                )

                if response.status_code == 200:
                    articles = parse_rss_feed(
                        feed_content=response.text,
                        source_name=source.name,
                        default_language=source.language
                    )
                    result["success"] = True
                    result["articles"] = articles
                else:
                    result["error"] = f"HTTP {response.status_code}"

            except httpx.TimeoutException:
                result["error"] = "Connection timed out"
            except httpx.RequestError as exc:
                result["error"] = f"Request failed: {str(exc)}"
            except Exception as exc:
                result["error"] = f"Unexpected error: {str(exc)}"

        return result

    async def run_collection(self, trigger_type: str = "scheduled") -> CollectionRun:
        """
        Executes full collection across all enabled sources.
        Persists results and returns the completed CollectionRun audit record.
        """
        run = CollectionRun(
            id=str(uuid.uuid4()),
            started_at=datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None),
            trigger_type=trigger_type,
            status="running"
        )
        self.db.add(run)
        self.db.commit()

        # Load active sources
        sources: List[Source] = self.db.query(Source).filter(Source.is_enabled == True).all()
        run.sources_attempted = len(sources)

        if not sources:
            run.status = "completed"
            run.completed_at = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
            self.db.commit()
            return run

        # Pre-fetch recent articles for event clustering (last 48 hours)
        cutoff_date = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) - datetime.timedelta(hours=48)
        recent_articles = self.db.query(Article).filter(Article.collected_at >= cutoff_date).all()

        semaphore = asyncio.Semaphore(settings.MAX_CONCURRENT_REQUESTS)
        async with httpx.AsyncClient() as client:
            tasks = [self.collect_from_source(client, src, semaphore) for src in sources]
            results = await asyncio.gather(*tasks, return_exceptions=False)

        source_map = {s.id: s for s in sources}
        errors_logged = []

        # Process results
        for res in results:
            src = source_map.get(res["source_id"])
            if not src:
                continue

            if res["success"]:
                src.last_status = "success"
                src.last_error_message = None
                src.consecutive_failures = 0
                src.last_collected_at = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
                run.sources_succeeded += 1

                for parsed in res["articles"]:
                    run.articles_fetched += 1

                    # Check exact duplicate
                    if self.deduplicator.is_exact_duplicate(self.db, parsed.canonical_url, parsed.content_hash):
                        run.articles_deduplicated += 1
                        continue

                    # Determine event cluster
                    cluster_id = self.deduplicator.find_cluster_or_create(
                        self.db,
                        parsed.headline,
                        recent_articles
                    )

                    # Create Article entity
                    article_id = hashlib.sha256(parsed.canonical_url.encode("utf-8")).hexdigest()[:32]
                    article = Article(
                        id=article_id,
                        headline=parsed.headline,
                        original_url=parsed.original_url,
                        canonical_url=parsed.canonical_url,
                        publisher=parsed.publisher,
                        published_at=parsed.published_at,
                        collected_at=datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None),
                        language=parsed.language,
                        short_description=parsed.short_description,
                        content_hash=parsed.content_hash,
                        cluster_id=cluster_id,
                        thumbnail_url=parsed.thumbnail_url,
                        source_id=src.id
                    )

                    # Associate default source category
                    if src.default_category:
                        article.categories.append(src.default_category)

                    self.db.add(article)
                    recent_articles.append(article)
                    src.total_articles_collected += 1
                    run.articles_added += 1

            else:
                src.last_status = "error"
                src.last_error_message = res["error"]
                src.consecutive_failures += 1
                run.sources_failed += 1
                errors_logged.append(f"{src.id}: {res['error']}")
                logger.warning("Source collection error for %s: %s", src.id, res["error"])

        run.completed_at = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
        run.status = "completed" if run.sources_failed == 0 else ("partial" if run.sources_succeeded > 0 else "failed")
        if errors_logged:
            run.error_log = "\n".join(errors_logged)

        self.db.commit()
        logger.info(
            "Collection run finished. Added: %d, Deduplicated: %d, Succeeded Sources: %d/%d",
            run.articles_added, run.articles_deduplicated, run.sources_succeeded, run.sources_attempted
        )
        return run
