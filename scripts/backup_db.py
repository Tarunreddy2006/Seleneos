import shutil
import datetime
from pathlib import Path
from app.config import settings, BASE_DIR
from app.core.logging import logger


def backup_database() -> Path:
    """
    Creates a timestamped snapshot of the SQLite database.
    Retains up to 7 historical snapshots to conserve mobile storage.
    """
    db_file = settings.DATA_DIR / "daily_intelligence.db"
    backup_dir = settings.DATA_DIR / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)

    if not db_file.exists():
        logger.warning("Database file %s does not exist yet. Backup skipped.", db_file)
        return backup_dir

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"daily_intelligence_backup_{timestamp}.db"

    shutil.copy2(db_file, backup_file)
    logger.info("Created database backup: %s", backup_file)

    # Prune old backups (keep latest 7)
    backups = sorted(list(backup_dir.glob("daily_intelligence_backup_*.db")), key=lambda p: p.stat().st_mtime)
    if len(backups) > 7:
        for old_backup in backups[:-7]:
            try:
                old_backup.unlink()
                logger.info("Pruned old backup: %s", old_backup.name)
            except OSError as err:
                logger.warning("Failed to remove old backup: %s", err)

    return backup_file


if __name__ == "__main__":
    b_path = backup_database()
    print(f"Database backed up successfully to: {b_path}")
