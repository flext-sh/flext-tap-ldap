"""Base typings for _typings family."""

from __future__ import annotations

from flext_ldap import FlextLdapTypes
from flext_meltano import t as meltano_t

from flext_core import t as core_t


class FlextTapLdapTypesBase(core_t, meltano_t, FlextLdapTypes):
    """Base typings for _typings family."""


__all__: list[str] = ["FlextTapLdapTypesBase"]
