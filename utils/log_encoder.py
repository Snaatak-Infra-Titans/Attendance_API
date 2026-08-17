"""
Module for custom json log model in flask and gunicorn
"""

from pythonjsonlogger import jsonlogger
from opentelemetry import trace


# pylint: disable=super-with-arguments
class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Class for defining JSON log structure of Flask"""

    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(
            log_record,
            record,
            message_dict,
        )

        # Timestamp
        if not log_record.get("timestamp"):
            log_record["timestamp"] = record.created

        # Safely handle log arguments
        args = record.args or {}

        if "r" in args:
            log_record["request"] = args.get("r")
            log_record["message"] = None

        if "s" in args:
            log_record["status_code"] = args.get("s")

        if "m" in args:
            log_record["method"] = args.get("m")

        if "h" in args:
            log_record["remote_address"] = args.get("h")

        # Service name
        log_record["service"] = "attendance-api"

        # OpenTelemetry Trace Context
        span = trace.get_current_span()

        if span is not None:
            span_context = span.get_span_context()

            if span_context.is_valid:
                log_record["trace_id"] = format(span_context.trace_id, "032x")
                log_record["span_id"] = format(span_context.span_id, "016x")