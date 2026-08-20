#!/usr/bin/env bash
set -euo pipefail

cd "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

./.venv/bin/python - <<'PY'
import flask
import flasgger
import gunicorn
import psycopg2
import redis
import prometheus_client
import prometheus_flask_exporter
import opentelemetry
import opentelemetry.sdk

print("Attendance API Python dependencies: OK")
print("Flask:", flask.__version__)
print("Gunicorn:", gunicorn.__version__)
print("OpenTelemetry SDK:", opentelemetry.sdk.__version__)
PY
