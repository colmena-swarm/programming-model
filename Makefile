# Colmena Programming Model - Makefile
# This Makefile provides targets for running unit and integration tests

.PHONY: help install test test-unit test-integration test-all clean install-dev

# Default target
help:
	@echo "Colmena Programming Model - Available targets:"
	@echo ""
	@echo "  install      - Install the package in development mode with test dependencies"
	@echo "  install-dev  - Install only test dependencies (pytest, busypie)"
	@echo "  test         - Run all tests (unit + integration)"
	@echo "  test-unit    - Run only unit tests"
	@echo "  test-integration - Run only integration tests"
	@echo "  test-verbose - Run all tests with verbose output"
	@echo "  test-coverage - Run all tests with coverage report"
	@echo "  clean        - Clean up test artifacts and cache files"
	@echo "  help         - Show this help message"
	@echo ""

# Install the package in development mode with test dependencies
install:
	pip install -e ".[ci]"

# Install only test dependencies
install-dev:
	pip install pytest busypie

# Run all tests (unit + integration)
test: test-unit test-integration

# Run only unit tests
test-unit:
	@echo "Running unit tests..."
	python -m pytest test/unit/ -v --folder=./test/unit/resources

# Run only integration tests
test-integration:
	@echo "Running integration tests..."
	python -m pytest test/integration/ -v

# Run all tests with verbose output
test-verbose:
	@echo "Running all tests with verbose output..."
	python -m pytest test/ -v -s --folder=./test/unit/resources

# Run all tests with coverage report
test-coverage:
	@echo "Running tests with coverage report..."
	pip install pytest-cov
	python -m pytest test/ --cov=colmena --cov-report=html --cov-report=term-missing --folder=./test/unit/resources

# Clean up test artifacts and cache files
clean:
	@echo "Cleaning up test artifacts..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	rm -rf htmlcov/ 2>/dev/null || true
	rm -rf .coverage 2>/dev/null || true
	rm -rf dist/ 2>/dev/null || true
	rm -rf build/ 2>/dev/null || true
	rm -rf *.egg-info/ 2>/dev/null || true
