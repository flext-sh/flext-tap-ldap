"""FLEXT Tap LDAP Constants - LDAP tap extraction constants.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import ClassVar

from flext_core import FlextConstants


class FlextTapLdapConstants(FlextConstants):
    """LDAP tap extraction-specific constants following FLEXT unified pattern with nested domains."""

    class Connection:
        """LDAP connection configuration constants."""

        class Ldap:
            """Standard LDAP connection settings."""

            DEFAULT_HOST = FlextConstants.Platform.DEFAULT_HOST
            DEFAULT_PORT = FlextConstants.Platform.LDAP_DEFAULT_PORT
            DEFAULT_TIMEOUT = FlextConstants.Network.DEFAULT_TIMEOUT

        class Ldaps:
            """Secure LDAP connection settings."""

            DEFAULT_PORT = FlextConstants.Platform.LDAPS_DEFAULT_PORT

    class Processing:
        """Singer tap data processing configuration."""

        DEFAULT_PAGE_SIZE = FlextConstants.Performance.BatchProcessing.DEFAULT_SIZE
        DEFAULT_BATCH_SIZE = FlextConstants.Performance.BatchProcessing.DEFAULT_SIZE
        MAX_BATCH_SIZE = FlextConstants.Performance.BatchProcessing.MAX_ITEMS

    class Search:
        """LDAP search operation configuration."""

        DEFAULT_SCOPE = "SUBTREE"
        SCOPES: ClassVar[list[str]] = ["BASE", "ONELEVEL", "SUBTREE"]


__all__ = ["FlextTapLdapConstants"]
