# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from types import MappingProxyType

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from . import e2e as e2e
    from . import unit as unit
    from flext_tap_ldap import FlextTapLdapConstants
    from flext_tests import FlextTestsConstants, d, e, h, r, td, tf, tk, tm, tv, x
    from typing import Final

    from .base import TestsFlextTapLdapServiceBase, TestsFlextTapLdapServiceBase as s
    from .constants import TestsFlextTapLdapConstants, TestsFlextTapLdapConstants as c
    from .models import TestsFlextTapLdapModels, TestsFlextTapLdapModels as m
    from .protocols import TestsFlextTapLdapProtocols, TestsFlextTapLdapProtocols as p
    from .settings import TestsFlextTapLdapSettings
    from .typings import TestsFlextTapLdapTypes, TestsFlextTapLdapTypes as t
    from .utilities import TestsFlextTapLdapUtilities, TestsFlextTapLdapUtilities as u
__all__: tuple[str, ...] = (
    "Final",
    "FlextTapLdapConstants",
    "FlextTestsConstants",
    "TestsFlextTapLdapConstants",
    "TestsFlextTapLdapModels",
    "TestsFlextTapLdapProtocols",
    "TestsFlextTapLdapServiceBase",
    "TestsFlextTapLdapSettings",
    "TestsFlextTapLdapTypes",
    "TestsFlextTapLdapUtilities",
    "c",
    "d",
    "e",
    "e2e",
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
    "unit",
    "x",
)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            ".base": ("TestsFlextTapLdapServiceBase", "s"),
            ".constants": ("TestsFlextTapLdapConstants", "c"),
            ".e2e": ("e2e",),
            ".models": ("TestsFlextTapLdapModels", "m"),
            ".protocols": ("TestsFlextTapLdapProtocols", "p"),
            ".settings": ("TestsFlextTapLdapSettings",),
            ".typings": ("TestsFlextTapLdapTypes", "t"),
            ".unit": ("unit",),
            ".utilities": ("TestsFlextTapLdapUtilities", "u"),
            "flext_tap_ldap": ("FlextTapLdapConstants",),
            "flext_tests": (
                "FlextTestsConstants",
                "d",
                "e",
                "h",
                "r",
                "td",
                "tf",
                "tk",
                "tm",
                "tv",
                "x",
            ),
            "typing": ("Final",),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
