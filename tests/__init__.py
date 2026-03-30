# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Tests package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from tests import (
        conftest as conftest,
        constants as constants,
        e2e as e2e,
        models as models,
        protocols as protocols,
        typings as typings,
        unit as unit,
        utilities as utilities,
    )
    from tests.conftest import (
        pytest_configure as pytest_configure,
        shared_ldap_container as shared_ldap_container,
        test_data_dir as test_data_dir,
    )
    from tests.constants import (
        FlextTapLdapTestConstants as FlextTapLdapTestConstants,
        FlextTapLdapTestConstants as c,
    )
    from tests.e2e import test_integration as test_integration
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
    from tests.models import (
        FlextTapLdapTestModels as FlextTapLdapTestModels,
        FlextTapLdapTestModels as m,
    )
    from tests.protocols import (
        FlextTapLdapTestProtocols as FlextTapLdapTestProtocols,
        FlextTapLdapTestProtocols as p,
    )
    from tests.typings import (
        FlextTapLdapTestTypes as FlextTapLdapTestTypes,
        FlextTapLdapTestTypes as t,
    )
    from tests.unit import (
        test_client as test_client,
        test_client_quick as test_client_quick,
        test_ldif_processor as test_ldif_processor,
        test_ldif_stream as test_ldif_stream,
        test_models as test_models,
        test_streams as test_streams,
        test_tap as test_tap,
    )
    from tests.unit.test_client import (
        TestLDAPClientCoverageBoost as TestLDAPClientCoverageBoost,
    )
    from tests.unit.test_client_quick import TestLDAPClientQuick as TestLDAPClientQuick
    from tests.unit.test_ldif_processor import TestLdifProcessor as TestLdifProcessor
    from tests.unit.test_ldif_stream import TestLDIFStreamBasic as TestLDIFStreamBasic
    from tests.unit.test_models import (
        TestConnectionTestedEvent as TestConnectionTestedEvent,
        TestRecordExtractedEvent as TestRecordExtractedEvent,
        TestStreamDiscoveredEvent as TestStreamDiscoveredEvent,
        TestTapExecutionCompletedEvent as TestTapExecutionCompletedEvent,
        TestTapExecutionStartedEvent as TestTapExecutionStartedEvent,
    )
    from tests.unit.test_streams import (
        TestCustomStream as TestCustomStream,
        TestCustomStreamParams as TestCustomStreamParams,
        TestGroupsStream as TestGroupsStream,
        TestLDAPBaseStream as TestLDAPBaseStream,
        TestLDAPBaseStreamDirectUsage as TestLDAPBaseStreamDirectUsage,
        TestOrganizationalUnitsStream as TestOrganizationalUnitsStream,
        TestSchemaStream as TestSchemaStream,
        TestStreamExceptionHandling as TestStreamExceptionHandling,
        TestStreamIntegration as TestStreamIntegration,
        TestUsersStream as TestUsersStream,
    )
    from tests.unit.test_tap import TestFlextTapLdapTapUnit as TestFlextTapLdapTapUnit
    from tests.utilities import (
        FlextTapLdapTestUtilities as FlextTapLdapTestUtilities,
        FlextTapLdapTestUtilities as u,
    )

