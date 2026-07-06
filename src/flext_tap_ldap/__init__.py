# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Tap Ldap package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports
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
    from flext_ldap import d, e, h, r, s, x
    from flext_tap_ldap.api import FlextTapLdapService, tap_ldap
    from flext_tap_ldap.constants import FlextTapLdapConstants, c
    from flext_tap_ldap.models import FlextTapLdapModels, m
    from flext_tap_ldap.protocols import FlextTapLdapProtocols, p
    from flext_tap_ldap.settings import FlextTapLdapSettings
    from flext_tap_ldap.tap import FlextTapLdapTap
    from flext_tap_ldap.typings import FlextTapLdapTypes, t
    from flext_tap_ldap.utilities import FlextTapLdapUtilities, u
_LAZY_IMPORTS = build_lazy_import_map(
    {
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
        "flext_ldap": (
            "d",
            "e",
            "h",
            "r",
            "s",
            "x",
        ),
    },
)


__all__: tuple[str, ...] = (
    "FlextTapLdapConstants",
    "FlextTapLdapModels",
    "FlextTapLdapProtocols",
    "FlextTapLdapService",
    "FlextTapLdapSettings",
    "FlextTapLdapTap",
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
    "d",
    "e",
    "h",
    "m",
    "p",
    "r",
    "s",
    "t",
    "tap_ldap",
    "u",
    "x",
)


install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    public_exports=__all__,
)
