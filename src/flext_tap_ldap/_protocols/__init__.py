# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Tap Ldap. Protocols package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import install_lazy_exports

if TYPE_CHECKING:
    from flext_tap_ldap._protocols.base import FlextTapLdapProtocolsBase


__all__: tuple[str, ...] = ("FlextTapLdapProtocolsBase",)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({"FlextTapLdapProtocolsBase": ".base"}),
    public_exports=__all__,
)
