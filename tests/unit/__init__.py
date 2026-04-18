# AUTO-GENERATED FILE — Regenerate with: make gen
"""Unit package."""

from __future__ import annotations

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

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


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, publish_all=False)
