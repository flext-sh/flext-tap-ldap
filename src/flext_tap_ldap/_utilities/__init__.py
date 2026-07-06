# AUTO-GENERATED FILE — Regenerate with: make gen
"""Utilities package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_tap_ldap._utilities._processor import FlextTapLdapUtilitiesProcessorMixin
    from flext_tap_ldap._utilities.client_support import (
        FlextTapLdapUtilitiesClientSupport,
    )
    from flext_tap_ldap._utilities.error_handling import (
        FlextTapLdapUtilitiesErrorHandling,
    )
_LAZY_IMPORTS = build_lazy_import_map(
    {
        "._processor": ("FlextTapLdapUtilitiesProcessorMixin",),
        ".client_support": ("FlextTapLdapUtilitiesClientSupport",),
        ".error_handling": ("FlextTapLdapUtilitiesErrorHandling",),
    },
)


install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    publish_all=False,
)
