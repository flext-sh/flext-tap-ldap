"""Re-export shim — canonical implementation lives in _utilities.ldif_streams."""

from __future__ import annotations

from flext_tap_ldap._utilities.ldif_streams import FlextTapLdapLdifStreams

__all__ = ["FlextTapLdapLdifStreams"]
