.PHONY: help install install-dev test test-unit test-integration test-e2e lint format format-check type-check security clean build publish docs serve-docs docker-test docker-clean pre-commit all

# Configuration
PYTHON := python
POETRY := poetry
SOURCE_DIR := src
TEST_DIR := tests
PACKAGE_NAME := tap_ldap

# Colors for output
BLUE := \033[34m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

# Default target
help: ## Show this help message
	@echo "$(BLUE)Available targets:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(RESET) %s\n", $$1, $$2}'

# Installation targets
install: ## Install package dependencies
	@echo "$(BLUE)Installing dependencies...$(RESET)"
	$(POETRY) install

install-dev: ## Install package with development dependencies
	@echo "$(BLUE)Installing development dependencies...$(RESET)"
	$(POETRY) install --with dev

install-e2e: ## Install package with E2E testing dependencies
	@echo "$(BLUE)Installing E2E testing dependencies...$(RESET)"
	$(POETRY) install --with dev,e2e

install-all: ## Install all dependencies
	@echo "$(BLUE)Installing all dependencies...$(RESET)"
	$(POETRY) install --with dev,e2e

# Testing targets
test: test-unit test-integration ## Run all tests
	@echo "$(GREEN)All tests completed!$(RESET)"

test-unit: ## Run unit tests
	@echo "$(BLUE)Running unit tests...$(RESET)"
	$(POETRY) run pytest $(TEST_DIR)/unit -v --cov=$(SOURCE_DIR)/$(PACKAGE_NAME) --cov-report=term-missing --cov-report=html --cov-report=xml

test-integration: ## Run integration tests
	@echo "$(BLUE)Running integration tests...$(RESET)"
	$(POETRY) run pytest $(TEST_DIR)/integration -v --cov=$(SOURCE_DIR)/$(PACKAGE_NAME) --cov-append --cov-report=term-missing

test-e2e: ## Run E2E tests with Docker
	@echo "$(BLUE)Running E2E tests...$(RESET)"
	$(POETRY) run pytest $(TEST_DIR)/e2e -v --tb=short

test-coverage: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(RESET)"
	$(POETRY) run pytest $(TEST_DIR) -v --cov=$(SOURCE_DIR)/$(PACKAGE_NAME) --cov-report=term-missing --cov-report=html --cov-report=xml --cov-fail-under=90

# Code quality targets
lint: ## Run linting (ruff + additional checks)
	@echo "$(BLUE)Running linter...$(RESET)"
	$(POETRY) run ruff check $(SOURCE_DIR) $(TEST_DIR)
	$(POETRY) run ruff format --check $(SOURCE_DIR) $(TEST_DIR)

format: ## Format code with ruff and black
	@echo "$(BLUE)Formatting code...$(RESET)"
	$(POETRY) run ruff format $(SOURCE_DIR) $(TEST_DIR)
	$(POETRY) run ruff check --fix $(SOURCE_DIR) $(TEST_DIR)

format-check: ## Check code formatting
	@echo "$(BLUE)Checking code formatting...$(RESET)"
	$(POETRY) run ruff format --check $(SOURCE_DIR) $(TEST_DIR)

type-check: ## Run type checking with mypy
	@echo "$(BLUE)Running type checker...$(RESET)"
	$(POETRY) run mypy $(SOURCE_DIR)

security: ## Run security checks
	@echo "$(BLUE)Running security checks...$(RESET)"
	$(POETRY) run bandit -r $(SOURCE_DIR) -f json -o bandit-report.json || true
	$(POETRY) run safety check

# Singer SDK specific targets
discover: ## Run tap discovery
	@echo "$(BLUE)Running tap discovery...$(RESET)"
	$(POETRY) run tap-ldap --config config.example.json --discover

extract: ## Run tap extraction (requires config.json)
	@echo "$(BLUE)Running tap extraction...$(RESET)"
	$(POETRY) run tap-ldap --config config.json --catalog catalog.json

validate-config: ## Validate configuration file
	@echo "$(BLUE)Validating configuration...$(RESET)"
	$(POETRY) run tap-ldap --config config.json --test

