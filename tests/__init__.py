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
    from tests.e2e.test_integration import TestsFlextTapLdapIntegration
    from tests.models import TestsFlextTapLdapModels, m
    from tests.protocols import TestsFlextTapLdapProtocols, p
    from tests.typings import TestsFlextTapLdapTypes, t
    from tests.unit.test_client import TestsFlextTapLdapClient
    from tests.unit.test_client_quick import TestsFlextTapLdapClientQuick
    from tests.unit.test_ldif_processor import TestsFlextTapLdapLdifProcessor
    from tests.unit.test_ldif_stream import TestsFlextTapLdapLdifStream
    from tests.unit.test_models import TestsFlextTapLdapModelsUnit
    from tests.unit.test_tap import TestsFlextTapLdapTap
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
            ".e2e.test_integration": ("TestsFlextTapLdapIntegration",),
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
            ".unit.test_client": ("TestsFlextTapLdapClient",),
            ".unit.test_client_quick": ("TestsFlextTapLdapClientQuick",),
            ".unit.test_ldif_processor": ("TestsFlextTapLdapLdifProcessor",),
            ".unit.test_ldif_stream": ("TestsFlextTapLdapLdifStream",),
            ".unit.test_models": ("TestsFlextTapLdapModelsUnit",),
            ".unit.test_tap": ("TestsFlextTapLdapTap",),
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
        "pytest_addoption",
        "pytest_collect_file",
        "pytest_collection_modifyitems",
        "pytest_configure",
        "pytest_runtest_setup",
        "pytest_runtest_teardown",
        "pytest_sessionfinish",
        "pytest_sessionstart",
        "pytest_terminal_summary",
        "pytest_warning_recorded",
    ),
    module_name=__name__,
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)

__all__: list[str] = [
    "TestsFlextTapLdapClient",
    "TestsFlextTapLdapClientQuick",
    "TestsFlextTapLdapConstants",
    "TestsFlextTapLdapIntegration",
    "TestsFlextTapLdapLdifProcessor",
    "TestsFlextTapLdapLdifStream",
    "TestsFlextTapLdapModels",
    "TestsFlextTapLdapModelsUnit",
    "TestsFlextTapLdapProtocols",
    "TestsFlextTapLdapTap",
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
