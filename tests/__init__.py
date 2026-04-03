# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Tests package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import install_lazy_exports, merge_lazy_imports

if _t.TYPE_CHECKING:
    import tests.conftest as _tests_conftest

    conftest = _tests_conftest
    import tests.constants as _tests_constants
    from tests.conftest import pytest_configure, shared_ldap_container, test_data_dir

    constants = _tests_constants
    import tests.e2e as _tests_e2e
    from tests.constants import (
        FlextTapLdapTestConstants,
        FlextTapLdapTestConstants as c,
    )

    e2e = _tests_e2e
    import tests.e2e.test_integration as _tests_e2e_test_integration
    from tests.e2e.conftest import (
        catalog_file,
        ldap_connection,
        ldap_container,
        logger,
        project_root,
        sample_catalog,
        tap_config_file,
    )

    test_integration = _tests_e2e_test_integration
    import tests.models as _tests_models
    from tests.e2e.test_integration import TestFlextTapLdapIntegration

    models = _tests_models
    import tests.protocols as _tests_protocols
    from tests.models import FlextTapLdapTestModels, FlextTapLdapTestModels as m

    protocols = _tests_protocols
    import tests.typings as _tests_typings
    from tests.protocols import (
        FlextTapLdapTestProtocols,
        FlextTapLdapTestProtocols as p,
    )

    typings = _tests_typings
    import tests.unit as _tests_unit
    from tests.typings import FlextTapLdapTestTypes, FlextTapLdapTestTypes as t

    unit = _tests_unit
    import tests.unit.test_client as _tests_unit_test_client

    test_client = _tests_unit_test_client
    import tests.unit.test_client_quick as _tests_unit_test_client_quick
    from tests.unit.test_client import TestLDAPClientCoverageBoost

    test_client_quick = _tests_unit_test_client_quick
    import tests.unit.test_ldif_processor as _tests_unit_test_ldif_processor
    from tests.unit.test_client_quick import TestLDAPClientQuick

    test_ldif_processor = _tests_unit_test_ldif_processor
    import tests.unit.test_ldif_stream as _tests_unit_test_ldif_stream
    from tests.unit.test_ldif_processor import TestLdifProcessor

    test_ldif_stream = _tests_unit_test_ldif_stream
    import tests.unit.test_models as _tests_unit_test_models
    from tests.unit.test_ldif_stream import TestLDIFStreamBasic

    test_models = _tests_unit_test_models
    import tests.unit.test_streams as _tests_unit_test_streams
    from tests.unit.test_models import (
        TestConnectionTestedEvent,
        TestRecordExtractedEvent,
        TestStreamDiscoveredEvent,
        TestTapExecutionCompletedEvent,
        TestTapExecutionStartedEvent,
    )

    test_streams = _tests_unit_test_streams
    import tests.unit.test_tap as _tests_unit_test_tap
    from tests.unit.test_streams import (
        TestCustomStream,
        TestCustomStreamParams,
        TestGroupsStream,
        TestLDAPBaseStream,
        TestLDAPBaseStreamDirectUsage,
        TestOrganizationalUnitsStream,
        TestSchemaStream,
        TestStreamExceptionHandling,
        TestStreamIntegration,
        TestUsersStream,
    )

    test_tap = _tests_unit_test_tap
    import tests.utilities as _tests_utilities
    from tests.unit.test_tap import TestFlextTapLdapTapUnit

    utilities = _tests_utilities
    from flext_core.decorators import FlextDecorators as d
    from flext_core.exceptions import FlextExceptions as e
    from flext_core.handlers import FlextHandlers as h
    from flext_core.mixins import FlextMixins as x
    from flext_core.result import FlextResult as r
    from flext_core.service import FlextService as s
    from tests.utilities import (
        FlextTapLdapTestUtilities,
        FlextTapLdapTestUtilities as u,
    )
_LAZY_IMPORTS = merge_lazy_imports(
    (
        "tests.e2e",
        "tests.unit",
    ),
    {
        "FlextTapLdapTestConstants": "tests.constants",
        "FlextTapLdapTestModels": "tests.models",
        "FlextTapLdapTestProtocols": "tests.protocols",
        "FlextTapLdapTestTypes": "tests.typings",
        "FlextTapLdapTestUtilities": "tests.utilities",
        "c": ("tests.constants", "FlextTapLdapTestConstants"),
        "conftest": "tests.conftest",
        "constants": "tests.constants",
        "d": ("flext_core.decorators", "FlextDecorators"),
        "e": ("flext_core.exceptions", "FlextExceptions"),
        "e2e": "tests.e2e",
        "h": ("flext_core.handlers", "FlextHandlers"),
        "m": ("tests.models", "FlextTapLdapTestModels"),
        "models": "tests.models",
        "p": ("tests.protocols", "FlextTapLdapTestProtocols"),
        "protocols": "tests.protocols",
        "pytest_configure": "tests.conftest",
        "r": ("flext_core.result", "FlextResult"),
        "s": ("flext_core.service", "FlextService"),
        "shared_ldap_container": "tests.conftest",
        "t": ("tests.typings", "FlextTapLdapTestTypes"),
        "test_data_dir": "tests.conftest",
        "typings": "tests.typings",
        "u": ("tests.utilities", "FlextTapLdapTestUtilities"),
        "unit": "tests.unit",
        "utilities": "tests.utilities",
        "x": ("flext_core.mixins", "FlextMixins"),
    },
)

__all__ = [
    "FlextTapLdapTestConstants",
    "FlextTapLdapTestModels",
    "FlextTapLdapTestProtocols",
    "FlextTapLdapTestTypes",
    "FlextTapLdapTestUtilities",
    "TestConnectionTestedEvent",
    "TestCustomStream",
    "TestCustomStreamParams",
    "TestFlextTapLdapIntegration",
    "TestFlextTapLdapTapUnit",
    "TestGroupsStream",
    "TestLDAPBaseStream",
    "TestLDAPBaseStreamDirectUsage",
    "TestLDAPClientCoverageBoost",
    "TestLDAPClientQuick",
    "TestLDIFStreamBasic",
    "TestLdifProcessor",
    "TestOrganizationalUnitsStream",
    "TestRecordExtractedEvent",
    "TestSchemaStream",
    "TestStreamDiscoveredEvent",
    "TestStreamExceptionHandling",
    "TestStreamIntegration",
    "TestTapExecutionCompletedEvent",
    "TestTapExecutionStartedEvent",
    "TestUsersStream",
    "c",
    "catalog_file",
    "conftest",
    "constants",
    "d",
    "e",
    "e2e",
    "h",
    "ldap_connection",
    "ldap_container",
    "logger",
    "m",
    "models",
    "p",
    "project_root",
    "protocols",
    "pytest_configure",
    "r",
    "s",
    "sample_catalog",
    "shared_ldap_container",
    "t",
    "tap_config_file",
    "test_client",
    "test_client_quick",
    "test_data_dir",
    "test_integration",
    "test_ldif_processor",
    "test_ldif_stream",
    "test_models",
    "test_streams",
    "test_tap",
    "typings",
    "u",
    "unit",
    "utilities",
    "x",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
