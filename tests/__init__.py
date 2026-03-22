# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make codegen
#
"""Tests package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import cleanup_submodule_namespace, lazy_getattr

if TYPE_CHECKING:
    from flext_core.typings import FlextTypes
    from flext_tests import d, e, h, r, s, x

    from . import e2e as e2e, unit as unit
    from .conftest import pytest_configure, shared_ldap_container, test_data_dir
    from .constants import FlextTapLdapTestConstants, FlextTapLdapTestConstants as c
    from .e2e.conftest import (
        catalog_file,
        ldap_connection,
        ldap_container,
        logger,
        project_root,
        sample_catalog,
        tap_config_file,
    )
    from .e2e.test_integration import TestFlextTapLdapIntegration
    from .models import FlextTapLdapTestModels, FlextTapLdapTestModels as m
    from .protocols import FlextTapLdapTestProtocols, FlextTapLdapTestProtocols as p
    from .typings import FlextTapLdapTestTypes, FlextTapLdapTestTypes as t
    from .unit.test_client import TestLDAPClientCoverageBoost
    from .unit.test_client_quick import TestLDAPClientQuick
    from .unit.test_ldif_processor import TestLdifProcessor
    from .unit.test_ldif_stream import TestLDIFStreamBasic
    from .unit.test_models import (
        TestConnectionTestedEvent,
        TestRecordExtractedEvent,
        TestStreamDiscoveredEvent,
        TestTapExecutionCompletedEvent,
        TestTapExecutionStartedEvent,
    )
    from .unit.test_streams import (
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
    from .unit.test_tap import TestFlextTapLdapTapUnit
    from .utilities import FlextTapLdapTestUtilities, FlextTapLdapTestUtilities as u

_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    "FlextTapLdapTestConstants": ("tests.constants", "FlextTapLdapTestConstants"),
    "FlextTapLdapTestModels": ("tests.models", "FlextTapLdapTestModels"),
    "FlextTapLdapTestProtocols": ("tests.protocols", "FlextTapLdapTestProtocols"),
    "FlextTapLdapTestTypes": ("tests.typings", "FlextTapLdapTestTypes"),
    "FlextTapLdapTestUtilities": ("tests.utilities", "FlextTapLdapTestUtilities"),
    "TestConnectionTestedEvent": (
        "tests.unit.test_models",
        "TestConnectionTestedEvent",
    ),
    "TestCustomStream": ("tests.unit.test_streams", "TestCustomStream"),
    "TestCustomStreamParams": ("tests.unit.test_streams", "TestCustomStreamParams"),
    "TestFlextTapLdapIntegration": (
        "tests.e2e.test_integration",
        "TestFlextTapLdapIntegration",
    ),
    "TestFlextTapLdapTapUnit": ("tests.unit.test_tap", "TestFlextTapLdapTapUnit"),
    "TestGroupsStream": ("tests.unit.test_streams", "TestGroupsStream"),
    "TestLDAPBaseStream": ("tests.unit.test_streams", "TestLDAPBaseStream"),
    "TestLDAPBaseStreamDirectUsage": (
        "tests.unit.test_streams",
        "TestLDAPBaseStreamDirectUsage",
    ),
    "TestLDAPClientCoverageBoost": (
        "tests.unit.test_client",
        "TestLDAPClientCoverageBoost",
    ),
    "TestLDAPClientQuick": ("tests.unit.test_client_quick", "TestLDAPClientQuick"),
    "TestLDIFStreamBasic": ("tests.unit.test_ldif_stream", "TestLDIFStreamBasic"),
    "TestLdifProcessor": ("tests.unit.test_ldif_processor", "TestLdifProcessor"),
    "TestOrganizationalUnitsStream": (
        "tests.unit.test_streams",
        "TestOrganizationalUnitsStream",
    ),
    "TestRecordExtractedEvent": ("tests.unit.test_models", "TestRecordExtractedEvent"),
    "TestSchemaStream": ("tests.unit.test_streams", "TestSchemaStream"),
    "TestStreamDiscoveredEvent": (
        "tests.unit.test_models",
        "TestStreamDiscoveredEvent",
    ),
    "TestStreamExceptionHandling": (
        "tests.unit.test_streams",
        "TestStreamExceptionHandling",
    ),
    "TestStreamIntegration": ("tests.unit.test_streams", "TestStreamIntegration"),
    "TestTapExecutionCompletedEvent": (
        "tests.unit.test_models",
        "TestTapExecutionCompletedEvent",
    ),
    "TestTapExecutionStartedEvent": (
        "tests.unit.test_models",
        "TestTapExecutionStartedEvent",
    ),
    "TestUsersStream": ("tests.unit.test_streams", "TestUsersStream"),
    "c": ("tests.constants", "FlextTapLdapTestConstants"),
    "catalog_file": ("tests.e2e.conftest", "catalog_file"),
    "d": ("flext_tests", "d"),
    "e": ("flext_tests", "e"),
    "e2e": ("tests.e2e", ""),
    "h": ("flext_tests", "h"),
    "ldap_connection": ("tests.e2e.conftest", "ldap_connection"),
    "ldap_container": ("tests.e2e.conftest", "ldap_container"),
    "logger": ("tests.e2e.conftest", "logger"),
    "m": ("tests.models", "FlextTapLdapTestModels"),
    "p": ("tests.protocols", "FlextTapLdapTestProtocols"),
    "project_root": ("tests.e2e.conftest", "project_root"),
    "pytest_configure": ("tests.conftest", "pytest_configure"),
    "r": ("flext_tests", "r"),
    "s": ("flext_tests", "s"),
    "sample_catalog": ("tests.e2e.conftest", "sample_catalog"),
    "shared_ldap_container": ("tests.conftest", "shared_ldap_container"),
    "t": ("tests.typings", "FlextTapLdapTestTypes"),
    "tap_config_file": ("tests.e2e.conftest", "tap_config_file"),
    "test_data_dir": ("tests.conftest", "test_data_dir"),
    "u": ("tests.utilities", "FlextTapLdapTestUtilities"),
    "unit": ("tests.unit", ""),
    "x": ("flext_tests", "x"),
}

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


_LAZY_CACHE: dict[str, FlextTypes.ModuleExport] = {}


def __getattr__(name: str) -> FlextTypes.ModuleExport:
    """Lazy-load module attributes on first access (PEP 562).

    A local cache ``_LAZY_CACHE`` persists resolved objects across repeated
    accesses during process lifetime.

    Args:
        name: Attribute name requested by dir()/import.

    Returns:
        Lazy-loaded module export type.

    Raises:
        AttributeError: If attribute not registered.

    """
    if name in _LAZY_CACHE:
        return _LAZY_CACHE[name]

    value = lazy_getattr(name, _LAZY_IMPORTS, globals(), __name__)
    _LAZY_CACHE[name] = value
    return value


def __dir__() -> list[str]:
    """Return list of available attributes for dir() and autocomplete.

    Returns:
        List of public names from module exports.

    """
    return sorted(__all__)


cleanup_submodule_namespace(__name__, _LAZY_IMPORTS)
