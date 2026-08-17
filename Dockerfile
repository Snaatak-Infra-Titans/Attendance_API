# ==================================================
# Stage 1 - Build Attendance API
# ==================================================
FROM python:3.11-slim-bookworm AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        wget \
        unzip \
        libpq5 && \
    rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry

# Copy dependency files
COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false

RUN poetry install --no-root --no-interaction --no-ansi

# Copy source
COPY . .

# ==================================================
# Stage 2 - Runtime
# ==================================================
FROM python:3.11-slim-bookworm

LABEL authors="Opstree Solution" \
      application="Attendance API" \
      version="v0.1.0"

WORKDIR /app

# Runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        wget \
        unzip \
        make \
        netcat-openbsd \
        openjdk-17-jre-headless && \
    rm -rf /var/lib/apt/lists/*

# --------------------------------------------------
# Install Liquibase
# --------------------------------------------------
RUN wget https://github.com/liquibase/liquibase/releases/download/v4.33.0/liquibase-4.33.0.zip && \
    unzip liquibase-4.33.0.zip -d /liquibase && \
    rm liquibase-4.33.0.zip

ENV PATH="/liquibase:${PATH}"

# --------------------------------------------------
# PostgreSQL JDBC Driver
# --------------------------------------------------
RUN wget \
https://jdbc.postgresql.org/download/postgresql-42.7.7.jar \
-O /liquibase/postgresql.jar

# --------------------------------------------------
# Copy Python dependencies
# --------------------------------------------------
COPY --from=builder /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=builder /usr/local/bin /usr/local/bin

# --------------------------------------------------
# Copy Application
# --------------------------------------------------
COPY --from=builder /app /app

# --------------------------------------------------
# Startup 
# --------------------------------------------------

EXPOSE 8081

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8081", "--log-config", "log.conf", "--access-logfile", "/dev/null"]