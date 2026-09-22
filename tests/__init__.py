# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests package."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_ldap import adapters, ldap
    from flext_meltano import meltano
    from flext_tests import (
        api,
        cli,
        config,
        core,
        d,
        e,
        from_json,
        h,
        install_local_packages,
        lazy_attribute,
        load_infra_report,
        r,
        services,
        settings,
        td,
        tf,
        tk,
        tm,
        to_json,
        to_jsonable_python,
        tv,
        x,
    )

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
    "adapters",
    "api",
    "c",
    "cli",
    "config",
    "core",
    "d",
    "e",
    "e2e",
    "from_json",
    "h",
    "install_local_packages",
    "lazy_attribute",
    "ldap",
    "load_infra_report",
    "m",
    "main",
    "meltano",
    "p",
    "r",
    "s",
    "services",
    "settings",
    "t",
    "tap_ldap",
    "td",
    "tf",
    "tk",
    "tm",
    "to_json",
    "to_jsonable_python",
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
            "flext_ldap": ("adapters", "ldap"),
            "flext_meltano": ("meltano",),
            "flext_tap_ldap": ("main", "tap_ldap"),
            "flext_tests": (
                "api",
                "cli",
                "config",
                "core",
                "d",
                "e",
                "from_json",
                "h",
                "install_local_packages",
                "lazy_attribute",
                "load_infra_report",
                "r",
                "services",
                "settings",
                "td",
                "tf",
                "tk",
                "tm",
                "to_json",
                "to_jsonable_python",
                "tv",
                "x",
            ),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
