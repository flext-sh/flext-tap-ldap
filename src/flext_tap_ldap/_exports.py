# AUTO-GENERATED FILE — Regenerate with: make gen
"""Lazy export registry."""

from __future__ import annotations

from flext_core.lazy import build_lazy_import_map, merge_lazy_imports

_LOCAL_LAZY_IMPORTS = build_lazy_import_map(
    {
        "._utilities": ("_utilities",),
        ".api": (
            "FlextTapLdapService",
            "tap_ldap",
        ),
        ".constants": (
            "FlextTapLdapConstants",
            "c",
        ),
        ".models": (
            "FlextTapLdapModels",
            "m",
        ),
        ".protocols": (
            "FlextTapLdapProtocols",
            "p",
        ),
        ".settings": ("FlextTapLdapSettings",),
        ".tap": ("FlextTapLdapTap",),
        ".typings": (
            "FlextTapLdapTypes",
            "t",
        ),
        ".utilities": (
            "FlextTapLdapUtilities",
            "u",
        ),
        "flext_core._root_typing_parts.facades": (
            "d",
            "e",
            "h",
            "r",
            "s",
            "x",
        ),
    },
)

FLEXT_TAP_LDAP_LAZY_IMPORTS = merge_lazy_imports(
    (),
    _LOCAL_LAZY_IMPORTS,
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
    module_name="flext_tap_ldap",
)

__all__: list[str] = ["FLEXT_TAP_LDAP_LAZY_IMPORTS"]