# Development targets
clean: ## Clean build artifacts and cache
	@echo "$(BLUE)Cleaning build artifacts...$(RESET)"
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -f coverage.xml
	rm -f bandit-report.json
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: ## Build package
	@echo "$(BLUE)Building package...$(RESET)"
	$(POETRY) build

publish: ## Publish package to PyPI
	@echo "$(BLUE)Publishing package...$(RESET)"
	$(POETRY) publish

publish-test: ## Publish package to Test PyPI
	@echo "$(BLUE)Publishing package to Test PyPI...$(RESET)"
	$(POETRY) publish --repository testpypi

# Docker targets
docker-test: ## Run tests in Docker environment
	@echo "$(BLUE)Starting Docker test environment...$(RESET)"
	docker-compose -f docker-compose.yml up -d
	@echo "$(YELLOW)Waiting for services to be ready...$(RESET)"
	sleep 10
	$(POETRY) run pytest $(TEST_DIR)/e2e -v
	docker-compose -f docker-compose.yml down -v

docker-clean: ## Clean Docker environment
	@echo "$(BLUE)Cleaning Docker environment...$(RESET)"
	docker-compose -f docker-compose.yml down -v --remove-orphans
	docker system prune -f

# Pre-commit and CI targets
pre-commit: format lint type-check security test-unit ## Run pre-commit checks
	@echo "$(GREEN)Pre-commit checks completed!$(RESET)"

ci: install-dev pre-commit test-coverage ## Run CI pipeline
	@echo "$(GREEN)CI pipeline completed!$(RESET)"

# Convenience targets
all: clean install-dev pre-commit test build ## Run complete development cycle
	@echo "$(GREEN)Complete development cycle finished!$(RESET)"

check: lint type-check security ## Run all code quality checks
	@echo "$(GREEN)Code quality checks completed!$(RESET)"

dev-setup: install-dev ## Setup development environment
	@echo "$(BLUE)Setting up development environment...$(RESET)"
	$(POETRY) install --with dev,e2e
	@echo "$(GREEN)Development environment ready!$(RESET)"
	@echo "$(YELLOW)Next steps:$(RESET)"
	@echo "  1. Copy config.example.json to config.json and update with your LDAP settings"
	@echo "  2. Run 'make discover' to test your configuration"
	@echo "  3. Run 'make test' to ensure everything works"

# Poetry specific targets
poetry-lock: ## Update poetry.lock file
	@echo "$(BLUE)Updating poetry.lock...$(RESET)"
	$(POETRY) lock

poetry-update: ## Update dependencies
	@echo "$(BLUE)Updating dependencies...$(RESET)"
	$(POETRY) update

poetry-show: ## Show dependency tree
	@echo "$(BLUE)Dependency tree:$(RESET)"
	$(POETRY) show --tree

poetry-export: ## Export requirements.txt
	@echo "$(BLUE)Exporting requirements.txt...$(RESET)"
	$(POETRY) export -f requirements.txt --output requirements.txt --without-hashes

# Debug targets
debug-env: ## Show environment information
	@echo "$(BLUE)Environment Information:$(RESET)"
	@echo "Python: $$($(PYTHON) --version)"
	@echo "Poetry: $$($(POETRY) --version)"
	@echo "Package: $(PACKAGE_NAME)"
	@echo "Source: $(SOURCE_DIR)"
	@echo "Tests: $(TEST_DIR)"

# Example configuration
example-config: ## Create example configuration file
	@echo "$(BLUE)Creating example configuration...$(RESET)"
	@echo '{\n  "host": "ldap.example.com",\n  "port": 389,\n  "bind_dn": "cn=REDACTED_LDAP_BIND_PASSWORD,dc=example,dc=com",\n  "password": "your_password",\n  "base_dn": "dc=example,dc=com",\n  "use_ssl": false,\n  "page_size": 1000,\n  "user_filter": "(objectClass=inetOrgPerson)",\n  "group_filter": "(objectClass=groupOfNames)"\n}' > config.example.json
	@echo "$(GREEN)Example configuration created: config.example.json$(RESET)"
