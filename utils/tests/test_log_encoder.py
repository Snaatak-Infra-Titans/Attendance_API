from pythonjsonlogger import jsonlogger
import json
import logging
import pytest


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Class for defining JSON log structure of Flask"""

    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)

        if not log_record.get("timestamp"):
            log_record["timestamp"] = record.created

        if "r" in record.args:
            log_record["request"] = record.args.get("r")
            log_record["message"] = None

        if "s" in record.args:
            log_record["status_code"] = record.args.get("s")

        if "m" in record.args:
            log_record["method"] = record.args.get("m")

        if "h" in record.args:
            log_record["remote_address"] = record.args.get("h")


def test_custom_json_formatter():
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="",
        lineno=1,
        msg="",
        args={"r": "/api", "s": 200, "m": "GET", "h": "127.0.0.1"},
        exc_info=None,
    )

    formatter = CustomJsonFormatter()
    result = formatter.format(record)

    # Convert JSON string to dictionary
    log = json.loads(result)

    assert log["request"] == "/api"
    assert log["status_code"] == 200
    assert log["method"] == "GET"
    assert log["remote_address"] == "127.0.0.1"
    assert log["message"] is None
    assert "timestamp" in log


if __name__ == "__main__":
    pytest.main()
