"""Base protocols for flext-tap-ldap private family."""

from __future__ import annotations

from flext_meltano import p as meltano_p

from flext_core import p as core_p


class FlextTapLdapProtocolsBase(core_p, meltano_p):
    """Base protocols for _protocols family."""


__all__: list[str] = ["FlextTapLdapProtocolsBase"]
