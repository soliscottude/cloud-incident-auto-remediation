import logging
import json
from typing import Any, Dict, Optional


def get_logger(name: str) -> logging.Logger:
    """
    Return a configured logger instance with a simple, consistent format.
    This logger can be reused across multiple modules.
    """
    logger = logging.getLogger(name)

    # Avoid adding multiple handlers if this function is called many times
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    return logger


def log_json(
    logger: logging.Logger,
    level: str,
    message: str,
    extra: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Log a structured JSON message with an optional `extra` payload.

    This helps keep Lambda logs consistent and easy to query
    using CloudWatch Logs Insights.
    """
    payload: Dict[str, Any] = {"message": message}
    if extra:
        payload["extra"] = extra

    text = json.dumps(payload, ensure_ascii=False)

    level = level.lower()
    if level == "debug":
        logger.debug(text)
    elif level == "warning":
        logger.warning(text)
    elif level == "error":
        logger.error(text)
    elif level == "critical":
        logger.critical(text)
    else:
        logger.info(text)
