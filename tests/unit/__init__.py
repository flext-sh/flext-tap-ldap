# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Unit package."""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import cleanup_submodule_namespace, lazy_getattr

if TYPE_CHECKING:
    from flext_core import FlextTypes

    from tests.unit import (
        test_client,
        test_client_quick,
        test_ldif_processor,
        test_ldif_stream,
        test_models,
        test_streams,
        test_tap,
    )
    from tests.unit.test_client import TestLDAPClientCoverageBoost
    from tests.unit.test_client_quick import TestLDAPClientQuick
    from tests.unit.test_ldif_processor import TestLdifProcessor
    from tests.unit.test_ldif_stream import TestLDIFStreamBasic
    from tests.unit.test_models import (
        TestConnectionTestedEvent,
        TestRecordExtractedEvent,
        TestStreamDiscoveredEvent,
        TestTapExecutionCompletedEvent,
        TestTapExecutionStartedEvent,
    )
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
    from tests.unit.test_tap import TestFlextTapLdapTapUnit

_LAZY_IMPORTS: Mapping[str, Sequence[str]] = {
    "TestConnectionTestedEvent": [
        "tests.unit.test_models",
        "TestConnectionTestedEvent",
    ],
    "TestCustomStream": ["tests.unit.test_streams", "TestCustomStream"],
    "TestCustomStreamParams": ["tests.unit.test_streams", "TestCustomStreamParams"],
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
    "test_client": ["tests.unit.test_client", ""],
    "test_client_quick": ["tests.unit.test_client_quick", ""],
    "test_ldif_processor": ["tests.unit.test_ldif_processor", ""],
    "test_ldif_stream": ["tests.unit.test_ldif_stream", ""],
    "test_models": ["tests.unit.test_models", ""],
    "test_streams": ["tests.unit.test_streams", ""],
    "test_tap": ["tests.unit.test_tap", ""],
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
    "test_client",
    "test_client_quick",
    "test_ldif_processor",
    "test_ldif_stream",
    "test_models",
    "test_streams",
    "test_tap",
]


_LAZY_CACHE: MutableMapping[str, FlextTypes.ModuleExport] = {}


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


def __dir__() -> Sequence[str]:
    """Return list of available attributes for dir() and autocomplete.

    Returns:
        List of public names from module exports.

    """
    return sorted(__all__)


cleanup_submodule_namespace(__name__, _LAZY_IMPORTS)
