# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests package."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_cli import cli
    from flext_ldap import ldap
    from flext_ldif import ldif
    from flext_meltano import meltano
    from flext_tests import (
        active_rules,
        api,
        config,
        discover_repository_root,
        install_local_packages,
        load_infra_report,
        settings,
        split_csv,
        td,
        tf,
        tk,
        tm,
        tv,
    )

    from flext_core import core, d, e, h, lazy_attribute, r, x
    from flext_tap_ldap import main, tap_ldap

    from . import e2e, unit
    from .base import TestsFlextTapLdapServiceBase, TestsFlextTapLdapServiceBase as s
    from .constants import TestsFlextTapLdapConstants, TestsFlextTapLdapConstants as c
    from .models import TestsFlextTapLdapModels, TestsFlextTapLdapModels as m
    from .protocols import TestsFlextTapLdapProtocols, TestsFlextTapLdapProtocols as p
    from .settings import TestsFlextTapLdapSettings
    from .typings import TestsFlextTapLdapTypes, TestsFlextTapLdapTypes as t
    from .utilities import TestsFlextTapLdapUtilities, TestsFlextTapLdapUtilities as u
__all__: tuple[str, ...] = (
    "TestsFlextTapLdapConstants",
    "TestsFlextTapLdapModels",
    "TestsFlextTapLdapProtocols",
    "TestsFlextTapLdapServiceBase",
    "TestsFlextTapLdapSettings",
    "TestsFlextTapLdapTypes",
    "TestsFlextTapLdapUtilities",
    "active_rules",
    "api",
    "c",
    "cli",
    "config",
    "core",
    "d",
    "discover_repository_root",
    "e",
    "e2e",
    "h",
    "install_local_packages",
    "lazy_attribute",
    "ldap",
    "ldif",
    "load_infra_report",
    "m",
    "main",
    "meltano",
    "p",
    "r",
    "s",
    "settings",
    "split_csv",
    "t",
    "tap_ldap",
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
            "flext_cli": ("cli",),
            "flext_core": ("core", "d", "e", "h", "lazy_attribute", "r", "x"),
            "flext_ldap": ("ldap",),
            "flext_ldif": ("ldif",),
            "flext_meltano": ("meltano",),
            "flext_tap_ldap": ("main", "tap_ldap"),
            "flext_tests": (
                "active_rules",
                "api",
                "config",
                "discover_repository_root",
                "install_local_packages",
                "load_infra_report",
                "settings",
                "split_csv",
                "td",
                "tf",
                "tk",
                "tm",
                "tv",
            ),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
