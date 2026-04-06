# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Utilities package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import install_lazy_exports

if _t.TYPE_CHECKING:
    import flext_tap_ldap._utilities._processor as _flext_tap_ldap__utilities__processor

    _processor = _flext_tap_ldap__utilities__processor
    from flext_tap_ldap._utilities._processor import (
        FlextTapLdapUtilitiesProcessorMixin,
        logger,
    )
_LAZY_IMPORTS = {
    "FlextTapLdapUtilitiesProcessorMixin": (
        "flext_tap_ldap._utilities._processor",
        "FlextTapLdapUtilitiesProcessorMixin",
    ),
    "_processor": "flext_tap_ldap._utilities._processor",
    "logger": ("flext_tap_ldap._utilities._processor", "logger"),
}

__all__ = [
    "FlextTapLdapUtilitiesProcessorMixin",
    "_processor",
    "logger",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
