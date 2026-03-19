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
    from .constants import TestsFlextTapLdapConstants, c
    from .e2e.conftest import (
        catalog_file,
        ldap_connection,
        ldap_container,
        logger,
        sample_catalog,
        tap_config_file,
    )
    from .e2e.test_integration import TestFlextTapLdapIntegration
    from .models import TestsFlextTapLdapModels, m
    from .protocols import TestsFlextTapLdapProtocols, p
    from .typings import TestsFlextTapLdapTypes, t
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
    from .utilities import TestsFlextTapLdapUtilities, u

_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
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
    "TestsFlextTapLdapConstants": ("tests.constants", "TestsFlextTapLdapConstants"),
    "TestsFlextTapLdapModels": ("tests.models", "TestsFlextTapLdapModels"),
    "TestsFlextTapLdapProtocols": ("tests.protocols", "TestsFlextTapLdapProtocols"),
    "TestsFlextTapLdapTypes": ("tests.typings", "TestsFlextTapLdapTypes"),
    "TestsFlextTapLdapUtilities": ("tests.utilities", "TestsFlextTapLdapUtilities"),
    "c": ("tests.constants", "c"),
    "catalog_file": ("tests.e2e.conftest", "catalog_file"),
    "d": ("flext_tap_ldap", "d"),
    "e": ("flext_tap_ldap", "e"),
    "e2e": ("tests.e2e", ""),
    "h": ("flext_tap_ldap", "h"),
    "ldap_connection": ("tests.e2e.conftest", "ldap_connection"),
    "ldap_container": ("tests.e2e.conftest", "ldap_container"),
    "logger": ("tests.e2e.conftest", "logger"),
    "m": ("tests.models", "m"),
    "p": ("tests.protocols", "p"),
    "project_root": ("tests.conftest", "project_root"),
    "pytest_configure": ("tests.conftest", "pytest_configure"),
    "r": ("flext_tap_ldap", "r"),
    "s": ("flext_tap_ldap", "s"),
    "sample_catalog": ("tests.e2e.conftest", "sample_catalog"),
    "shared_ldap_container": ("tests.conftest", "shared_ldap_container"),
    "t": ("tests.typings", "t"),
    "tap_config_file": ("tests.e2e.conftest", "tap_config_file"),
    "test_data_dir": ("tests.conftest", "test_data_dir"),
    "u": ("tests.utilities", "u"),
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
