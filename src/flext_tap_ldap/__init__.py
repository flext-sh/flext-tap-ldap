# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Tap Ldap package."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

from .__version__ import (
    __author__ as __author__,
    __author_email__ as __author_email__,
    __description__ as __description__,
    __license__ as __license__,
    __title__ as __title__,
    __url__ as __url__,
    __version__ as __version__,
    __version_info__ as __version_info__,
)

if TYPE_CHECKING:
    from enum import StrEnum, unique
    from typing import TYPE_CHECKING, Final

    from flext_ldap import FlextLdapConstants, d, e, h, r, x

    from . import services as services
    from ._config import FlextTapLdapConfig, config
    from ._settings import FlextTapLdapSettings, settings
    from .api import FlextTapLdapService, tap_ldap
    from .base import FlextTapLdapServiceBase, FlextTapLdapServiceBase as s
    from .cli import main
    from .constants import FlextTapLdapConstants, FlextTapLdapConstants as c
    from .models import FlextTapLdapModels, FlextTapLdapModels as m
    from .protocols import FlextTapLdapProtocols, FlextTapLdapProtocols as p
    from .services.extract import FlextTapLdapExtractService
    from .typings import FlextTapLdapTypes, FlextTapLdapTypes as t
    from .utilities import FlextTapLdapUtilities, FlextTapLdapUtilities as u
__all__: tuple[str, ...] = (
    "TYPE_CHECKING",
    "Final",
    "FlextLdapConstants",
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
    "StrEnum",
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
    "unique",
    "x",
)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            "._config": ("FlextTapLdapConfig", "config"),
            "._settings": ("FlextTapLdapSettings", "settings"),
            ".api": ("FlextTapLdapService", "tap_ldap"),
            ".base": ("FlextTapLdapServiceBase", "s"),
            ".cli": ("main",),
            ".constants": ("FlextTapLdapConstants", "c"),
            ".models": ("FlextTapLdapModels", "m"),
            ".protocols": ("FlextTapLdapProtocols", "p"),
            ".services": ("services",),
            ".services.extract": ("FlextTapLdapExtractService",),
            ".typings": ("FlextTapLdapTypes", "t"),
            ".utilities": ("FlextTapLdapUtilities", "u"),
            "enum": ("StrEnum", "unique"),
            "flext_ldap": ("FlextLdapConstants", "d", "e", "h", "r", "x"),
            "typing": ("Final", "TYPE_CHECKING"),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
