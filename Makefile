# macOS / Linux. On Windows use tasks.ps1 (same targets).
PY ?= .venv/bin/python

.PHONY: setup dev run test test-infer lint fetch-models fetch-soundfont fetch-corpus bench migrate

setup:
	python3 -m venv .venv
	$(PY) -m pip install -U pip
	$(PY) -m pip install -e ".[dev]"

dev:
	$(PY) -m uvicorn app.main:create_app --factory --reload --host 127.0.0.1 --port 8000

run:
	$(PY) -m app.main

migrate:
	$(PY) -m alembic upgrade head

test:
	$(PY) -m pytest

test-infer:
	$(PY) -m pytest -m inference

lint:
	$(PY) -m ruff check .
	$(PY) -m ruff format --check .
	$(PY) -m mypy

fetch-models:
	$(PY) scripts/fetch_models.py

fetch-soundfont:
	$(PY) scripts/fetch_soundfont.py

fetch-corpus:
	$(PY) scripts/fetch_corpus.py

bench:
	$(PY) scripts/benchmark_models.py
