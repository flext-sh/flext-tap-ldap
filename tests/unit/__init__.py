# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Unit package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
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

_EXPORTS: Sequence[str] = [
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


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, _EXPORTS)
