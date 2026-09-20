"""Base utilities for flext-tap-ldap private family."""

from __future__ import annotations

from flext_meltano import u as meltano_u


class FlextTapLdapUtilitiesBase(meltano_u):
    """Base utilities for _utilities family."""


__all__: list[str] = ["FlextTapLdapUtilitiesBase"]
