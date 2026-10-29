# AUTO-GENERATED FILE — Regenerate with: make gen
"""FLEXT Tap LDAP models - tap-specific namespace only.

Connection and search shapes come from the parent libraries (``m.Ldap.*`` from
flext-ldap, ``m.Meltano.*`` from flext-meltano); the tap declares no copies.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_ldap import m as flext_ldap_m
from flext_meltano import m as flext_meltano_m

from flext_tap_ldap._models import FlextModelsTapLdapBase, FlextModelsTapLdapConfig


class FlextModelsTapLdap(flext_meltano_m, flext_ldap_m):
    """Models facade for the LDAP tap composed from flext-meltano and flext-ldap."""

    class TapLdap(FlextModelsTapLdapBase, FlextModelsTapLdapConfig):
        """Tap LDAP namespace for cross-project access."""


# Runtime alias for simplified usage
m = FlextModelsTapLdap
__all__: list[str] = ["FlextModelsTapLdap", "m"]
