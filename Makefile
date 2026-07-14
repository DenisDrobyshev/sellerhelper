.PHONY: install dev up down test lint wb

install:
	pip install -e ".[dev]"

dev:
	uvicorn core.main:app --reload

up:
	docker compose up --build

down:
	docker compose down

test:
	pytest -q

lint:
	ruff check core tests

# Smoke-test the Wildberries collector:  make wb Q="чехол для iphone"
wb:
	python -m core.collectors.wildberries "$(Q)"
