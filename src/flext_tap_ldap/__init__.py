# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Tap Ldap package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import install_lazy_exports
from flext_tap_ldap.__version__ import (
    __author__,
    __author_email__,
    __description__,
    __license__,
    __title__,
    __url__,
    __version__,
    __version_info__,
)

if TYPE_CHECKING:
    from flext_meltano import d, e, h, r, x

    from flext_tap_ldap import services
    from flext_tap_ldap._config import FlextTapLdapConfig, config
    from flext_tap_ldap._settings import FlextTapLdapSettings, settings
    from flext_tap_ldap.api import FlextTapLdapService, tap_ldap
    from flext_tap_ldap.base import FlextTapLdapServiceBase, s
    from flext_tap_ldap.cli import main
    from flext_tap_ldap.constants import FlextTapLdapConstants, c
    from flext_tap_ldap.models import FlextTapLdapModels, m
    from flext_tap_ldap.protocols import FlextTapLdapProtocols, p
    from flext_tap_ldap.services.extract import FlextTapLdapExtractService
    from flext_tap_ldap.typings import FlextTapLdapTypes, t
    from flext_tap_ldap.utilities import FlextTapLdapUtilities, u


__all__: tuple[str, ...] = (
    "FlextTapLdapConfig",
    "FlextTapLdapConstants",
    "FlextTapLdapExtractService",
    "FlextTapLdapModels",
    "FlextTapLdapProtocols",
    "FlextTapLdapService",
    "FlextTapLdapServiceBase",
    "FlextTapLdapSettings",
    "FlextTapLdapTypes",
    "FlextTapLdapUtilities",
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
    "services",
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
        "FlextTapLdapExtractService": ".services.extract",
        "FlextTapLdapModels": ".models",
        "FlextTapLdapProtocols": ".protocols",
        "FlextTapLdapService": ".api",
        "FlextTapLdapServiceBase": ".base",
        "FlextTapLdapSettings": "._settings",
        "FlextTapLdapTypes": ".typings",
        "FlextTapLdapUtilities": ".utilities",
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
        "services": ".services",
        "settings": "._settings",
        "t": ".typings",
        "tap_ldap": ".api",
        "u": ".utilities",
        "x": "flext_meltano",
    }),
    public_exports=__all__,
)
