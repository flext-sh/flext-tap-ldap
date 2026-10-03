"""FLEXT Tap LDAP models - tap-specific namespace only.

Connection and search shapes come from the parent libraries (``m.Ldap.*`` from
flext-ldap, ``m.Meltano.*`` from flext-meltano); the tap declares no copies.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_ldap import FlextLdapModels
from flext_meltano import FlextMeltanoModels


class FlextTapLdapModels(FlextMeltanoModels, FlextLdapModels):
    """Models facade for the LDAP tap composed from flext-meltano and flext-ldap."""

    class TapLdap:
        """Tap LDAP namespace for cross-project access."""


# Runtime alias for simplified usage
m = FlextTapLdapModels

__all__: list[str] = ["FlextTapLdapModels", "m"]
