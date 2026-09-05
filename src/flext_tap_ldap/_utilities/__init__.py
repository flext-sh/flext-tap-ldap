# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Tap Ldap. Utilities package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from types import MappingProxyType

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from .extract_support import FlextTapLdapUtilitiesExtractSupport
__all__: tuple[str, ...] = ("FlextTapLdapUtilitiesExtractSupport",)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            ".extract_support": ("FlextTapLdapUtilitiesExtractSupport",)
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)
