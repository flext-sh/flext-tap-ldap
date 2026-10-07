# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Tap Ldap.services package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import install_lazy_exports

if TYPE_CHECKING:
    from flext_tap_ldap.services.extract import FlextTapLdapExtractService


__all__: tuple[str, ...] = ("FlextTapLdapExtractService",)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({"FlextTapLdapExtractService": ".extract"}),
    public_exports=__all__,
)
