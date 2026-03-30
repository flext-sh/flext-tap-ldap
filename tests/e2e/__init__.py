# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""E2E tests package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from tests.e2e import conftest as conftest, test_integration as test_integration
    from tests.e2e.conftest import (
        catalog_file as catalog_file,
        ldap_connection as ldap_connection,
        ldap_container as ldap_container,
        logger as logger,
        project_root as project_root,
        sample_catalog as sample_catalog,
        tap_config_file as tap_config_file,
    )
    from tests.e2e.test_integration import (
        TestFlextTapLdapIntegration as TestFlextTapLdapIntegration,
    )

_LAZY_IMPORTS: Mapping[str, Sequence[str]] = {
    "TestFlextTapLdapIntegration": [
        "tests.e2e.test_integration",
        "TestFlextTapLdapIntegration",
    ],
    "catalog_file": ["tests.e2e.conftest", "catalog_file"],
    "conftest": ["tests.e2e.conftest", ""],
    "ldap_connection": ["tests.e2e.conftest", "ldap_connection"],
    "ldap_container": ["tests.e2e.conftest", "ldap_container"],
    "logger": ["tests.e2e.conftest", "logger"],
    "project_root": ["tests.e2e.conftest", "project_root"],
    "sample_catalog": ["tests.e2e.conftest", "sample_catalog"],
    "tap_config_file": ["tests.e2e.conftest", "tap_config_file"],
    "test_integration": ["tests.e2e.test_integration", ""],
}

_EXPORTS: Sequence[str] = [
    "TestFlextTapLdapIntegration",
    "catalog_file",
    "conftest",
    "ldap_connection",
    "ldap_container",
    "logger",
    "project_root",
    "sample_catalog",
    "tap_config_file",
    "test_integration",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, _EXPORTS)
