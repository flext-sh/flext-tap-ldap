# @generated AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Tap Ldap package."""

from __future__ import annotations

from typing import TYPE_CHECKING

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
    from flext_ldap import d as d
    from flext_ldap import e as e
    from flext_ldap import h as h
    from flext_ldap import r as r
    from flext_ldap import x as x

    from ._config import FlextTapLdapConfig as FlextTapLdapConfig
    from ._config import config as config
    from ._settings import FlextTapLdapSettings as FlextTapLdapSettings
    from ._settings import settings as settings
    from .api import FlextTapLdapService as FlextTapLdapService
    from .api import tap_ldap as tap_ldap
    from .base import FlextTapLdapServiceBase as FlextTapLdapServiceBase

    s: type[FlextTapLdapServiceBase]
    from .cli import main as main
    from .constants import FlextTapLdapConstants as FlextTapLdapConstants

    c: type[FlextTapLdapConstants]
    from .models import FlextTapLdapModels as FlextTapLdapModels

    m: type[FlextTapLdapModels]
    from .protocols import FlextTapLdapProtocols as FlextTapLdapProtocols

    p: type[FlextTapLdapProtocols]
    from .typings import FlextTapLdapTypes as FlextTapLdapTypes

    t: type[FlextTapLdapTypes]
    from .utilities import FlextTapLdapUtilities as FlextTapLdapUtilities

    u: type[FlextTapLdapUtilities]

_LAZY_MODULES: dict[str, tuple[str, ...]] = {
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
}


_LAZY_ALIAS_GROUPS: dict[str, tuple[tuple[str, str], ...]] = {}


_LAZY_IMPORTS = build_lazy_import_map(
    _LAZY_MODULES, alias_groups=_LAZY_ALIAS_GROUPS, sort_keys=False
)

_PUBLIC_EXPORTS: tuple[str, ...] = (
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

__all__: tuple[str, ...] = tuple(_PUBLIC_EXPORTS)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
