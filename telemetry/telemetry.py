import os
from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

try:
    from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
except ImportError:
    from opentelemetry.exporter.otlp.proto.http.log_exporter import OTLPLogExporter


SERVICE_NAME = "attendance-api"
SERVICE_VERSION = "1.0.0"
_http_requests = None
_http_request_duration = None


def _otlp_base_endpoint():
    """Return the OTLP base URL without a signal-specific path."""
    endpoint = os.getenv(
        "OTEL_EXPORTER_OTLP_ENDPOINT",
        "http://otms.monitoring.internal:4318",
    ).rstrip("/")

    for suffix in ("/v1/traces", "/v1/metrics", "/v1/logs"):
        if endpoint.endswith(suffix):
            endpoint = endpoint[: -len(suffix)]
            break

    return endpoint


def _resource():
    return Resource.create(
        {
            "service.name": SERVICE_NAME,
            "service.version": SERVICE_VERSION,
        }
    )


def _endpoint(path):
    return f"{_otlp_base_endpoint()}/v1/{path}"


def get_http_metrics():
    """Return the OTEL HTTP metrics created during telemetry initialization."""
    return _http_requests, _http_request_duration


def init_telemetry():
    """Initialize OTEL traces, metrics and logs.

    The application continues to write JSON logs to stdout via log.conf.
    The OTEL LoggingHandler additionally exports the same Python log records
    over OTLP to the central Collector.
    """
    resource = _resource()

    # -------------------------
    # Traces
    # -------------------------
    tracer_provider = TracerProvider(resource=resource)

    tracer_provider.add_span_processor(
        BatchSpanProcessor(
            OTLPSpanExporter(
                endpoint=_endpoint("traces"),
            )
        )
    )

    trace.set_tracer_provider(tracer_provider)

    # -------------------------
    # Metrics
    # -------------------------
    metric_exporter = OTLPMetricExporter(
        endpoint=_endpoint("metrics"),
    )

    global _http_requests, _http_request_duration

    metric_reader = PeriodicExportingMetricReader(
        metric_exporter,
        export_interval_millis=int(
            os.getenv("OTEL_METRIC_EXPORT_INTERVAL", "15000")
        ),
    )

    meter_provider = MeterProvider(
        resource=resource,
        metric_readers=[metric_reader],
    )

    metrics.set_meter_provider(meter_provider)

    meter = metrics.get_meter(SERVICE_NAME)
    _http_requests = meter.create_counter(
        "http.server.request.count",
        description="Number of HTTP requests received by the Attendance API",
        unit="{request}",
    )
    _http_request_duration = meter.create_histogram(
        "http.server.request.duration",
        description="HTTP request duration for the Attendance API",
        unit="ms",
    )

    # -------------------------
    # Logs
    # -------------------------
    logger_provider = LoggerProvider(resource=resource)

    logger_provider.add_log_record_processor(
        BatchLogRecordProcessor(
            OTLPLogExporter(
                endpoint=_endpoint("logs"),
            )
        )
    )

    # Send standard Python logging records through OTEL as well.
    # The existing log.conf StreamHandler remains responsible for the
    # JSON stdout/journald copy.
    otel_logging_handler = LoggingHandler(
        level=0,
        logger_provider=logger_provider,
    )

    root_logger = __import__("logging").getLogger()
    if not any(
        isinstance(handler, LoggingHandler)
        for handler in root_logger.handlers
    ):
        root_logger.addHandler(otel_logging_handler)

    # Psycopg2 instrumentation remains enabled.
    Psycopg2Instrumentor().instrument()
