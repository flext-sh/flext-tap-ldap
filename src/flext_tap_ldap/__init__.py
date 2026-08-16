# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Tap Ldap package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from types import MappingProxyType

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

from .__version__ import __author__ as __author__
from .__version__ import __author_email__ as __author_email__
from .__version__ import __description__ as __description__
from .__version__ import __license__ as __license__
from .__version__ import __title__ as __title__
from .__version__ import __url__ as __url__
from .__version__ import __version__ as __version__
from .__version__ import __version_info__ as __version_info__

if TYPE_CHECKING:
    from flext_ldap import d, e, h, r, x

    from ._config import FlextTapLdapConfig, config
    from ._settings import FlextTapLdapSettings, settings
    from .api import FlextTapLdapService, tap_ldap
    from .base import FlextTapLdapServiceBase, FlextTapLdapServiceBase as s
    from .cli import main
    from .constants import FlextTapLdapConstants, FlextTapLdapConstants as c
    from .models import FlextTapLdapModels, FlextTapLdapModels as m
    from .protocols import FlextTapLdapProtocols, FlextTapLdapProtocols as p
    from .typings import FlextTapLdapTypes, FlextTapLdapTypes as t
    from .utilities import FlextTapLdapUtilities, FlextTapLdapUtilities as u
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
    MappingProxyType(
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
                ".typings": ("FlextTapLdapTypes", "t"),
                ".utilities": ("FlextTapLdapUtilities", "u"),
                "flext_ldap": ("d", "e", "h", "r", "x"),
            }),
            alias_groups=MappingProxyType({}),
            sort_keys=False,
        )
    ),
    public_exports=__all__,
)
