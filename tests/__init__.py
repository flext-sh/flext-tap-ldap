# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_tests import api, d, e, h, r, td, tf, tk, tm, x

    from flext_tap_ldap import config, main, settings, tap_ldap
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
    "config",
    "d",
    "e",
    "h",
    "m",
    "main",
    "p",
    "r",
    "s",
    "settings",
    "t",
    "tap_ldap",
    "td",
    "tf",
    "tk",
    "tm",
    "u",
    "x",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "TestsFlextTapLdapConstants": ".constants",
        "TestsFlextTapLdapModels": ".models",
        "TestsFlextTapLdapProtocols": ".protocols",
        "TestsFlextTapLdapServiceBase": ".base",
        "TestsFlextTapLdapSettings": ".settings",
        "TestsFlextTapLdapTypes": ".typings",
        "TestsFlextTapLdapUtilities": ".utilities",
        "api": "flext_tests",
        "c": ".constants",
        "config": "flext_tap_ldap",
        "d": "flext_tests",
        "e": "flext_tests",
        "h": "flext_tests",
        "m": ".models",
        "main": "flext_tap_ldap",
        "p": ".protocols",
        "r": "flext_tests",
        "s": ".base",
        "settings": "flext_tap_ldap",
        "t": ".typings",
        "tap_ldap": "flext_tap_ldap",
        "td": "flext_tests",
        "tf": "flext_tests",
        "tk": "flext_tests",
        "tm": "flext_tests",
        "u": ".utilities",
        "x": "flext_tests",
    }),
    public_exports=__all__,
)
