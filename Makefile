APP_VERSION ?= v0.1.0
IMAGE_REGISTRY ?= quay.io/opstree
IMAGE_NAME ?= attendance-api

#########################################################
# Build
#########################################################

build: fmt
	poetry config virtualenvs.create false
	poetry install --no-root --no-interaction --no-ansi

#########################################################
# Code Quality
#########################################################

fmt:
	pylint router/ client/ models/ utils/ app.py

#########################################################
# Docker
#########################################################

docker-build:
	docker build -t ${IMAGE_REGISTRY}/${IMAGE_NAME}:${APP_VERSION} -f Dockerfile .

docker-push:
	docker push ${IMAGE_REGISTRY}/${IMAGE_NAME}:${APP_VERSION}

#########################################################
# Database Migration
#########################################################

LIQUIBASE_PROPERTIES ?= liquibase.properties

run-migrations:
	@echo "Running Attendance DB Migrations..."

	liquibase \
		--driver-properties-file=$(LIQUIBASE_PROPERTIES) \
		update