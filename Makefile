.PHONY: help install install-dev test test-cov test-real lint format clean build upload docs

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install the package
	pip install -e .

install-dev:  ## Install development dependencies
	pip install -e ".[dev,test]"
	pre-commit install

test:  ## Run tests
	pytest

test-cov:  ## Run tests with coverage
	pytest --cov=src --cov-report=html --cov-report=term-missing

test-real:  ## Run real functionality tests
	python demo_real_pdf_processing.py

lint:  ## Run linting
	flake8 src tests
	mypy src
	black --check src tests
	isort --check-only src tests

format:  ## Format code
	black src tests
	isort src tests

clean:  ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build:  ## Build the package
	python -m build

upload:  ## Upload to PyPI (requires twine)
	twine upload dist/*

docs:  ## Generate documentation (placeholder)
	@echo "Documentation generation not yet implemented"

check:  ## Run all checks (lint + test)
	$(MAKE) lint
	$(MAKE) test