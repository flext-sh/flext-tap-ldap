# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import (
    build_lazy_import_map,
    install_lazy_exports,
    merge_lazy_imports,
)

if _t.TYPE_CHECKING:
    from flext_tests import td, tf, tk, tm, tv

    from flext_tap_ldap import d, e, h, r, s, x
    from tests.constants import TestsFlextTapLdapConstants, c
    from tests.e2e.test_integration import TestFlextTapLdapIntegration
    from tests.models import TestsFlextTapLdapModels, m
    from tests.protocols import TestsFlextTapLdapProtocols, p
    from tests.typings import TestsFlextTapLdapTypes, t
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
    from tests.unit.test_tap import TestFlextTapLdapTap
    from tests.utilities import TestsFlextTapLdapUtilities, u
_LAZY_IMPORTS = merge_lazy_imports(
    (
        ".e2e",
        ".unit",
    ),
    build_lazy_import_map(
        {
            ".constants": (
                "TestsFlextTapLdapConstants",
                "c",
            ),
            ".e2e.test_integration": ("TestFlextTapLdapIntegration",),
            ".models": (
                "TestsFlextTapLdapModels",
                "m",
            ),
            ".protocols": (
                "TestsFlextTapLdapProtocols",
                "p",
            ),
            ".typings": (
                "TestsFlextTapLdapTypes",
                "t",
            ),
            ".unit.test_client": ("TestLDAPClientCoverageBoost",),
            ".unit.test_client_quick": ("TestLDAPClientQuick",),
            ".unit.test_ldif_processor": ("TestLdifProcessor",),
            ".unit.test_ldif_stream": ("TestLDIFStreamBasic",),
            ".unit.test_models": (
                "TestConnectionTestedEvent",
                "TestRecordExtractedEvent",
                "TestStreamDiscoveredEvent",
                "TestTapExecutionCompletedEvent",
                "TestTapExecutionStartedEvent",
            ),
            ".unit.test_streams": (
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
            ".unit.test_tap": ("TestFlextTapLdapTap",),
            ".utilities": (
                "TestsFlextTapLdapUtilities",
                "u",
            ),
            "flext_tap_ldap": (
                "d",
                "e",
                "h",
                "r",
                "s",
                "x",
            ),
            "flext_tests": (
                "td",
                "tf",
                "tk",
                "tm",
                "tv",
            ),
        },
    ),
    exclude_names=(
        "cleanup_submodule_namespace",
        "install_lazy_exports",
        "lazy_getattr",
        "logger",
        "merge_lazy_imports",
        "output",
        "output_reporting",
    ),
    module_name=__name__,
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)

__all__: list[str] = [
    "TestConnectionTestedEvent",
    "TestCustomStream",
    "TestCustomStreamParams",
    "TestFlextTapLdapIntegration",
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
    "TestsFlextTapLdapConstants",
    "TestsFlextTapLdapModels",
    "TestsFlextTapLdapProtocols",
    "TestsFlextTapLdapTypes",
    "TestsFlextTapLdapUtilities",
    "c",
    "d",
    "e",
    "h",
    "m",
    "p",
    "r",
    "s",
    "t",
    "td",
    "tf",
    "tk",
    "tm",
    "tv",
    "u",
    "x",
]
