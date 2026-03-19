.PHONY: install run test lint clean

install:
	python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

run:
	uvicorn app.main:app --reload

test:
	pytest

clean:
	rm -rf .pytest_cache .coverage data/*.db
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
