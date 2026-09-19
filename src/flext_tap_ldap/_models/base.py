"""Base models for flext-tap-ldap private family."""

from __future__ import annotations

from flext_meltano import m as meltano_m


class FlextTapLdapModelsBase(meltano_m):
    """Base models for _models family."""


__all__: list[str] = ["FlextTapLdapModelsBase"]
