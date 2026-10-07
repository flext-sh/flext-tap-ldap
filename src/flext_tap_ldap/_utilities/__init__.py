# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Tap Ldap. Utilities package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import install_lazy_exports

if TYPE_CHECKING:
    from flext_tap_ldap._utilities.base import FlextTapLdapUtilitiesBase
    from flext_tap_ldap._utilities.extract_support import (
        FlextTapLdapUtilitiesExtractSupport,
    )


__all__: tuple[str, ...] = (
    "FlextTapLdapUtilitiesBase",
    "FlextTapLdapUtilitiesExtractSupport",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "FlextTapLdapUtilitiesBase": ".base",
        "FlextTapLdapUtilitiesExtractSupport": ".extract_support",
    }),
    public_exports=__all__,
)
