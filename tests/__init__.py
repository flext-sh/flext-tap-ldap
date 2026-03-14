# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make codegen
#
"""Test module for flext-tap-ldap.

This module provides test infrastructure for flext-tap-ldap using unified namespace patterns.
Test objects are accessed via m.TapLdap.Tests.*, u.TapLdap.*, etc.
Combines FlextTests* with project-specific functionality.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import cleanup_submodule_namespace, lazy_getattr

if TYPE_CHECKING:
    from flext_core.typings import FlextTypes

    from tests.conftest import (
        project_root,
        pytest_configure,
        shared_ldap_container,
        test_data_dir,
    )
    from tests.constants import (
        TestsFlextTapLdapConstants,
        TestsFlextTapLdapConstants as c,
    )
    from tests.e2e.conftest import (
        catalog_file,
        ldap_connection,
        ldap_container,
        logger,
        sample_catalog,
        tap_config_file,
    )
    from tests.models import TestsFlextTapLdapModels, m
    from tests.protocols import TestsFlextTapLdapProtocols, p
    from tests.test_client import TestLDAPClientCoverageBoost
    from tests.test_client_quick import LDAPClient, TestLDAPClientQuick
    from tests.test_integration import TestFlextTapLdapIntegration
    from tests.test_ldif_processor import (
        TestPlaceholder,
        test_directory_processing_traverses_ldap_dit_with_mock_connection,
        test_ldif_directory_processing_traverses_ldif_files,
        test_transform_entry_applies_rules,
        test_transform_entry_applies_schema_mappings,
    )
    from tests.test_ldif_stream import TestLDIFStreamBasic
    from tests.test_models import (
        TestConnectionTestedEvent,
        TestRecordExtractedEvent,
        TestStreamDiscoveredEvent,
        TestTapExecutionCompletedEvent,
        TestTapExecutionStartedEvent,
    )
    from tests.test_streams import (
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
    from tests.test_tap import TestFlextTapLdapTapUnit
    from tests.typings import TestsFlextTapLdapTypes, t
    from tests.utilities import TestsFlextTapLdapUtilities, u

# Lazy import mapping: export_name -> (module_path, attr_name)
_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    "LDAPClient": ("tests.test_client_quick", "LDAPClient"),
    "TestConnectionTestedEvent": ("tests.test_models", "TestConnectionTestedEvent"),
    "TestCustomStream": ("tests.test_streams", "TestCustomStream"),
    "TestCustomStreamParams": ("tests.test_streams", "TestCustomStreamParams"),
    "TestFlextTapLdapIntegration": ("tests.test_integration", "TestFlextTapLdapIntegration"),
    "TestFlextTapLdapTapUnit": ("tests.test_tap", "TestFlextTapLdapTapUnit"),
    "TestGroupsStream": ("tests.test_streams", "TestGroupsStream"),
    "TestLDAPBaseStream": ("tests.test_streams", "TestLDAPBaseStream"),
    "TestLDAPBaseStreamDirectUsage": ("tests.test_streams", "TestLDAPBaseStreamDirectUsage"),
    "TestLDAPClientCoverageBoost": ("tests.test_client", "TestLDAPClientCoverageBoost"),
    "TestLDAPClientQuick": ("tests.test_client_quick", "TestLDAPClientQuick"),
    "TestLDIFStreamBasic": ("tests.test_ldif_stream", "TestLDIFStreamBasic"),
    "TestOrganizationalUnitsStream": ("tests.test_streams", "TestOrganizationalUnitsStream"),
    "TestPlaceholder": ("tests.test_ldif_processor", "TestPlaceholder"),
    "TestRecordExtractedEvent": ("tests.test_models", "TestRecordExtractedEvent"),
    "TestSchemaStream": ("tests.test_streams", "TestSchemaStream"),
    "TestStreamDiscoveredEvent": ("tests.test_models", "TestStreamDiscoveredEvent"),
    "TestStreamExceptionHandling": ("tests.test_streams", "TestStreamExceptionHandling"),
    "TestStreamIntegration": ("tests.test_streams", "TestStreamIntegration"),
    "TestTapExecutionCompletedEvent": ("tests.test_models", "TestTapExecutionCompletedEvent"),
    "TestTapExecutionStartedEvent": ("tests.test_models", "TestTapExecutionStartedEvent"),
    "TestUsersStream": ("tests.test_streams", "TestUsersStream"),
    "TestsFlextTapLdapConstants": ("tests.constants", "TestsFlextTapLdapConstants"),
    "TestsFlextTapLdapModels": ("tests.models", "TestsFlextTapLdapModels"),
    "TestsFlextTapLdapProtocols": ("tests.protocols", "TestsFlextTapLdapProtocols"),
    "TestsFlextTapLdapTypes": ("tests.typings", "TestsFlextTapLdapTypes"),
    "TestsFlextTapLdapUtilities": ("tests.utilities", "TestsFlextTapLdapUtilities"),
    "c": ("tests.constants", "TestsFlextTapLdapConstants"),
    "catalog_file": ("tests.e2e.conftest", "catalog_file"),
    "ldap_connection": ("tests.e2e.conftest", "ldap_connection"),
    "ldap_container": ("tests.e2e.conftest", "ldap_container"),
    "logger": ("tests.e2e.conftest", "logger"),
    "m": ("tests.models", "m"),
    "p": ("tests.protocols", "p"),
    "project_root": ("tests.conftest", "project_root"),
    "pytest_configure": ("tests.conftest", "pytest_configure"),
    "sample_catalog": ("tests.e2e.conftest", "sample_catalog"),
    "shared_ldap_container": ("tests.conftest", "shared_ldap_container"),
    "t": ("tests.typings", "t"),
    "tap_config_file": ("tests.e2e.conftest", "tap_config_file"),
    "test_data_dir": ("tests.conftest", "test_data_dir"),
    "test_directory_processing_traverses_ldap_dit_with_mock_connection": ("tests.test_ldif_processor", "test_directory_processing_traverses_ldap_dit_with_mock_connection"),
    "test_ldif_directory_processing_traverses_ldif_files": ("tests.test_ldif_processor", "test_ldif_directory_processing_traverses_ldif_files"),
    "test_transform_entry_applies_rules": ("tests.test_ldif_processor", "test_transform_entry_applies_rules"),
    "test_transform_entry_applies_schema_mappings": ("tests.test_ldif_processor", "test_transform_entry_applies_schema_mappings"),
    "u": ("tests.utilities", "u"),
}

__all__ = [
    "LDAPClient",
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
    "TestOrganizationalUnitsStream",
    "TestPlaceholder",
    "TestRecordExtractedEvent",
    "TestSchemaStream",
    "TestStreamDiscoveredEvent",
    "TestStreamExceptionHandling",
    "TestStreamIntegration",
    "TestTapExecutionCompletedEvent",
    "TestTapExecutionStartedEvent",
    "TestUsersStream",
    "TestsFlextTapLdapConstants",
    "TestsFlextTapLdapModels",
    "TestsFlextTapLdapProtocols",
    "TestsFlextTapLdapTypes",
    "TestsFlextTapLdapUtilities",
    "c",
    "catalog_file",
    "ldap_connection",
    "ldap_container",
    "logger",
    "m",
    "p",
    "project_root",
    "pytest_configure",
    "sample_catalog",
    "shared_ldap_container",
    "t",
    "tap_config_file",
    "test_data_dir",
    "test_directory_processing_traverses_ldap_dit_with_mock_connection",
    "test_ldif_directory_processing_traverses_ldif_files",
    "test_transform_entry_applies_rules",
    "test_transform_entry_applies_schema_mappings",
    "u",
]


def __getattr__(name: str) -> FlextTypes.ModuleExport:
    """Lazy-load module attributes on first access (PEP 562)."""
    return lazy_getattr(name, _LAZY_IMPORTS, globals(), __name__)


def __dir__() -> list[str]:
    """Return list of available attributes for dir() and autocomplete."""
    return sorted(__all__)


cleanup_submodule_namespace(__name__, _LAZY_IMPORTS)
