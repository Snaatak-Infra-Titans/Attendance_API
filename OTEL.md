# Attendance API - OpenTelemetry 3-signal configuration

## What changed

This version keeps the existing Attendance tracing and PostgreSQL instrumentation and adds:

- OTLP traces
- OTLP metrics
- OTLP logs
- Existing JSON stdout/journald logging
- Existing trace_id/span_id fields in JSON logs

The application exports directly to the central OTEL Collector.

## Recommended systemd setting

Use the OTLP base endpoint:

```ini
Environment="OTEL_EXPORTER_OTLP_ENDPOINT=http://otms.monitoring.internal:4318"
```

The application derives:

- `/v1/traces`
- `/v1/metrics`
- `/v1/logs`

Do not use the Docker-only hostname `otel-collector`.

## Install dependencies

For a fresh EC2 deployment, the runtime dependency file is complete and includes
the application, database, Redis, Swagger, Gunicorn, Prometheus and all
OpenTelemetry dependencies.

```bash
cd /home/ubuntu/Attendance_API
./install_dependencies.sh
```

Or manually:

```bash
cd /home/ubuntu/Attendance_API
python3.11 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -r requirements.txt
```


## Restart

```bash
sudo systemctl daemon-reload
sudo systemctl restart attendance-api
sudo systemctl status attendance-api --no-pager -l
```

## Verify

```bash
sudo journalctl -u attendance-api -n 50 --no-pager
```

Then generate an API request and verify traces in Tempo/Grafana.

Metrics and logs require the central Monitoring OTEL Collector to have working `metrics` and `logs` pipelines.

## Rollback

The previous tracing-only implementation can be restored by restoring the old
`telemetry/telemetry.py` and `app.py` from version control or backup.

## Application metrics

The application retains the existing `/metrics` endpoint during migration, but
also creates OTLP metrics directly through the OpenTelemetry SDK:

- `http.server.request.count`
- `http.server.request.duration`

The existing Prometheus Flask exporter is intentionally retained for now so the
current Prometheus dashboard does not break during the migration. It can be
removed later after OTLP metrics are verified end-to-end.
