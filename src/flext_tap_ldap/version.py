"""Version information for flext-tap-ldap."""

from __future__ import annotations

from typing import NamedTuple


class FlextMeltanoTapLdapVersion(NamedTuple):
    """Version information for flext-tap-ldap."""

    version: str
    version_info: tuple[int | str, ...]


VERSION: FlextMeltanoTapLdapVersion = FlextMeltanoTapLdapVersion(
    version="0.9.0",
    version_info=(0, 9, 0),
)

__all__ = [
    "VERSION",
    "FlextMeltanoTapLdapVersion",
]
