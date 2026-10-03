"""LDAP tap typings - public facade.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tap_ldap._typings.base import FlextTapLdapTypesBase


class FlextTapLdapTypes(FlextTapLdapTypesBase):
    """MRO facade composing Meltano + LDAP type namespaces.

    Access: ``t.Meltano.*`` (Singer protocol), ``t.Ldap.*`` (LDAP domain),
    ``t.TapLdap.*`` (tap-specific adapters), and all core ``t.*`` types via MRO.
    """

    class TapLdap:
        """Tap-LDAP-specific type adapters (project slot namespace)."""


t = FlextTapLdapTypes
__all__: list[str] = ["FlextTapLdapTypes", "t"]
