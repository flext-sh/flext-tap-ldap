# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_tests import api, d, e, h, r, td, tf, tk, tm, x

    from tests import e2e, unit
    from tests.base import TestsFlextTapLdapServiceBase, s
    from tests.constants import TestsFlextTapLdapConstants, c
    from tests.models import TestsFlextTapLdapModels, m
    from tests.protocols import TestsFlextTapLdapProtocols, p
    from tests.settings import TestsFlextTapLdapSettings
    from tests.typings import TestsFlextTapLdapTypes, t
    from tests.utilities import TestsFlextTapLdapUtilities, u


__all__: tuple[str, ...] = (
    "TestsFlextTapLdapConstants",
    "TestsFlextTapLdapModels",
    "TestsFlextTapLdapProtocols",
    "TestsFlextTapLdapServiceBase",
    "TestsFlextTapLdapSettings",
    "TestsFlextTapLdapTypes",
    "TestsFlextTapLdapUtilities",
    "api",
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
            "flext_tests": ("api", "d", "e", "h", "r", "td", "tf", "tk", "tm", "x"),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    ),
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
