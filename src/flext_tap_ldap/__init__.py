# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Tap Ldap package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_meltano import d, e, h, r, x

    from flext_tap_ldap.__version__ import (
        FlextTapLdapVersion,
        __author__,
        __author_email__,
        __description__,
        __license__,
        __title__,
        __url__,
        __version__,
        __version_info__,
    )
    from flext_tap_ldap._config import FlextTapLdapConfig, config
    from flext_tap_ldap._settings import FlextTapLdapSettings, settings
    from flext_tap_ldap.api import FlextTapLdapService, tap_ldap
    from flext_tap_ldap.base import FlextTapLdapServiceBase, s
    from flext_tap_ldap.cli import main
    from flext_tap_ldap.constants import FlextTapLdapConstants, c
    from flext_tap_ldap.models import FlextTapLdapModels, m
    from flext_tap_ldap.protocols import FlextTapLdapProtocols, p
    from flext_tap_ldap.typings import FlextTapLdapTypes, t
    from flext_tap_ldap.utilities import FlextTapLdapUtilities, u


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
    "__author__",
    "__author_email__",
    "__description__",
    "__license__",
    "__title__",
    "__url__",
    "__version__",
    "__version_info__",
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
    "u",
    "x",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "FlextTapLdapConfig": "._config",
        "FlextTapLdapConstants": ".constants",
        "FlextTapLdapModels": ".models",
        "FlextTapLdapProtocols": ".protocols",
        "FlextTapLdapService": ".api",
        "FlextTapLdapServiceBase": ".base",
        "FlextTapLdapSettings": "._settings",
        "FlextTapLdapTypes": ".typings",
        "FlextTapLdapUtilities": ".utilities",
        "FlextTapLdapVersion": ".__version__",
        "__author__": ".__version__",
        "__author_email__": ".__version__",
        "__description__": ".__version__",
        "__license__": ".__version__",
        "__title__": ".__version__",
        "__url__": ".__version__",
        "__version_info__": ".__version__",
        "c": ".constants",
        "config": "._config",
        "d": "flext_meltano",
        "e": "flext_meltano",
        "h": "flext_meltano",
        "m": ".models",
        "main": ".cli",
        "p": ".protocols",
        "r": "flext_meltano",
        "s": ".base",
        "settings": "._settings",
        "t": ".typings",
        "tap_ldap": ".api",
        "u": ".utilities",
        "x": "flext_meltano",
    }),
    public_exports=__all__,
)

if not TYPE_CHECKING:
    from flext_tap_ldap.__version__ import __version__
