import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from app.config import settings


def setup_logging() -> logging.Logger:
    """
    Configures structured logging for Daily Intelligence.
    Uses console output and a bounded rotating file handler
    to prevent runaway disk usage on Android / mobile devices.
    """
    logger = logging.getLogger("daily_intelligence")
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(log_level)

    # Avoid duplicate handlers on reload
    if logger.handlers:
        return logger

    log_format = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] [%(name)s:%(module)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)
    console_handler.setLevel(log_level)
    logger.addHandler(console_handler)

    # Rotating File Handler (Max 5MB per file, max 3 backups = 20MB max)
    log_file = settings.LOG_DIR / "daily_intelligence.log"
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8"
    )
    file_handler.setFormatter(log_format)
    file_handler.setLevel(log_level)
    logger.addHandler(file_handler)

    logger.info("Logging initialized at %s level (file: %s)", settings.LOG_LEVEL, log_file)
    return logger


logger = setup_logging()
