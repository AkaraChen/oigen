.PHONY: install dev test cov lint fmt clean build publish

install:
	pdm install

dev:
	pdm install -G dev

test:
	pdm run pytest

cov:
	pdm run pytest --cov=oigen --cov-report=term-missing --cov-branch

cov-html:
	pdm run pytest --cov=oigen --cov-report=html --cov-branch
	open htmlcov/index.html

lint:
	pdm run ruff check oigen tests

fmt:
	pdm run ruff format oigen tests

clean:
	rm -rf dist build *.egg-info htmlcov .coverage .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

build:
	pdm build

publish:
	pdm publish
