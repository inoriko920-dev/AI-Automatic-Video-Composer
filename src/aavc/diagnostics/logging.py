from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from aavc.diagnostics.redaction import redact_text, redact_value


class JsonLineFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": redact_text(record.getMessage()),
        }
        event = getattr(record, "event", None)
        if isinstance(event, str) and event:
            payload["event"] = redact_text(event)
        context = getattr(record, "context", None)
        if isinstance(context, dict):
            payload["context"] = redact_value(context)
        if record.exc_info:
            payload["exception"] = redact_text(self.formatException(record.exc_info))
        return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def configure_file_logger(
    log_path: str | Path,
    *,
    name: str = "aavc",
    level: int = logging.INFO,
) -> logging.Logger:
    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    target = str(path.resolve())
    for handler in logger.handlers:
        if isinstance(handler, logging.FileHandler) and handler.baseFilename == target:
            return logger

    handler = logging.FileHandler(path, encoding="utf-8")
    handler.setFormatter(JsonLineFormatter())
    logger.addHandler(handler)
    return logger


def log_event(
    logger: logging.Logger,
    level: int,
    event: str,
    message: str,
    *,
    context: dict[str, Any] | None = None,
) -> None:
    logger.log(
        level,
        message,
        extra={"event": event, "context": {} if context is None else context},
    )
