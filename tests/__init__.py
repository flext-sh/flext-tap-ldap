# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import (
    build_lazy_import_map,
    install_lazy_exports,
    merge_lazy_imports,
)

if TYPE_CHECKING:
    from flext_tests import (
        d as d,
        e as e,
        h as h,
        r as r,
        td as td,
        tf as tf,
        tk as tk,
        tm as tm,
        tv as tv,
        x as x,
    )

    from tests.base import (
        TestsFlextTapLdapServiceBase as TestsFlextTapLdapServiceBase,
        s as s,
    )
    from tests.constants import (
        TestsFlextTapLdapConstants as TestsFlextTapLdapConstants,
        c as c,
    )
    from tests.e2e.test_integration import (
        TestsFlextTapLdapIntegration as TestsFlextTapLdapIntegration,
    )
    from tests.models import TestsFlextTapLdapModels as TestsFlextTapLdapModels, m as m
    from tests.protocols import (
        TestsFlextTapLdapProtocols as TestsFlextTapLdapProtocols,
        p,
    )
    from tests.settings import TestsFlextTapLdapSettings as TestsFlextTapLdapSettings
    from tests.typings import TestsFlextTapLdapTypes as TestsFlextTapLdapTypes, t as t
    from tests.unit.test_models import (
        TestsFlextTapLdapModelsUnit as TestsFlextTapLdapModelsUnit,
    )
    from tests.utilities import (
        TestsFlextTapLdapUtilities as TestsFlextTapLdapUtilities,
        u,
    )
_LAZY_IMPORTS = merge_lazy_imports(
    (".e2e", ".unit"),
    build_lazy_import_map({
        ".base": ("TestsFlextTapLdapServiceBase", "s"),
        ".conftest": ("conftest",),
        ".constants": ("TestsFlextTapLdapConstants", "c"),
        ".e2e": ("e2e",),
        ".e2e.test_integration": ("TestsFlextTapLdapIntegration",),
        ".models": ("TestsFlextTapLdapModels", "m"),
        ".protocols": ("TestsFlextTapLdapProtocols", "p"),
        ".settings": ("TestsFlextTapLdapSettings",),
        ".typings": ("TestsFlextTapLdapTypes", "t"),
        ".unit": ("unit",),
        ".unit.test_models": ("TestsFlextTapLdapModelsUnit",),
        ".utilities": ("TestsFlextTapLdapUtilities", "u"),
        "flext_tests": ("d", "e", "h", "r", "td", "tf", "tk", "tm", "tv", "x"),
    }),
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


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, publish_all=False)
