# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""E2E tests package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from tests.e2e.conftest import *
    from tests.e2e.test_integration import *

_LAZY_IMPORTS: Mapping[str, str | Sequence[str]] = {
    "TestFlextTapLdapIntegration": "tests.e2e.test_integration",
    "catalog_file": "tests.e2e.conftest",
    "conftest": "tests.e2e.conftest",
    "ldap_connection": "tests.e2e.conftest",
    "ldap_container": "tests.e2e.conftest",
    "logger": "tests.e2e.conftest",
    "project_root": "tests.e2e.conftest",
    "sample_catalog": "tests.e2e.conftest",
    "tap_config_file": "tests.e2e.conftest",
    "test_integration": "tests.e2e.test_integration",
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