_LAZY_IMPORTS: Mapping[str, Sequence[str]] = {
    "FlextTapLdapTestConstants": ["tests.constants", "FlextTapLdapTestConstants"],
    "FlextTapLdapTestModels": ["tests.models", "FlextTapLdapTestModels"],
    "FlextTapLdapTestProtocols": ["tests.protocols", "FlextTapLdapTestProtocols"],
    "FlextTapLdapTestTypes": ["tests.typings", "FlextTapLdapTestTypes"],
    "FlextTapLdapTestUtilities": ["tests.utilities", "FlextTapLdapTestUtilities"],
    "TestConnectionTestedEvent": [
        "tests.unit.test_models",
        "TestConnectionTestedEvent",
    ],
    "TestCustomStream": ["tests.unit.test_streams", "TestCustomStream"],
    "TestCustomStreamParams": ["tests.unit.test_streams", "TestCustomStreamParams"],
    "TestFlextTapLdapIntegration": [
        "tests.e2e.test_integration",
        "TestFlextTapLdapIntegration",
    ],
    "TestFlextTapLdapTapUnit": ["tests.unit.test_tap", "TestFlextTapLdapTapUnit"],
    "TestGroupsStream": ["tests.unit.test_streams", "TestGroupsStream"],
    "TestLDAPBaseStream": ["tests.unit.test_streams", "TestLDAPBaseStream"],
    "TestLDAPBaseStreamDirectUsage": [
        "tests.unit.test_streams",
        "TestLDAPBaseStreamDirectUsage",
    ],
    "TestLDAPClientCoverageBoost": [
        "tests.unit.test_client",
        "TestLDAPClientCoverageBoost",
    ],
    "TestLDAPClientQuick": ["tests.unit.test_client_quick", "TestLDAPClientQuick"],
    "TestLDIFStreamBasic": ["tests.unit.test_ldif_stream", "TestLDIFStreamBasic"],
    "TestLdifProcessor": ["tests.unit.test_ldif_processor", "TestLdifProcessor"],
    "TestOrganizationalUnitsStream": [
        "tests.unit.test_streams",
        "TestOrganizationalUnitsStream",
    ],
    "TestRecordExtractedEvent": ["tests.unit.test_models", "TestRecordExtractedEvent"],
    "TestSchemaStream": ["tests.unit.test_streams", "TestSchemaStream"],
    "TestStreamDiscoveredEvent": [
        "tests.unit.test_models",
        "TestStreamDiscoveredEvent",
    ],
    "TestStreamExceptionHandling": [
        "tests.unit.test_streams",
        "TestStreamExceptionHandling",
    ],
    "TestStreamIntegration": ["tests.unit.test_streams", "TestStreamIntegration"],
    "TestTapExecutionCompletedEvent": [
        "tests.unit.test_models",
        "TestTapExecutionCompletedEvent",
    ],
    "TestTapExecutionStartedEvent": [
        "tests.unit.test_models",
        "TestTapExecutionStartedEvent",
    ],
    "TestUsersStream": ["tests.unit.test_streams", "TestUsersStream"],
    "c": ["tests.constants", "FlextTapLdapTestConstants"],
    "catalog_file": ["tests.e2e.conftest", "catalog_file"],
    "conftest": ["tests.conftest", ""],
    "constants": ["tests.constants", ""],
    "d": ["flext_tests", "d"],
    "e": ["flext_tests", "e"],
    "e2e": ["tests.e2e", ""],
    "h": ["flext_tests", "h"],
    "ldap_connection": ["tests.e2e.conftest", "ldap_connection"],
    "ldap_container": ["tests.e2e.conftest", "ldap_container"],
    "logger": ["tests.e2e.conftest", "logger"],
    "m": ["tests.models", "FlextTapLdapTestModels"],
    "models": ["tests.models", ""],
    "p": ["tests.protocols", "FlextTapLdapTestProtocols"],
    "project_root": ["tests.e2e.conftest", "project_root"],
    "protocols": ["tests.protocols", ""],
    "pytest_configure": ["tests.conftest", "pytest_configure"],
    "r": ["flext_tests", "r"],
    "s": ["flext_tests", "s"],
    "sample_catalog": ["tests.e2e.conftest", "sample_catalog"],
    "shared_ldap_container": ["tests.conftest", "shared_ldap_container"],
    "t": ["tests.typings", "FlextTapLdapTestTypes"],
    "tap_config_file": ["tests.e2e.conftest", "tap_config_file"],
    "test_client": ["tests.unit.test_client", ""],
    "test_client_quick": ["tests.unit.test_client_quick", ""],
    "test_data_dir": ["tests.conftest", "test_data_dir"],
    "test_integration": ["tests.e2e.test_integration", ""],
    "test_ldif_processor": ["tests.unit.test_ldif_processor", ""],
    "test_ldif_stream": ["tests.unit.test_ldif_stream", ""],
    "test_models": ["tests.unit.test_models", ""],
    "test_streams": ["tests.unit.test_streams", ""],
    "test_tap": ["tests.unit.test_tap", ""],
    "typings": ["tests.typings", ""],
    "u": ["tests.utilities", "FlextTapLdapTestUtilities"],
    "unit": ["tests.unit", ""],
    "utilities": ["tests.utilities", ""],
    "x": ["flext_tests", "x"],
}

_EXPORTS: Sequence[str] = [
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


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, _EXPORTS)
