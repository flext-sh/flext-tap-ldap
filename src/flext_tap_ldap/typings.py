"""FLEXT Tap LDAP Types — MRO composition of parent type namespaces.

All Singer protocol types are in ``t.Meltano.*``.
All LDAP domain types are in ``FlextLdapTypes.Ldap.*``.
This facade composes both via MRO — access as ``t.Meltano.*`` and ``t.Ldap.*``.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_ldap import FlextLdapTypes
from flext_meltano import t


class FlextTapLdapTypes(t, FlextLdapTypes):
    """MRO facade composing Meltano + LDAP type namespaces.

    Access: ``t.Meltano.*`` (Singer protocol), ``t.Ldap.*`` (LDAP domain),
    ``t.TapLdap.*`` (tap-specific adapters), and all core ``t.*`` types via MRO.
    """

    class TapLdap:
        """Tap-LDAP-specific type adapters (project slot namespace)."""

        pass


t = FlextTapLdapTypes
__all__: list[str] = ["FlextTapLdapTypes", "t"]
