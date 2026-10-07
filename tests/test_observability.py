import json
import logging

from roster.observability import JsonFormatter, configure_logging, timed


def test_json_formatter_contains_structured_fields():
    record = logging.LogRecord("roster", logging.INFO, "", 0, "hello", (), None)
    record.event = "request_finished"
    record.request_id = "abc"
    record.duration_ms = 12.5
    payload = json.loads(JsonFormatter().format(record))
    assert payload["event"] == "request_finished"
    assert payload["request_id"] == "abc"
    assert payload["duration_ms"] == 12.5


def test_configure_logging_is_idempotent():
    logger = configure_logging("WARNING")
    count = len(logger.handlers)
    assert configure_logging("WARNING") is logger
    assert len(logger.handlers) == count


def test_timed_emits_duration(caplog):
    logger = logging.getLogger("roster.test")
    with caplog.at_level(logging.INFO, logger="roster.test"):
        with timed(logger, "operation"):
            pass
    assert any("operation" in record.message for record in caplog.records)
