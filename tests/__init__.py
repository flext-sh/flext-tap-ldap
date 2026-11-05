# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_tests import api, d, e, h, r, td, tf, tk, tm, x

    from flext_tap_ldap import (
        FlextTapLdapConfig,
        FlextTapLdapConstants,
        FlextTapLdapModels,
        FlextTapLdapProtocols,
        FlextTapLdapService,
        FlextTapLdapServiceBase,
        FlextTapLdapSettings,
        FlextTapLdapTypes,
        FlextTapLdapUtilities,
        FlextTapLdapVersion,
        __author__,
        __author_email__,
        __description__,
        __license__,
        __title__,
        __url__,
        __version__,
        __version_info__,
        config,
        main,
        settings,
        tap_ldap,
    )
    from tests.base import TestsFlextTapLdapServiceBase, s
    from tests.constants import TestsFlextTapLdapConstants, c
    from tests.models import TestsFlextTapLdapModels, m
    from tests.protocols import TestsFlextTapLdapProtocols, p
    from tests.settings import TestsFlextTapLdapSettings
    from tests.typings import TestsFlextTapLdapTypes, t
    from tests.utilities import TestsFlextTapLdapUtilities, u


__all__: tuple[str, ...] = (
    "FlextTapLdapConfig",
    "FlextTapLdapConstants",
    "FlextTapLdapModels",
    "FlextTapLdapProtocols",
    "FlextTapLdapService",
    "FlextTapLdapServiceBase",
    "FlextTapLdapSettings",
    "FlextTapLdapTypes",
    "FlextTapLdapUtilities",
    "FlextTapLdapVersion",
    "TestsFlextTapLdapConstants",
    "TestsFlextTapLdapModels",
    "TestsFlextTapLdapProtocols",
    "TestsFlextTapLdapServiceBase",
    "TestsFlextTapLdapSettings",
    "TestsFlextTapLdapTypes",
    "TestsFlextTapLdapUtilities",
    "__author__",
    "__author_email__",
    "__description__",
    "__license__",
    "__title__",
    "__url__",
    "__version__",
    "__version_info__",
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
    {
        "FlextTapLdapConfig": "flext_tap_ldap",
        "FlextTapLdapConstants": "flext_tap_ldap",
        "FlextTapLdapModels": "flext_tap_ldap",
        "FlextTapLdapProtocols": "flext_tap_ldap",
        "FlextTapLdapService": "flext_tap_ldap",
        "FlextTapLdapServiceBase": "flext_tap_ldap",
        "FlextTapLdapSettings": "flext_tap_ldap",
        "FlextTapLdapTypes": "flext_tap_ldap",
        "FlextTapLdapUtilities": "flext_tap_ldap",
        "FlextTapLdapVersion": "flext_tap_ldap",
        "TestsFlextTapLdapConstants": ".constants",
        "TestsFlextTapLdapModels": ".models",
        "TestsFlextTapLdapProtocols": ".protocols",
        "TestsFlextTapLdapServiceBase": ".base",
        "TestsFlextTapLdapSettings": ".settings",
        "TestsFlextTapLdapTypes": ".typings",
        "TestsFlextTapLdapUtilities": ".utilities",
        "__author__": "flext_tap_ldap",
        "__author_email__": "flext_tap_ldap",
        "__description__": "flext_tap_ldap",
        "__license__": "flext_tap_ldap",
        "__title__": "flext_tap_ldap",
        "__url__": "flext_tap_ldap",
        "__version__": "flext_tap_ldap",
        "__version_info__": "flext_tap_ldap",
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
    },
    public_exports=__all__,
)
