# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Tap LDAP utilities subpackage."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_tap_ldap._utilities._processor import *

_LAZY_IMPORTS: Mapping[str, str | Sequence[str]] = {
    "FlextTapLdapUtilitiesProcessorMixin": "flext_tap_ldap._utilities._processor",
    "_processor": "flext_tap_ldap._utilities._processor",
    "logger": "flext_tap_ldap._utilities._processor",
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
