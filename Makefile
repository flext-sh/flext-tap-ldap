# flext-tap-ldap - LDAP Singer Tap
PROJECT_NAME := flext-tap-ldap
COV_DIR := flext_tap_ldap
MIN_COVERAGE := 90

include ../base.mk

# === PROJECT-SPECIFIC TARGETS ===
.PHONY: tap-run tap-discover tap-catalog test-unit test-integration build shell

tap-run: ## Run tap with config
	$(Q)PYTHONPATH=$(SRC_DIR) $(POETRY) run tap-ldap --config config.json

tap-discover: ## Run discovery mode
	$(Q)PYTHONPATH=$(SRC_DIR) $(POETRY) run tap-ldap --config config.json --discover

tap-catalog: ## Show catalog
	$(Q)PYTHONPATH=$(SRC_DIR) $(POETRY) run tap-ldap --config config.json --discover | jq .

.DEFAULT_GOAL := help
