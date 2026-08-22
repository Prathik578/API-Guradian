.PHONY: setup test lint build run-api run-worker bootstrap-build clean

setup:
	python3 -m venv .venv && . .venv/bin/activate && pip install -e ".[dev]"

test:
	pytest tests/

lint:
	ruff check src/ tests/
	mypy src/

run-api:
	uvicorn api_guardian.api.app:app --reload --port 8000

run-worker:
	celery -A api_guardian.workers.celery_app worker --loglevel=info

bootstrap-build:
	cd bootstrap && CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o bootstrap main.go

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
