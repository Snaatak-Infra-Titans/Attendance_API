import os

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor


def init_tracing():
    resource = Resource.create(
        {
            "service.name": "attendance-api",
            "service.version": "1.0.0",
        }
    )

    provider = TracerProvider(resource=resource)

    otel_endpoint = os.getenv(
        "OTEL_EXPORTER_OTLP_ENDPOINT",
        "http://otms.monitoring.internal:4318/v1/traces",
    )

    exporter = OTLPSpanExporter(
        endpoint=otel_endpoint,
    )

    provider.add_span_processor(
        BatchSpanProcessor(exporter)
    )

    trace.set_tracer_provider(provider)

    Psycopg2Instrumentor().instrument()
