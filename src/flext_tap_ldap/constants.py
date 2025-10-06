"""FLEXT Tap LDAP Constants - LDAP tap extraction constants.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import ClassVar

from flext_core import FlextConstants, FlextTypes
from flext_ldap.constants import FlextLDAPConstants


class FlextTapLdapConstants(FlextConstants):
    """LDAP tap extraction-specific constants following FLEXT unified pattern with nested domains.

    Composes with FlextLDAPConstants to avoid duplication and ensure consistency.
    """

    # LDAP-specific constants composed from flext-ldap (composition pattern)

    class Connection:
        """LDAP connection configuration constants."""

        class Ldap:
            """Standard LDAP connection settings."""

            DEFAULT_HOST = (
                FlextLDAPConstants.Protocol.DEFAULT_HOST
                if hasattr(FlextLDAPConstants.Protocol, "DEFAULT_HOST")
                else FlextConstants.Platform.DEFAULT_HOST
            )
            DEFAULT_PORT = FlextLDAPConstants.Protocol.DEFAULT_PORT
            DEFAULT_TIMEOUT = FlextLDAPConstants.Protocol.DEFAULT_TIMEOUT_SECONDS

        class Ldaps:
            """Secure LDAP connection settings."""

            DEFAULT_PORT = FlextLDAPConstants.Protocol.DEFAULT_SSL_PORT

    class Processing:
        """Singer tap data processing configuration."""

        DEFAULT_PAGE_SIZE = FlextLDAPConstants.Connection.DEFAULT_PAGE_SIZE
        DEFAULT_BATCH_SIZE = FlextConstants.Performance.BatchProcessing.DEFAULT_SIZE
        MAX_BATCH_SIZE = FlextConstants.Performance.BatchProcessing.MAX_ITEMS

    class Search:
        """LDAP search operation configuration."""

        DEFAULT_SCOPE = FlextLDAPConstants.Scopes.SUBTREE
        SCOPES: ClassVar[FlextTypes.StringList] = list(
            FlextLDAPConstants.Scopes.VALID_SCOPES
        )

    class Extraction:
        """Singer tap specific extraction constants."""

        DEFAULT_STREAM_PAGE_SIZE = FlextLDAPConstants.Connection.DEFAULT_PAGE_SIZE
        MAX_STREAM_RECORDS = FlextLDAPConstants.LdapDefaults.MAX_SEARCH_ENTRIES
        DEFAULT_STREAM_TIMEOUT = FlextLDAPConstants.DEFAULT_TIMEOUT

    class Retry:
        """Tap-specific retry configuration."""

        CONNECTION_RETRY_DELAY = FlextLDAPConstants.LdapRetry.CONNECTION_RETRY_DELAY
        CONNECTION_MAX_RETRIES = FlextLDAPConstants.LdapRetry.CONNECTION_MAX_RETRIES


__all__ = ["FlextTapLdapConstants"]
