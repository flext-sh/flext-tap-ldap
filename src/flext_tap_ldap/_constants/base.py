"""Base constants for flext-tap-ldap private family."""

from __future__ import annotations

from flext_meltano import c as meltano_c

from flext_core import c as core_c


class FlextTapLdapConstantsBase(core_c, meltano_c):
    """Base constants for _constants family."""


__all__: list[str] = ["FlextTapLdapConstantsBase"]
