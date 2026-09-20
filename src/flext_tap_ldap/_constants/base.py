"""Base constants for flext-tap-ldap private family."""

from __future__ import annotations

from flext_meltano import c as meltano_c


class FlextTapLdapConstantsBase(meltano_c):
    """Base constants for _constants family."""


__all__: list[str] = ["FlextTapLdapConstantsBase"]
