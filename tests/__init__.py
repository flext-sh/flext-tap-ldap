# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Tests package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_tests import *

    from tests import conftest, constants, models, protocols, typings, utilities
    from tests.conftest import *
    from tests.constants import *
    from tests.e2e import *
    from tests.models import *
    from tests.protocols import *
    from tests.typings import *
    from tests.unit import *
    from tests.utilities import *

_LAZY_IMPORTS: Mapping[str, str | Sequence[str]] = {
    "FlextTapLdapTestConstants": "tests.constants",
    "FlextTapLdapTestModels": "tests.models",
    "FlextTapLdapTestProtocols": "tests.protocols",
    "FlextTapLdapTestTypes": "tests.typings",
    "FlextTapLdapTestUtilities": "tests.utilities",
    "TestConnectionTestedEvent": "tests.unit.test_models",
    "TestCustomStream": "tests.unit.test_streams",
    "TestCustomStreamParams": "tests.unit.test_streams",
    "TestFlextTapLdapIntegration": "tests.e2e.test_integration",
    "TestFlextTapLdapTapUnit": "tests.unit.test_tap",
    "TestGroupsStream": "tests.unit.test_streams",
    "TestLDAPBaseStream": "tests.unit.test_streams",
    "TestLDAPBaseStreamDirectUsage": "tests.unit.test_streams",
    "TestLDAPClientCoverageBoost": "tests.unit.test_client",
    "TestLDAPClientQuick": "tests.unit.test_client_quick",
    "TestLDIFStreamBasic": "tests.unit.test_ldif_stream",
    "TestLdifProcessor": "tests.unit.test_ldif_processor",
    "TestOrganizationalUnitsStream": "tests.unit.test_streams",
    "TestRecordExtractedEvent": "tests.unit.test_models",
    "TestSchemaStream": "tests.unit.test_streams",
    "TestStreamDiscoveredEvent": "tests.unit.test_models",
    "TestStreamExceptionHandling": "tests.unit.test_streams",
    "TestStreamIntegration": "tests.unit.test_streams",
    "TestTapExecutionCompletedEvent": "tests.unit.test_models",
    "TestTapExecutionStartedEvent": "tests.unit.test_models",
    "TestUsersStream": "tests.unit.test_streams",
    "c": ["tests.constants", "FlextTapLdapTestConstants"],
    "catalog_file": "tests.e2e.conftest",
    "conftest": "tests.conftest",
    "constants": "tests.constants",
    "d": "flext_tests",
    "e": "flext_tests",
    "e2e": "tests.e2e",
    "h": "flext_tests",
    "ldap_connection": "tests.e2e.conftest",
    "ldap_container": "tests.e2e.conftest",
    "logger": "tests.e2e.conftest",
    "m": ["tests.models", "FlextTapLdapTestModels"],
    "models": "tests.models",
    "p": ["tests.protocols", "FlextTapLdapTestProtocols"],
    "project_root": "tests.e2e.conftest",
    "protocols": "tests.protocols",
    "pytest_configure": "tests.conftest",
    "r": "flext_tests",
    "s": "flext_tests",
    "sample_catalog": "tests.e2e.conftest",
    "shared_ldap_container": "tests.conftest",
    "t": ["tests.typings", "FlextTapLdapTestTypes"],
    "tap_config_file": "tests.e2e.conftest",
    "test_client": "tests.unit.test_client",
    "test_client_quick": "tests.unit.test_client_quick",
    "test_data_dir": "tests.conftest",
    "test_integration": "tests.e2e.test_integration",
    "test_ldif_processor": "tests.unit.test_ldif_processor",
    "test_ldif_stream": "tests.unit.test_ldif_stream",
    "test_models": "tests.unit.test_models",
    "test_streams": "tests.unit.test_streams",
    "test_tap": "tests.unit.test_tap",
    "typings": "tests.typings",
    "u": ["tests.utilities", "FlextTapLdapTestUtilities"],
    "unit": "tests.unit",
    "utilities": "tests.utilities",
    "x": "flext_tests",
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, sorted(_LAZY_IMPORTS))
