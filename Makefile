# original file https://github.com/aiogram/bot/blob/master/Makefile
include .env

tail := 200
PYTHONPATH := $(shell pwd):${PYTHONPATH}

PROJECT := py-telegram-broker
VERSION := 0.1.0
PIPENV_VERBOSITY := -1

# =================================================================================================
# Base
# =================================================================================================

default:help

help:
	@echo "py-telegram-broker"

# =================================================================================================
# Development
# =================================================================================================

isort:
	pipenv run isort --recursive .

black:
	pipenv run black .

flake8:
	pipenv run flake8 .

lint: isort black flake8

alembic:
	PYTHONPATH=$(shell pwd):${PYTHONPATH} pipenv run alembic ${args}

migrate:
	PYTHONPATH=$(shell pwd):${PYTHONPATH} pipenv run alembic upgrade head

migration:
	PYTHONPATH=$(shell pwd):${PYTHONPATH} pipenv run alembic revision --autogenerate -m "${message}"

downgrade:
	PYTHONPATH=$(shell pwd):${PYTHONPATH} pipenv run alembic downgrade -1

beforeStart: docker-up-db migrate

app:
	pipenv run python -m core

start:
	$(MAKE) beforeStart
	$(MAKE) app

# =================================================================================================
# Docker
# =================================================================================================

docker-config:
	docker-compose config

docker-ps:
	docker-compose ps

docker-build:
	docker-compose build

docker-db:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d redis db

docker-up:
	docker-compose up -d --remove-orphans

docker-stop:
	docker-compose stop

docker-down:
	docker-compose down

docker-destroy:
	docker-compose down -v --remove-orphans

docker-logs:
	docker-compose logs -f --tail=${tail} ${args}

# =================================================================================================
# Application in Docker
# =================================================================================================

app-create: docker-build docker-stop docker-up

app-logs:
	$(MAKE) docker-logs args="bot"

app-stop: docker-stop

app-down: docker-down

app-start: docker-stop docker-up

app-destroy: docker-destroy
