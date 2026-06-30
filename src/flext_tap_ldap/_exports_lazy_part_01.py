# AUTO-GENERATED FILE — Regenerate with: make gen
"""Lazy export map part."""

from __future__ import annotations

from flext_core.lazy import build_lazy_import_map

FLEXT_TAP_LDAP_LAZY_IMPORTS_PART_01 = build_lazy_import_map(
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
    },
)

__all__: list[str] = ["FLEXT_TAP_LDAP_LAZY_IMPORTS_PART_01"]
