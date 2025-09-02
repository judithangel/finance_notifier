import logging
from logging.handlers import RotatingFileHandler
from typing import Dict, Any


def setup_logging(cfg_log: Dict[str, Any]) -> logging.Logger:
    """
    Configure and return the central logger for the app.

    Features:
      - Log level configurable via config (DEBUG, INFO, WARNING, …)
      - Always logs to console (stdout)
      - Optional rotating file handler for persistent logs:
          * File size limit (maxBytes)
          * Number of backups (backupCount)
          * UTF-8 encoding for international characters

    Args:
        cfg_log: Logging configuration dictionary. Expected keys:
            - "level": str - log level (e.g. "INFO", "DEBUG")
            - "to_file": bool - whether to also log to a file
            - "file_path": str - log filename (default "alerts.log")
            - "file_max_bytes": int - max file size before rotation
            - "file_backup_count": int - number of rotated backups to keep

    Returns:
        logging.Logger: Configured logger instance named "stock-alerts".
    """
    # Resolve log level from cfg_log (fallback to INFO)
    level_name = cfg_log["level"]
    level = getattr(logging, level_name, logging.INFO)

    # Obtain the named logger "stock-alerts" and set its level
    logger = logging.getLogger("stock-alerts")
    logger.setLevel(level)

    # Clear any existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create a Formatter with timestamp, level and message
    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Configure a StreamHandler for console output, apply formatter and add it
    ch = logging.StreamHandler()
    logger.addHandler(ch)

    # If cfg_log["to_file"] is true, create a RotatingFileHandler with provided settings
    if cfg_log.get("to_file", False):
        fh = RotatingFileHandler(
            cfg_log["file_path"],
            maxBytes=cfg_log["file_max_bytes"],
            backupCount=cfg_log["file_backup_count"],
            encoding="utf-8"
        )
        fh.setFormatter(fmt)
        logger.addHandler(fh)

    # Log a debug message summarizing the final logging setup
    logger.debug("Logging initialized: level=%s, to_file=%s", level_name, cfg_log.get("to_file", False))

    # Return the configured logger
    return logger
