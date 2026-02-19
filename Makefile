# FLEXT-TAP-LDAP Makefile
# Migrated to use base.mk - 2026-01-03

PROJECT_NAME := flext-tap-ldap
# Include shared base.mk for standard targets
include ../base.mk

# =============================================================================
# SINGER TAP CONFIGURATION
# =============================================================================

TAP_CONFIG ?= config.json
TAP_CATALOG ?= catalog.json
TAP_STATE ?= state.json

# =============================================================================
# SINGER TAP OPERATIONS
# =============================================================================

.PHONY: discover run catalog sync validate-config test-singer

discover: ## Run tap discovery mode
	$(POETRY) run tap-ldap --config $(TAP_CONFIG) --discover > $(TAP_CATALOG)

run: ## Run tap extraction
	$(POETRY) run tap-ldap --config $(TAP_CONFIG) --catalog $(TAP_CATALOG) --state $(TAP_STATE)

catalog: discover ## Alias for discover

sync: run ## Alias for run

validate-config: ## Validate tap configuration
	PYTHONPATH=$(SRC_DIR) $(POETRY) run python -c "import json; json.load(open('$(TAP_CONFIG)'))"

# =============================================================================
# LDAP-SPECIFIC TARGETS
# =============================================================================

.PHONY: ldap-test ldap-discover ldap-query

ldap-test: ## Test LDAP connection
	PYTHONPATH=$(SRC_DIR) $(POETRY) run python -c "from flext_tap_ldap.client import test_connection; test_connection()"

ldap-discover: ## Discover LDAP schema
	PYTHONPATH=$(SRC_DIR) $(POETRY) run python -c "from flext_tap_ldap.discovery import discover_schema; discover_schema()"

ldap-query: ## Run test LDAP query
	PYTHONPATH=$(SRC_DIR) $(POETRY) run python -c "from flext_tap_ldap.client import test_query; test_query()"

# =============================================================================
# PROJECT-SPECIFIC TEST TARGETS
# =============================================================================

.PHONY: test-singer

test-singer: ## Run Singer protocol tests
	$(POETRY) run pytest $(TESTS_DIR) -m singer -v
