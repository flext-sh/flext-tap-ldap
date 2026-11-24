# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Tap Ldap. Protocols package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_tap_ldap._protocols.base import FlextTapLdapProtocolsBase
    from flext_tap_ldap._protocols.config import FlextTapLdapProtocolsConfig


__all__: tuple[str, ...] = ("FlextTapLdapProtocolsBase", "FlextTapLdapProtocolsConfig")

install_lazy_exports(
    __name__,
    globals(),
    {"FlextTapLdapProtocolsBase": ".base", "FlextTapLdapProtocolsConfig": ".config"},
    public_exports=__all__,
    deferred_members=(
        "FlextTapLdapProtocolsBase",
        "FlextTapLdapProtocolsConfig",
    ),
)
