# AUTO-GENERATED FILE — Regenerate with: make gen
"""LDAP tap typings - public facade.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_ldap import FlextLdapTypes
from flext_meltano import FlextMeltanoTypes

from flext_tap_ldap._typings import FlextTapLdapTypesBase


class FlextTapLdapTypes(FlextMeltanoTypes, FlextLdapTypes):
    """MRO facade composing Meltano + LDAP type namespaces.

    Access: ``t.Meltano.*`` (Singer protocol), ``t.Ldap.*`` (LDAP domain),
    ``t.TapLdap.*`` (tap-specific adapters), and all core ``t.*`` types via MRO.
    """

    class TapLdap(FlextTapLdapTypesBase):
        """Tap-LDAP-specific type adapters (project slot namespace).

        Composes the ``_typings`` family base so the namespace reaches every
        class the family package declares.
        """


t = FlextTapLdapTypes
__all__: list[str] = ["FlextTapLdapTypes", "t"]
