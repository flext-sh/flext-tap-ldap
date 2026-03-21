# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make codegen
#
"""Tests package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import cleanup_submodule_namespace, lazy_getattr

if TYPE_CHECKING:
    from flext_core.typings import FlextTypes

    from flext_tap_ldap import d, e, h, r, s, x

    from . import e2e as e2e, unit as unit
    from .conftest import (
        project_root,
        pytest_configure,
        shared_ldap_container,
        test_data_dir,
    )
    from .constants import TestsFlextTapLdapConstants, TestsFlextTapLdapConstants as c
    from .e2e import (
        TestFlextTapLdapIntegration,
        catalog_file,
        ldap_connection,
        ldap_container,
        logger,
        sample_catalog,
        tap_config_file,
    )
    from .models import TestsFlextTapLdapModels, TestsFlextTapLdapModels as m
    from .protocols import TestsFlextTapLdapProtocols, TestsFlextTapLdapProtocols as p
    from .typings import TestsFlextTapLdapTypes, TestsFlextTapLdapTypes as t
    from .unit import (
        TestConnectionTestedEvent,
        TestCustomStream,
        TestCustomStreamParams,
        TestFlextTapLdapTapUnit,
        TestGroupsStream,
        TestLDAPBaseStream,
        TestLDAPBaseStreamDirectUsage,
        TestLDAPClientCoverageBoost,
        TestLDAPClientQuick,
        TestLdifProcessor,
        TestLDIFStreamBasic,
        TestOrganizationalUnitsStream,
        TestRecordExtractedEvent,
        TestSchemaStream,
        TestStreamDiscoveredEvent,
        TestStreamExceptionHandling,
        TestStreamIntegration,
        TestTapExecutionCompletedEvent,
        TestTapExecutionStartedEvent,
        TestUsersStream,
    )
    from .utilities import TestsFlextTapLdapUtilities, TestsFlextTapLdapUtilities as u

_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    "TestConnectionTestedEvent": ("tests.unit", "TestConnectionTestedEvent"),
    "TestCustomStream": ("tests.unit", "TestCustomStream"),
    "TestCustomStreamParams": ("tests.unit", "TestCustomStreamParams"),
    "TestFlextTapLdapIntegration": ("tests.e2e", "TestFlextTapLdapIntegration"),
    "TestFlextTapLdapTapUnit": ("tests.unit", "TestFlextTapLdapTapUnit"),
    "TestGroupsStream": ("tests.unit", "TestGroupsStream"),
    "TestLDAPBaseStream": ("tests.unit", "TestLDAPBaseStream"),
    "TestLDAPBaseStreamDirectUsage": ("tests.unit", "TestLDAPBaseStreamDirectUsage"),
    "TestLDAPClientCoverageBoost": ("tests.unit", "TestLDAPClientCoverageBoost"),
    "TestLDAPClientQuick": ("tests.unit", "TestLDAPClientQuick"),
    "TestLDIFStreamBasic": ("tests.unit", "TestLDIFStreamBasic"),
    "TestLdifProcessor": ("tests.unit", "TestLdifProcessor"),
    "TestOrganizationalUnitsStream": ("tests.unit", "TestOrganizationalUnitsStream"),
    "TestRecordExtractedEvent": ("tests.unit", "TestRecordExtractedEvent"),
    "TestSchemaStream": ("tests.unit", "TestSchemaStream"),
    "TestStreamDiscoveredEvent": ("tests.unit", "TestStreamDiscoveredEvent"),
    "TestStreamExceptionHandling": ("tests.unit", "TestStreamExceptionHandling"),
    "TestStreamIntegration": ("tests.unit", "TestStreamIntegration"),
    "TestTapExecutionCompletedEvent": ("tests.unit", "TestTapExecutionCompletedEvent"),
    "TestTapExecutionStartedEvent": ("tests.unit", "TestTapExecutionStartedEvent"),
    "TestUsersStream": ("tests.unit", "TestUsersStream"),
    "TestsFlextTapLdapConstants": ("tests.constants", "TestsFlextTapLdapConstants"),
    "TestsFlextTapLdapModels": ("tests.models", "TestsFlextTapLdapModels"),
    "TestsFlextTapLdapProtocols": ("tests.protocols", "TestsFlextTapLdapProtocols"),
    "TestsFlextTapLdapTypes": ("tests.typings", "TestsFlextTapLdapTypes"),
    "TestsFlextTapLdapUtilities": ("tests.utilities", "TestsFlextTapLdapUtilities"),
    "c": ("tests.constants", "TestsFlextTapLdapConstants"),
    "catalog_file": ("tests.e2e", "catalog_file"),
    "d": ("flext_tap_ldap", "d"),
    "e": ("flext_tap_ldap", "e"),
    "e2e": ("tests.e2e", ""),
    "h": ("flext_tap_ldap", "h"),
    "ldap_connection": ("tests.e2e", "ldap_connection"),
    "ldap_container": ("tests.e2e", "ldap_container"),
    "logger": ("tests.e2e", "logger"),
    "m": ("tests.models", "TestsFlextTapLdapModels"),
    "p": ("tests.protocols", "TestsFlextTapLdapProtocols"),
    "project_root": ("tests.conftest", "project_root"),
    "pytest_configure": ("tests.conftest", "pytest_configure"),
    "r": ("flext_tap_ldap", "r"),
    "s": ("flext_tap_ldap", "s"),
    "sample_catalog": ("tests.e2e", "sample_catalog"),
    "shared_ldap_container": ("tests.conftest", "shared_ldap_container"),
    "t": ("tests.typings", "TestsFlextTapLdapTypes"),
    "tap_config_file": ("tests.e2e", "tap_config_file"),
    "test_data_dir": ("tests.conftest", "test_data_dir"),
    "u": ("tests.utilities", "TestsFlextTapLdapUtilities"),
    "unit": ("tests.unit", ""),
    "x": ("flext_tap_ldap", "x"),
}

__all__ = [
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
    "TestsFlextTapLdapConstants",
    "TestsFlextTapLdapModels",
    "TestsFlextTapLdapProtocols",
    "TestsFlextTapLdapTypes",
    "TestsFlextTapLdapUtilities",
    "c",
    "catalog_file",
    "d",
    "e",
    "e2e",
    "h",
    "ldap_connection",
    "ldap_container",
    "logger",
    "m",
    "p",
    "project_root",
    "pytest_configure",
    "r",
    "s",
    "sample_catalog",
    "shared_ldap_container",
    "t",
    "tap_config_file",
    "test_data_dir",
    "u",
    "unit",
    "x",
]


def __getattr__(name: str) -> FlextTypes.ModuleExport:
    """Lazy-load module attributes on first access (PEP 562)."""
    return lazy_getattr(name, _LAZY_IMPORTS, globals(), __name__)


def __dir__() -> list[str]:
    """Return list of available attributes for dir() and autocomplete."""
    return sorted(__all__)


cleanup_submodule_namespace(__name__, _LAZY_IMPORTS)
