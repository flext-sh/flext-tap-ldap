"""Re-export shim — canonical implementation lives in _utilities.tap."""

from __future__ import annotations

from flext_tap_ldap._utilities.tap import CLI_COMMAND, FlextTapLdapTap, logger, main

__all__ = ["CLI_COMMAND", "FlextTapLdapTap", "logger", "main"]
