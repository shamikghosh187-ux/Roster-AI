import json
import logging
import os
import sys
from contextlib import contextmanager
from datetime import datetime, timezone
from time import monotonic


class JsonFormatter(logging.Formatter):
    def format(self, record):
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key in ("event", "request_id", "duration_ms", "action", "error_type"):
            value = getattr(record, key, None)
            if value is not None:
                payload[key] = value
        return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def configure_logging(level=None):
    level_name = (level or os.getenv("ROSTER_LOG_LEVEL", "INFO")).upper()
    numeric_level = getattr(logging, level_name, logging.INFO)
    root = logging.getLogger("roster")
    root.setLevel(numeric_level)
    if not root.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(JsonFormatter())
        root.addHandler(handler)
    return root


@contextmanager
def timed(logger, event, **fields):
    started = monotonic()
    try:
        yield
    finally:
        logger.info(
            event,
            extra={
                "event": event,
                "duration_ms": round((monotonic() - started) * 1000, 2),
                **fields,
            },
        )
