"""FLEXT Tap LDAP Constants - LDAP tap extraction constants.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import ClassVar

from flext_ldap.constants import FlextLdapConstants

from flext_core import FlextConstants


class FlextTapLdapConstants(FlextConstants):
    """LDAP tap extraction-specific constants following FLEXT unified pattern with nested domains.

    Composes with FlextLdapConstants to avoid duplication and ensure consistency.
    """

    # LDAP-specific constants composed from flext-ldap (composition pattern)

    class Connection:
        """LDAP connection configuration constants."""

        class Ldap:
            """Standard LDAP connection settings."""

            DEFAULT_HOST = (
                FlextLdapConstants.Protocol.DEFAULT_HOST
                if hasattr(FlextLdapConstants.Protocol, "DEFAULT_HOST")
                else FlextConstants.Platform.DEFAULT_HOST
            )
            DEFAULT_PORT = FlextLdapConstants.Protocol.DEFAULT_PORT
            DEFAULT_TIMEOUT = FlextLdapConstants.Protocol.DEFAULT_TIMEOUT_SECONDS

        class Ldaps:
            """Secure LDAP connection settings."""

            DEFAULT_PORT = FlextLdapConstants.Protocol.DEFAULT_SSL_PORT

    class Processing:
        """Singer tap data processing configuration."""

        DEFAULT_PAGE_SIZE = FlextLdapConstants.Connection.DEFAULT_PAGE_SIZE
        DEFAULT_BATCH_SIZE = FlextConstants.Performance.BatchProcessing.DEFAULT_SIZE
        MAX_BATCH_SIZE = FlextConstants.Performance.BatchProcessing.MAX_ITEMS

    class Search:
        """LDAP search operation configuration."""

        DEFAULT_SCOPE = FlextLdapConstants.Scopes.SUBTREE
        SCOPES: ClassVar[list[str]] = list(FlextLdapConstants.Scopes.VALID_SCOPES)

    class Extraction:
        """Singer tap specific extraction constants."""

        DEFAULT_STREAM_PAGE_SIZE = FlextLdapConstants.Connection.DEFAULT_PAGE_SIZE
        MAX_STREAM_RECORDS = FlextLdapConstants.LdapDefaults.MAX_SEARCH_ENTRIES
        DEFAULT_STREAM_TIMEOUT = FlextLdapConstants.DEFAULT_TIMEOUT

    class Retry:
        """Tap-specific retry configuration."""

        CONNECTION_RETRY_DELAY = FlextLdapConstants.LdapRetry.CONNECTION_RETRY_DELAY
        CONNECTION_MAX_RETRIES = FlextLdapConstants.LdapRetry.CONNECTION_MAX_RETRIES


__all__ = ["FlextTapLdapConstants"]
