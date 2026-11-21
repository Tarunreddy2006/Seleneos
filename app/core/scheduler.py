import asyncio
import datetime
from zoneinfo import ZoneInfo
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session

from app.config import settings
from app.core.logging import logger
from app.database.session import SessionLocal
from app.database.models import Briefing, BriefingItem, Article, Category, CollectionRun
from app.ingestion.collector import NewsCollector
from app.intelligence.pipeline import IntelligencePipeline

# Timezone object for Asia/Kolkata
IST_TZ = ZoneInfo(settings.TIMEZONE)

# Lock to prevent overlapping runs
_collection_lock = asyncio.Lock()


async def execute_briefing_job(briefing_type: str = "scheduled") -> None:
    """
    Core briefing task:
    1. Runs async news collection across all active sources.
    2. Runs intelligence pipeline (categorization, summarization, Kannada translation).
    3. Synthesizes formal Morning or Evening Briefing record.
    """
    if _collection_lock.locked():
        logger.info("Collection job already in progress, skipping overlapping execution.")
        return

    async with _collection_lock:
        logger.info("Executing scheduled briefing job: %s...", briefing_type)
        with SessionLocal() as db:
            try:
                # 1. Ingestion
                collector = NewsCollector(db)
                run = await collector.run_collection(trigger_type=briefing_type)

                # 2. Intelligence processing
                pipeline = IntelligencePipeline(db)
                await pipeline.process_batch(limit=40)

                # 3. Briefing Synthesis
                now_ist = datetime.datetime.now(IST_TZ)
                briefing_date = now_ist.date()
                edition = "morning" if now_ist.hour < 12 else "evening"
                briefing_id = f"briefing-{briefing_date.isoformat()}-{edition}"

                existing_briefing = db.query(Briefing).filter(Briefing.id == briefing_id).first()
                if not existing_briefing:
                    # Select top recent articles
                    recent_articles = db.query(Article).order_by(Article.published_at.desc().nullslast()).limit(15).all()

                    summary_en = (
                        f"{edition.capitalize()} Briefing for {briefing_date.strftime('%B %d, %Y')}. "
                        f"Synthesized coverage across {run.sources_succeeded} verified publishers with {len(recent_articles)} top developments."
                    )
                    summary_kn = (
                        f"{briefing_date.strftime('%d-%m-%Y')} ರ {edition} ಬ್ರೀಫಿಂಗ್. "
                        f"{run.sources_succeeded} ಅಧಿಕೃತ ಮೂಲಗಳಿಂದ ಪ್ರಮುಖ ಬೆಳವಣಿಗೆಗಳ ಸಾರಾಂಶ."
                    )

                    briefing = Briefing(
                        id=briefing_id,
                        briefing_type=edition,
                        briefing_date=briefing_date,
                        summary_en=summary_en,
                        summary_kn=summary_kn,
                        article_count=len(recent_articles)
                    )
                    db.add(briefing)

                    for idx, art in enumerate(recent_articles):
                        cat_id = art.categories[0].id if art.categories else "global-business"
                        item = BriefingItem(
                            briefing_id=briefing.id,
                            article_id=art.id,
                            category_id=cat_id,
                            order_index=idx
                        )
                        db.add(item)

                    db.commit()
                    logger.info("Successfully synthesized briefing: %s", briefing_id)

            except Exception as exc:
                logger.error("Error in briefing job: %s", exc, exc_info=True)


async def check_and_recover_missed_briefings() -> None:
    """
    Evaluates whether an automatic briefing was missed during shutdown or restart
    (critical for Android background recovery).
    """
    with SessionLocal() as db:
        last_run = db.query(CollectionRun).order_by(CollectionRun.started_at.desc()).first()

        now_utc = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
        should_run = False

        if not last_run:
            should_run = True
            logger.info("No prior collection found. Triggering initial collection.")
        else:
            time_since_last = now_utc - last_run.started_at
            # If last run was more than 12 hours ago, run missed briefing recovery
            if time_since_last > datetime.timedelta(hours=12):
                should_run = True
                logger.info("Last collection was %s ago (>12h). Triggering missed recovery job.", time_since_last)

        if should_run:
            asyncio.create_task(execute_briefing_job("restart_recovery"))


class DailyIntelligenceScheduler:
    """APScheduler manager running 6 AM and 6 PM IST cron briefings."""

    def __init__(self):
        self.scheduler = AsyncIOScheduler(timezone=IST_TZ)

    def start(self) -> None:
        if not settings.AUTO_UPDATE_ENABLED:
            logger.info("Automated scheduler is disabled via configuration.")
            return

        # Morning Briefing: 6:00 AM IST
        self.scheduler.add_job(
            execute_briefing_job,
            CronTrigger(hour=6, minute=0, timezone=IST_TZ),
            args=["morning_cron"],
            id="morning_briefing_job",
            replace_existing=True
        )

        # Evening Briefing: 6:00 PM (18:00) IST
        self.scheduler.add_job(
            execute_briefing_job,
            CronTrigger(hour=18, minute=0, timezone=IST_TZ),
            args=["evening_cron"],
            id="evening_briefing_job",
            replace_existing=True
        )

        self.scheduler.start()
        logger.info(
            "Scheduler active: Morning briefing at 06:00 IST, Evening briefing at 18:00 IST (%s)",
            settings.TIMEZONE
        )

    def shutdown(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            logger.info("Scheduler stopped cleanly.")


scheduler_service = DailyIntelligenceScheduler()
