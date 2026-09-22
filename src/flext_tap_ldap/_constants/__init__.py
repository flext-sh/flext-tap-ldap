# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Tap Ldap. Constants package."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from .api import FlextTapLdapConstantsApi
    from .base import FlextTapLdapConstantsBase
    from .config import FlextTapLdapConstantsConfig
__all__: tuple[str, ...] = (
    "FlextTapLdapConstantsApi",
    "FlextTapLdapConstantsBase",
    "FlextTapLdapConstantsConfig",
)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            ".api": ("FlextTapLdapConstantsApi",),
            ".base": ("FlextTapLdapConstantsBase",),
            ".config": ("FlextTapLdapConstantsConfig",),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
