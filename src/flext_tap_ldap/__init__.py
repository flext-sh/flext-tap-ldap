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

    from ._settings import FlextTapLdapSettings, settings
    from .api import FlextTapLdapService, tap_ldap
    from .constants import FlextTapLdapConstants, FlextTapLdapConstants as c
    from .models import FlextTapLdapModels, FlextTapLdapModels as m
    from .protocols import FlextTapLdapProtocols, FlextTapLdapProtocols as p
    from .tap import FlextTapLdapTap
    from .typings import FlextTapLdapTypes, FlextTapLdapTypes as t
    from .utilities import FlextTapLdapUtilities, FlextTapLdapUtilities as u

    _ = (
        c,
        FlextTapLdapConstants,
        t,
        FlextTapLdapTypes,
        p,
        FlextTapLdapProtocols,
        m,
        FlextTapLdapModels,
        u,
        FlextTapLdapUtilities,
        d,
        e,
        h,
        r,
        s,
        x,
        FlextTapLdapSettings,
        settings,
        FlextTapLdapService,
        tap_ldap,
        FlextTapLdapTap,
    )


_LAZY_MODULES: dict[str, tuple[str, ...]] = {
    "._settings": (
        "FlextTapLdapSettings",
        "settings",
    ),
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
}


_LAZY_ALIAS_GROUPS: dict[str, tuple[tuple[str, str], ...]] = {}


_LAZY_IMPORTS = build_lazy_import_map(
    _LAZY_MODULES,
    alias_groups=_LAZY_ALIAS_GROUPS,
    sort_keys=False,
)

_DIRECT_IMPORTS: tuple[str, ...] = (
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
    "build_lazy_import_map",
    "c",
    "d",
    "e",
    "h",
    "install_lazy_exports",
    "m",
    "p",
    "r",
    "s",
    "settings",
    "t",
    "tap_ldap",
    "u",
    "x",
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
    "settings",
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
