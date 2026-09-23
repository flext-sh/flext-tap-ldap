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
    from flext_ldap import (
        adapters,
        cli,
        core,
        d,
        e,
        h,
        lazy_attribute,
        ldap,
        ldif,
        r,
        servers,
        x,
    )
    from flext_meltano import meltano

    from . import services
    from ._config import FlextTapLdapConfig, config
    from ._settings import FlextTapLdapSettings, settings
    from .api import FlextTapLdapService, tap_ldap
    from .base import FlextTapLdapServiceBase, FlextTapLdapServiceBase as s
    from .cli import main
    from .constants import FlextTapLdapConstants, c
    from .models import FlextTapLdapModels, m
    from .protocols import FlextTapLdapProtocols, p
    from .services.extract import FlextTapLdapExtractService
    from .typings import FlextTapLdapTypes, FlextTapLdapTypes as t
    from .utilities import FlextTapLdapUtilities, u


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
    "adapters",
    "c",
    "cli",
    "config",
    "core",
    "d",
    "e",
    "h",
    "lazy_attribute",
    "ldap",
    "ldif",
    "m",
    "main",
    "meltano",
    "p",
    "r",
    "s",
    "servers",
    "services",
    "settings",
    "t",
    "tap_ldap",
    "u",
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
            "flext_ldap": (
                "adapters",
                "cli",
                "core",
                "d",
                "e",
                "h",
                "lazy_attribute",
                "ldap",
                "ldif",
                "r",
                "servers",
                "x",
            ),
            "flext_meltano": ("meltano",),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
