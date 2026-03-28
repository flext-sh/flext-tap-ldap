"""Re-export shim — canonical implementation lives in _utilities.client."""

from __future__ import annotations

from flext_tap_ldap._utilities.client import FlextTapLdapClient

__all__ = ["FlextTapLdapClient"]
