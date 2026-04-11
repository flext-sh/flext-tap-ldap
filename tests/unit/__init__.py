# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Tap Ldap package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if _t.TYPE_CHECKING:
    from flext_tap_ldap.test_client import TestLDAPClientCoverageBoost
    from flext_tap_ldap.test_client_quick import TestLDAPClientQuick
    from flext_tap_ldap.test_ldif_processor import TestLdifProcessor
    from flext_tap_ldap.test_ldif_stream import TestLDIFStreamBasic
    from flext_tap_ldap.test_models import (
        TestConnectionTestedEvent,
        TestRecordExtractedEvent,
        TestStreamDiscoveredEvent,
        TestTapExecutionCompletedEvent,
        TestTapExecutionStartedEvent,
    )
    from flext_tap_ldap.test_streams import (
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
    from flext_tap_ldap.test_tap import TestFlextTapLdapTap
_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".test_client": ("TestLDAPClientCoverageBoost",),
        ".test_client_quick": ("TestLDAPClientQuick",),
        ".test_ldif_processor": ("TestLdifProcessor",),
        ".test_ldif_stream": ("TestLDIFStreamBasic",),
        ".test_models": (
            "TestConnectionTestedEvent",
            "TestRecordExtractedEvent",
            "TestStreamDiscoveredEvent",
            "TestTapExecutionCompletedEvent",
            "TestTapExecutionStartedEvent",
        ),
        ".test_streams": (
            "TestCustomStream",
            "TestCustomStreamParams",
            "TestGroupsStream",
            "TestLDAPBaseStream",
            "TestLDAPBaseStreamDirectUsage",
            "TestOrganizationalUnitsStream",
            "TestSchemaStream",
            "TestStreamExceptionHandling",
            "TestStreamIntegration",
            "TestUsersStream",
        ),
        ".test_tap": ("TestFlextTapLdapTap",),
    },
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)

__all__ = [
    "TestConnectionTestedEvent",
    "TestCustomStream",
    "TestCustomStreamParams",
    "TestFlextTapLdapTap",
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
]
