"""Base typings for _typings family."""

from __future__ import annotations

from flext_ldap import FlextLdapTypes
from flext_meltano import t as meltano_t


class FlextTapLdapTypesBase(meltano_t, FlextLdapTypes):
    """Base typings for _typings family."""


__all__: list[str] = ["FlextTapLdapTypesBase"]
