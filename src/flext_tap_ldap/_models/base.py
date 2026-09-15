"""Base models for flext-tap-ldap private family."""

from __future__ import annotations

from flext_meltano import m as meltano_m

from flext_core import m as core_m


class FlextTapLdapModelsBase(core_m, meltano_m):
    """Base models for _models family."""


__all__: list[str] = ["FlextTapLdapModelsBase"]
