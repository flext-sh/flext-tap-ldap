"""Service base for flext-tap-ldap — the ``s`` alias consumed by ``services/*``.

Composes the flext-meltano Singer tap runtime via MRO and injects the flext-ldap
directory facade as ``self.ldap`` so tap services perform LDAP work through the
library while importing only ``c, t, p, m, u`` plus this ``s``.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_ldap import ldap
from flext_meltano import s as meltano_service
from flext_tap_ldap import p, u


class FlextTapLdapServiceBase(meltano_service):
    """Tap-LDAP service base: meltano service runtime plus injected LDAP facade."""

    _ldap: p.Ldap.LdapClient = u.PrivateAttr(default_factory=lambda: ldap)

    @property
    def ldap(self) -> p.Ldap.LdapClient:
        """The shared flext-ldap directory facade for tap services."""
        return self._ldap


s = FlextTapLdapServiceBase

__all__: list[str] = ["FlextTapLdapServiceBase", "s"]
