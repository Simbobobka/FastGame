import logging
import logging.handlers
import sys
from pathlib import Path

from Scrapers.settings import LoggingConfig, get_config

config = get_config(LoggingConfig)

CURRENT_DIR = Path(__file__).resolve().parent
logs_dir = CURRENT_DIR / config.output_dir
logs_dir.mkdir(exist_ok=True, parents=True)
log_file = logs_dir / "scraper.log"

logging.basicConfig(
    force=True,
    level=getattr(logging, config.log_level.upper(), logging.INFO),
    format="%(asctime)s - [%(name)s] - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=config.max_bytes,
            backupCount=config.backup_count,
            encoding="utf-8",
        ),
    ],
)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger. The root configuration is already applied automatically.
    """
    return logging.getLogger(name)
