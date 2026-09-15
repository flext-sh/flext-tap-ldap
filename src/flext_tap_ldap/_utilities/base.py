"""Base utilities for flext-tap-ldap private family."""

from __future__ import annotations

from flext_meltano import u as meltano_u

from flext_core import u as core_u


class FlextTapLdapUtilitiesBase(core_u, meltano_u):
    """Base utilities for _utilities family."""


__all__: list[str] = ["FlextTapLdapUtilitiesBase"]
