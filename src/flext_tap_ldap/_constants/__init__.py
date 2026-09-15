"""LDAP tap constants - public facade."""

from __future__ import annotations

from .api import FlextTapLdapConstantsApi
from .base import FlextTapLdapConstantsBase
from .config import FlextTapLdapConstantsConfig


class FlextTapLdapConstants(
    FlextTapLdapConstantsConfig, FlextTapLdapConstantsApi, FlextTapLdapConstantsBase
):
    """Complete LDAP tap constants facade."""


c = FlextTapLdapConstants
__all__: list[str] = ["FlextTapLdapConstants", "c"]
