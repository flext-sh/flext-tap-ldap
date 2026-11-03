# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Tap Ldap. Models package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_tap_ldap._models.base import FlextTapLdapModelsBase
    from flext_tap_ldap._models.config import FlextTapLdapModelsConfig


__all__: tuple[str, ...] = ("FlextTapLdapModelsBase", "FlextTapLdapModelsConfig")

install_lazy_exports(
    __name__,
    globals(),
    {"FlextTapLdapModelsBase": ".base", "FlextTapLdapModelsConfig": ".config"},
    public_exports=__all__,
)
