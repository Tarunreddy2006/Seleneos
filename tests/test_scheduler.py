import pytest
from app.core.scheduler import DailyIntelligenceScheduler, IST_TZ
from scripts.backup_db import backup_database
from app.config import settings


@pytest.mark.asyncio
async def test_scheduler_cron_triggers():
    scheduler = DailyIntelligenceScheduler()
    # Check timezone
    assert scheduler.scheduler.timezone == IST_TZ

    # Check job definitions
    scheduler.start()
    jobs = scheduler.scheduler.get_jobs()
    job_ids = [j.id for j in jobs]
    assert "morning_briefing_job" in job_ids
    assert "evening_briefing_job" in job_ids

    scheduler.shutdown()


def test_database_backup_execution(tmp_path):
    # Ensure backup function executes without error
    backup_file = backup_database()
    assert backup_file is not None
