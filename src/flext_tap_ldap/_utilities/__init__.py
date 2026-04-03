# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Utilities package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING as _TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if _TYPE_CHECKING:
    from flext_core import FlextTypes
    from flext_tap_ldap._utilities import _processor
    from flext_tap_ldap._utilities._processor import (
        FlextTapLdapUtilitiesProcessorMixin,
        logger,
    )

_LAZY_IMPORTS: FlextTypes.LazyImportIndex = {
    "FlextTapLdapUtilitiesProcessorMixin": "flext_tap_ldap._utilities._processor",
    "_processor": "flext_tap_ldap._utilities._processor",
    "logger": "flext_tap_ldap._utilities._processor",
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
