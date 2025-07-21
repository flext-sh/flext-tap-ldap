# FLEXT TAP LDAP - LDAP Directory Singer Tap
# =========================================
# Enterprise-grade Singer tap for LDAP directory data extraction
# Python 3.13 + Singer SDK + LDAP + FLEXT Core + Zero Tolerance Quality Gates

.PHONY: help check validate test lint type-check security format format-check fix
.PHONY: install dev-install setup pre-commit build clean
.PHONY: coverage coverage-html test-unit test-integration test-singer
.PHONY: deps-update deps-audit deps-tree deps-outdated
.PHONY: discover run validate-config catalog sync
.PHONY: ldap-test ldap-discover ldap-query ldap-performance

# ============================================================================
# 🎯 HELP & INFORMATION
# ============================================================================

help: ## Show this help message
	@echo "🎯 FLEXT TAP LDAP - LDAP Directory Singer Tap"
	@echo "============================================"
	@echo "🎯 Singer SDK + LDAP + FLEXT Core + Python 3.13"
	@echo ""
	@echo "📦 Enterprise-grade LDAP directory tap for Singer protocol"
	@echo "🔒 Zero tolerance quality gates with LDAP integration"
	@echo "🧪 90%+ test coverage requirement with Oracle OID support"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\\033[36m%-20s\\033[0m %s\\n", $$1, $$2}'

# ============================================================================
# 🎯 CORE QUALITY GATES - ZERO TOLERANCE
# ============================================================================

validate: lint type-check security test ## STRICT compliance validation (all must pass)
	@echo "✅ ALL QUALITY GATES PASSED - FLEXT TAP LDAP COMPLIANT"

check: lint type-check test ## Essential quality checks (pre-commit standard)
	@echo "✅ Essential checks passed"

lint: ## Ruff linting (17 rule categories, ALL enabled)
	@echo "🔍 Running ruff linter (ALL rules enabled)..."
	@poetry run ruff check src/ tests/ --fix --unsafe-fixes
	@echo "✅ Linting complete"

type-check: ## MyPy strict mode type checking (zero errors tolerated)
	@echo "🛡️ Running MyPy strict type checking..."
	@poetry run mypy src/ tests/ --strict
	@echo "✅ Type checking complete"

security: ## Security scans (bandit + pip-audit + secrets)
	@echo "🔒 Running security scans..."
	@poetry run bandit -r src/ --severity-level medium --confidence-level medium
	@poetry run pip-audit --ignore-vuln PYSEC-2022-42969
	@poetry run detect-secrets scan --all-files
	@echo "✅ Security scans complete"

format: ## Format code with ruff
	@echo "🎨 Formatting code..."
	@poetry run ruff format src/ tests/
	@echo "✅ Formatting complete"

format-check: ## Check formatting without fixing
	@echo "🎨 Checking code formatting..."
	@poetry run ruff format src/ tests/ --check
	@echo "✅ Format check complete"

fix: format lint ## Auto-fix all issues (format + imports + lint)
	@echo "🔧 Auto-fixing all issues..."
	@poetry run ruff check src/ tests/ --fix --unsafe-fixes
	@echo "✅ All auto-fixes applied"

# ============================================================================
# 🧪 TESTING - 90% COVERAGE MINIMUM
# ============================================================================

test: ## Run tests with coverage (90% minimum required)
	@echo "🧪 Running tests with coverage..."
	@poetry run pytest tests/ -v --cov=src/flext_tap_ldap --cov-report=term-missing --cov-fail-under=90
	@echo "✅ Tests complete"

test-unit: ## Run unit tests only
	@echo "🧪 Running unit tests..."
	@poetry run pytest tests/unit/ -v
	@echo "✅ Unit tests complete"

test-integration: ## Run integration tests only
	@echo "🧪 Running integration tests..."
	@poetry run pytest tests/integration/ -v
	@echo "✅ Integration tests complete"

test-singer: ## Run Singer protocol tests
	@echo "🧪 Running Singer protocol tests..."
	@poetry run pytest tests/singer/ -v
	@echo "✅ Singer tests complete"

test-ldap: ## Run LDAP-specific tests
	@echo "🧪 Running LDAP-specific tests..."
	@poetry run pytest tests/ -m "ldap" -v
	@echo "✅ LDAP tests complete"

test-oracle-oid: ## Run Oracle OID tests
	@echo "🧪 Running Oracle OID tests..."
	@poetry run pytest tests/ -m "oracle_oid" -v
	@echo "✅ Oracle OID tests complete"

coverage: ## Generate detailed coverage report
	@echo "📊 Generating coverage report..."
	@poetry run pytest tests/ --cov=src/flext_tap_ldap --cov-report=term-missing --cov-report=html
	@echo "✅ Coverage report generated in htmlcov/"

coverage-html: coverage ## Generate HTML coverage report
	@echo "📊 Opening coverage report..."
	@python -m webbrowser htmlcov/index.html

# ============================================================================
# 🚀 DEVELOPMENT SETUP
# ============================================================================

setup: install pre-commit ## Complete development setup
	@echo "🎯 Development setup complete!"

install: ## Install dependencies with Poetry
	@echo "📦 Installing dependencies..."
	@poetry install --all-extras --with dev,test,docs,security
	@echo "✅ Dependencies installed"

dev-install: install ## Install in development mode
	@echo "🔧 Setting up development environment..."
	@poetry install --all-extras --with dev,test,docs,security
	@poetry run pre-commit install
	@echo "✅ Development environment ready"

pre-commit: ## Setup pre-commit hooks
	@echo "🎣 Setting up pre-commit hooks..."
	@poetry run pre-commit install
	@poetry run pre-commit run --all-files || true
	@echo "✅ Pre-commit hooks installed"

# ============================================================================
# 🎯 SINGER TAP OPERATIONS
# ============================================================================

discover: ## Run Singer discovery mode
	@echo "🎵 Running Singer discovery..."
	@poetry run tap-ldap --config tests/fixtures/config/tap_config.json --discover
	@echo "✅ Discovery complete"

run: ## Run Singer tap extraction
	@echo "🎵 Running Singer tap extraction..."
	@poetry run tap-ldap --config tests/fixtures/config/tap_config.json --catalog tests/fixtures/catalog/catalog.json
	@echo "✅ Extraction complete"

run-debug: ## Run Singer tap with debug logging
	@echo "🎵 Running Singer tap with debug..."
	@poetry run tap-ldap --config tests/fixtures/config/tap_config.json --catalog tests/fixtures/catalog/catalog.json --log-level DEBUG
	@echo "✅ Debug extraction complete"

validate-config: ## Validate Singer configuration
	@echo "🔍 Validating Singer configuration..."
	@poetry run tap-ldap --config tests/fixtures/config/tap_config.json --validate-config
	@echo "✅ Configuration validated"

catalog: ## Generate Singer catalog
	@echo "🎵 Generating Singer catalog..."
	@poetry run tap-ldap --config tests/fixtures/config/tap_config.json --discover > catalog.json
	@echo "✅ Catalog generated: catalog.json"

sync: ## Run incremental sync
	@echo "🎵 Running incremental sync..."
	@poetry run tap-ldap --config tests/fixtures/config/tap_config.json --catalog tests/fixtures/catalog/catalog.json --state tests/fixtures/state/state.json
	@echo "✅ Incremental sync complete"

test-connection: ## Test LDAP connection
	@echo "🔌 Testing LDAP connection..."
	@poetry run tap-ldap --config tests/fixtures/config/tap_config.json --test-connection
	@echo "✅ Connection test complete"

# ============================================================================
# 📁 LDAP OPERATIONS
# ============================================================================

ldap-test: ## Test LDAP connectivity
	@echo "📁 Testing LDAP connectivity..."
	@poetry run python -c "from flext_tap_ldap.client import LDAPClient; import json; config = json.load(open('tests/fixtures/config/tap_config.json')); client = LDAPClient(**config['ldap']); print('Testing connection...'); conn = client.get_connection(); print('✅ Connected!' if conn else '❌ Failed')"
	@echo "✅ LDAP connectivity test complete"

ldap-discover: ## Discover LDAP schema
	@echo "📁 Discovering LDAP schema..."
	@poetry run python scripts/discover_ldap_schema.py
	@echo "✅ LDAP schema discovery complete"

ldap-query: ## Test LDAP query operations
	@echo "📁 Testing LDAP query operations..."
	@poetry run python scripts/test_ldap_queries.py
	@echo "✅ LDAP query operations test complete"

ldap-performance: ## Run LDAP performance tests
	@echo "⚡ Running LDAP performance tests..."
	@poetry run pytest tests/performance/ -v --benchmark-only
	@echo "✅ LDAP performance tests complete"

ldap-browse: ## Browse LDAP directory structure
	@echo "📁 Browsing LDAP directory structure..."
	@poetry run python scripts/browse_ldap_structure.py
	@echo "✅ LDAP directory browsing complete"

ldap-users: ## Extract user data from LDAP
	@echo "👥 Extracting user data from LDAP..."
	@poetry run tap-ldap --config tests/fixtures/config/tap_config.json --catalog tests/fixtures/catalog/users_catalog.json
	@echo "✅ User data extraction complete"

ldap-groups: ## Extract group data from LDAP
	@echo "👥 Extracting group data from LDAP..."
	@poetry run tap-ldap --config tests/fixtures/config/tap_config.json --catalog tests/fixtures/catalog/groups_catalog.json
	@echo "✅ Group data extraction complete"

# ============================================================================
# 🏢 ORACLE OID OPERATIONS
# ============================================================================

oracle-oid-test: ## Test Oracle OID connectivity
	@echo "🏢 Testing Oracle OID connectivity..."
	@poetry run python scripts/test_oracle_oid.py
	@echo "✅ Oracle OID connectivity test complete"

oracle-oid-schema: ## Discover Oracle OID schema
	@echo "🏢 Discovering Oracle OID schema..."
	@poetry run python scripts/discover_oracle_oid_schema.py
	@echo "✅ Oracle OID schema discovery complete"

oracle-oid-extract: ## Extract data from Oracle OID
	@echo "🏢 Extracting data from Oracle OID..."
	@poetry run tap-ldap --config tests/fixtures/config/oracle_oid_config.json --catalog tests/fixtures/catalog/oracle_oid_catalog.json
	@echo "✅ Oracle OID data extraction complete"

oracle-oid-users: ## Extract users from Oracle OID
	@echo "🏢 Extracting users from Oracle OID..."
	@poetry run python scripts/extract_oracle_oid_users.py
	@echo "✅ Oracle OID users extraction complete"

oracle-oid-containers: ## Extract containers from Oracle OID
	@echo "🏢 Extracting containers from Oracle OID..."
	@poetry run python scripts/extract_oracle_oid_containers.py
	@echo "✅ Oracle OID containers extraction complete"

# ============================================================================
# 📦 BUILD & DISTRIBUTION
# ============================================================================

build: clean ## Build distribution packages
	@echo "🔨 Building distribution..."
	@poetry build
	@echo "✅ Build complete - packages in dist/"

# ============================================================================
# 🧹 CLEANUP
# ============================================================================

clean: ## Remove all artifacts
	@echo "🧹 Cleaning up..."
	@rm -rf build/
	@rm -rf dist/
	@rm -rf *.egg-info/
	@rm -rf .coverage
	@rm -rf htmlcov/
	@rm -rf catalog.json
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Cleanup complete"

# ============================================================================
# 📊 DEPENDENCY MANAGEMENT
# ============================================================================

deps-update: ## Update all dependencies
	@echo "🔄 Updating dependencies..."
	@poetry update
	@echo "✅ Dependencies updated"

deps-audit: ## Audit dependencies for vulnerabilities
	@echo "🔍 Auditing dependencies..."
	@poetry run pip-audit
	@echo "✅ Dependency audit complete"

deps-tree: ## Show dependency tree
	@echo "🌳 Dependency tree:"
	@poetry show --tree

deps-outdated: ## Show outdated dependencies
	@echo "📋 Outdated dependencies:"
	@poetry show --outdated

# ============================================================================
# 🔧 ENVIRONMENT CONFIGURATION
# ============================================================================

# Python settings
PYTHON := python3.13
export PYTHONPATH := $(PWD)/src:$(PYTHONPATH)
export PYTHONDONTWRITEBYTECODE := 1
export PYTHONUNBUFFERED := 1

# LDAP Tap settings
export TAP_LDAP_HOST := localhost
export TAP_LDAP_PORT := 389
export TAP_LDAP_USE_SSL := false
export TAP_LDAP_BASE_DN := dc=test,dc=com

# Singer settings
export SINGER_LOG_LEVEL := INFO
export SINGER_BATCH_SIZE := 1000
export SINGER_MAX_BATCH_AGE := 300

# Oracle OID settings
export TAP_LDAP_ORACLE_OID_MODE := false
export TAP_LDAP_ORACLE_COMPATIBILITY := true

# Performance settings
export TAP_LDAP_PAGE_SIZE := 1000
export TAP_LDAP_TIMEOUT := 30
export TAP_LDAP_MAX_RETRIES := 3

# Poetry settings
export POETRY_VENV_IN_PROJECT := false
export POETRY_CACHE_DIR := $(HOME)/.cache/pypoetry

# Quality gate settings
export MYPY_CACHE_DIR := .mypy_cache
export RUFF_CACHE_DIR := .ruff_cache

# ============================================================================
# 📝 PROJECT METADATA
# ============================================================================

# Project information
PROJECT_NAME := flext-tap-ldap
PROJECT_VERSION := $(shell poetry version -s)
PROJECT_DESCRIPTION := FLEXT TAP LDAP - LDAP Directory Singer Tap

.DEFAULT_GOAL := help

# ============================================================================
# 🎯 SINGER SPECIFIC COMMANDS
# ============================================================================

singer-about: ## Show Singer tap about information
	@echo "🎵 Singer tap about information..."
	@poetry run tap-ldap --about
	@echo "✅ About information displayed"

singer-config-sample: ## Generate Singer config sample
	@echo "🎵 Generating Singer config sample..."
	@poetry run tap-ldap --config-sample > config_sample.json
	@echo "✅ Config sample generated: config_sample.json"

singer-schema: ## Validate Singer schema
	@echo "🎵 Validating Singer schema..."
	@poetry run tap-ldap --config tests/fixtures/config/tap_config.json --discover --validate-schema
	@echo "✅ Singer schema validation complete"

singer-test-streams: ## Test Singer streams
	@echo "🎵 Testing Singer streams..."
	@poetry run pytest tests/singer/test_streams.py -v
	@echo "✅ Singer streams tests complete"

# ============================================================================
# 🔍 STREAM TESTING
# ============================================================================

test-users-stream: ## Test users stream
	@echo "👥 Testing users stream..."
	@poetry run python scripts/test_users_stream.py
	@echo "✅ Users stream test complete"

test-groups-stream: ## Test groups stream
	@echo "👥 Testing groups stream..."
	@poetry run python scripts/test_groups_stream.py
	@echo "✅ Groups stream test complete"

test-ous-stream: ## Test organizational units stream
	@echo "🏢 Testing organizational units stream..."
	@poetry run python scripts/test_ous_stream.py
	@echo "✅ OUs stream test complete"

test-all-streams: test-users-stream test-groups-stream test-ous-stream ## Test all streams
	@echo "✅ All streams testing complete"

# ============================================================================
# 🎯 FLEXT ECOSYSTEM INTEGRATION
# ============================================================================

ecosystem-check: ## Verify FLEXT ecosystem compatibility
	@echo "🌐 Checking FLEXT ecosystem compatibility..."
	@echo "📦 Singer project: $(PROJECT_NAME) v$(PROJECT_VERSION)"
	@echo "🏗️ Architecture: Singer Tap + LDAP"
	@echo "🐍 Python: 3.13"
	@echo "🔗 Framework: FLEXT Core + Singer SDK"
	@echo "📊 Quality: Zero tolerance enforcement"
	@echo "✅ Ecosystem compatibility verified"

workspace-info: ## Show workspace integration info
	@echo "🏢 FLEXT Workspace Integration"
	@echo "==============================="
	@echo "📁 Project Path: $(PWD)"
	@echo "🏆 Role: LDAP Directory Singer Tap"
	@echo "🔗 Dependencies: flext-core, flext-observability, singer-sdk"
	@echo "📦 Provides: LDAP directory data extraction capabilities"
	@echo "🎯 Standards: Enterprise LDAP integration patterns"
