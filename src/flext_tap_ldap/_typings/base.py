"""Base typings for _typings family."""

from __future__ import annotations

from flext_ldap import t
from flext_meltano import t as meltano_t


class FlextTapLdapTypesBase(meltano_t, t):
    """Base typings for _typings family."""


__all__: list[str] = ["FlextTapLdapTypesBase"]
