"""Tap LDAP utility facade."""

from __future__ import annotations

from flext_ldap import FlextLdapUtilities
from flext_meltano import u
from flext_tap_ldap._utilities._processor import FlextTapLdapUtilitiesProcessorMixin
from flext_tap_ldap._utilities.client_support import (
    FlextTapLdapUtilitiesClientSupport,
)
from flext_tap_ldap._utilities.error_handling import (
    FlextTapLdapUtilitiesErrorHandling,
)


class FlextTapLdapUtilities(
    FlextTapLdapUtilitiesProcessorMixin,
    u,
    FlextLdapUtilities,
):
    """Unified LDAP tap utility facade."""

    class TapLdap(
        FlextTapLdapUtilitiesProcessorMixin.TapLdap,
        FlextTapLdapUtilitiesClientSupport,
        FlextTapLdapUtilitiesErrorHandling,
    ):
        """Tap LDAP namespace for cross-project access."""


u = FlextTapLdapUtilities

__all__: list[str] = ["FlextTapLdapUtilities", "u"]
