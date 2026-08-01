#!/bin/bash

set -Eeuo pipefail

echo "Stopping Attendance API..."

sudo systemctl stop attendance-api || true

echo "Cleaning PostgreSQL..."

sudo -u postgres psql attendance_db <<EOF
TRUNCATE TABLE records RESTART IDENTITY CASCADE;
EOF

echo "Cleaning logs..."

rm -rf /home/ubuntu/logs/*

echo "Cleaning Python cache..."

find /home/ubuntu -type d -name "__pycache__" -exec rm -rf {} + || true
find /home/ubuntu -type f -name "*.pyc" -delete || true

echo "Attendance cleanup completed."
