"""
Module for calling the main flask application.
The application will be only supported with Flask and Gunicorn.
"""

from flask import Flask, json

# ==================================================
# OpenTelemetry initialization
# IMPORTANT:
# This must happen BEFORE importing modules that
# create PostgreSQL connections.
# ==================================================

from telemetry.telemetry import init_tracing

init_tracing()

# ==================================================
# Application imports
# ==================================================

from flasgger import Swagger
from prometheus_flask_exporter import PrometheusMetrics
from opentelemetry.instrumentation.flask import FlaskInstrumentor

from router.attendance import route as create_record
from router.cache import cache
from utils.json_encoder import DataclassJSONEncoder
from client.redis.redis_conn import get_caching_data
from middleware.logging import register_logging


# ==================================================
# Flask application
# ==================================================

app = Flask(__name__)

# ==================================================
# OpenTelemetry Flask instrumentation
# ==================================================

FlaskInstrumentor().instrument_app(app)

# ==================================================
# Logging
# ==================================================

register_logging(app)

# ==================================================
# Swagger
# ==================================================

swagger = Swagger(app)

# ==================================================
# Prometheus metrics
# ==================================================

metrics = PrometheusMetrics(app)

metrics.info(
    "attendance_api",
    "Attendance API opentelemetry metrics",
    version="0.1.0",
)

# ==================================================
# Redis cache
# ==================================================

cache.init_app(
    app,
    get_caching_data(),
)

# ==================================================
# JSON configuration
# ==================================================

app.config["JSON_SORT_KEYS"] = False
json.provider.DefaultJSONProvider.sort_keys = False
app.json_encoder = DataclassJSONEncoder

# ==================================================
# Routes
# ==================================================

app.register_blueprint(
    create_record,
    url_prefix="/api/v1",
)