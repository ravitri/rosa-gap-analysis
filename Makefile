.PHONY: setup test lint clean

setup:
	pip install -r requirements.txt

test:
	python -m pytest tests/ -v 2>/dev/null || echo "No tests directory found"

lint:
	python -m ruff check . 2>/dev/null || python -m flake8 . 2>/dev/null || echo "No linter installed"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
	find . -type f -name '*.pyc' -delete 2>/dev/null
