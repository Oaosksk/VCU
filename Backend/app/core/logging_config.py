"""Structured logging configuration with file rotation"""
import logging
import logging.handlers
from pathlib import Path


def setup_logging(log_dir: str = "./storage/logs", level: str = "INFO"):
    """
    Configure application-wide logging with console + rotating file output.

    Args:
        log_dir: Directory for log files
        level: Root log level (DEBUG, INFO, WARNING, ERROR)
    """
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Clear any existing handlers to avoid duplicates on reload
    root_logger.handlers.clear()

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console = logging.StreamHandler()
    console.setFormatter(fmt)
    console.setLevel(logging.DEBUG)
    root_logger.addHandler(console)

    # Rotating file handler – general log
    info_handler = logging.handlers.RotatingFileHandler(
        log_path / "app.log",
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding="utf-8",
    )
    info_handler.setFormatter(fmt)
    info_handler.setLevel(logging.INFO)
    root_logger.addHandler(info_handler)

    # Rotating file handler – errors only
    error_handler = logging.handlers.RotatingFileHandler(
        log_path / "error.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    error_handler.setFormatter(fmt)
    error_handler.setLevel(logging.ERROR)
    root_logger.addHandler(error_handler)

    # Quieten noisy third-party loggers
    for noisy in ("ultralytics", "urllib3", "httpcore", "httpx"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    logging.getLogger(__name__).info(
        "Logging configured – level=%s, log_dir=%s", level, log_dir
    )
