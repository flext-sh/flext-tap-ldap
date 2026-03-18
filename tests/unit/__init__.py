# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make codegen
#
"""Unit package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import cleanup_submodule_namespace, lazy_getattr

if TYPE_CHECKING:
    from flext_core.typings import FlextTypes

    from .test_client import TestLDAPClientCoverageBoost
    from .test_ldif_processor import TestLdifProcessor
    from .test_ldif_stream import TestLDIFStreamBasic
    from .test_models import (
        TestConnectionTestedEvent,
        TestRecordExtractedEvent,
        TestStreamDiscoveredEvent,
        TestTapExecutionCompletedEvent,
        TestTapExecutionStartedEvent,
    )
    from .test_streams import (
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
    from .test_tap import TestFlextTapLdapTapUnit

_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    "TestConnectionTestedEvent": (
        "tests.unit.test_models",
        "TestConnectionTestedEvent",
    ),
    "TestCustomStream": ("tests.unit.test_streams", "TestCustomStream"),
    "TestCustomStreamParams": ("tests.unit.test_streams", "TestCustomStreamParams"),
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
}

__all__ = [
    "TestConnectionTestedEvent",
    "TestCustomStream",
    "TestCustomStreamParams",
    "TestFlextTapLdapTapUnit",
    "TestGroupsStream",
    "TestLDAPBaseStream",
    "TestLDAPBaseStreamDirectUsage",
    "TestLDAPClientCoverageBoost",
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
]


def __getattr__(name: str) -> FlextTypes.ModuleExport:
    """Lazy-load module attributes on first access (PEP 562)."""
    return lazy_getattr(name, _LAZY_IMPORTS, globals(), __name__)


def __dir__() -> list[str]:
    """Return list of available attributes for dir() and autocomplete."""
    return sorted(__all__)


cleanup_submodule_namespace(__name__, _LAZY_IMPORTS)
