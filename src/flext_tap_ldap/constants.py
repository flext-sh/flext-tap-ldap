"""FLEXT Tap LDAP Constants - LDAP tap extraction constants.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from enum import StrEnum
from typing import Final, Literal

from flext_ldap import FlextLdapConstants
from flext_meltano import FlextMeltanoConstants

# LDAP port constants (moved outside class for accessibility)
DEFAULT_LDAP_PORT: Final[int] = 389
DEFAULT_LDAPS_PORT: Final[int] = 636


class FlextMeltanoTapLdapConstants(FlextMeltanoConstants, FlextLdapConstants):
    """LDAP tap extraction-specific constants following FLEXT unified pattern.

    Inherits from FlextMeltanoConstants for universal constants, defines only
    LDAP tap-specific constants using nested namespace classes.

    Composes with FlextLdapConstants to avoid duplication and ensure consistency.
    """

    class TapLdap:
        """Tap LDAP namespace for cross-project access."""

        # Constants
        DEFAULT_PAGE_SIZE = 1000
        MAX_LDAP_FILTER_LENGTH = 2048
        DEFAULT_SEARCH_TIMEOUT = 30

        class Ldap:
            """LDAP connection constants."""

            # Use FlextLdapConstants for LDAP-specific configuration
            DEFAULT_PORT: Final[int] = FlextLdapConstants.Ldap.ConnectionDefaults.PORT
            DEFAULT_SSL_PORT: Final[int] = 636  # CONFIG: Standard LDAPS port

            # LDAP-specific search configuration
            DEFAULT_PAGE_SIZE: Final[int] = 1000
            MAX_FILTER_LENGTH: Final[int] = 2048
            DEFAULT_TIMEOUT: Final[int] = (
                FlextLdapConstants.Ldap.ConnectionDefaults.TIMEOUT
            )
            MAX_PORT: Final[int] = 65535

        class Singer:
            """Singer tap configuration constants."""

            # Use FlextMeltanoConstants for performance settings
            DEFAULT_BATCH_SIZE: Final[int] = (
                FlextMeltanoConstants.Performance.BatchProcessing.DEFAULT_SIZE
            )
            MAX_BATCH_SIZE: Final[int] = (
                FlextMeltanoConstants.Performance.BatchProcessing.MAX_ITEMS
            )

        class Replication:
            """LDAP replication method constants."""

            class Method(StrEnum):
                """LDAP replication methods using StrEnum for type safety.

                DRY Pattern:
                    StrEnum is the single source of truth. Use Method.FULL_TABLE.value
                    or Method.FULL_TABLE directly - no string duplication needed.
                """

                FULL_TABLE = "FULL_TABLE"
                INCREMENTAL = "INCREMENTAL"

            DEFAULT_METHOD: Final[str] = Method.INCREMENTAL

        class TapValidation:
            """LDAP tap validation constants.

            Note: Does not override parent Validation class to avoid inheritance conflicts.
            """

            # Use FlextMeltanoConstants for validation limits
            MIN_BATCH_SIZE: Final[int] = 1  # Minimum batch size is 1 record
            MAX_TIMEOUT: Final[int] = (
                FlextMeltanoConstants.Performance.MAX_TIMEOUT_SECONDS
            )

            # LDAP-specific validation limits
            MAX_DN_LENGTH: Final[int] = 1024  # Maximum DN length
            MAX_ATTRIBUTE_NAME_LENGTH: Final[int] = 255  # Maximum attribute name length
            MAX_BASE_DN_LENGTH: Final[int] = 512  # Maximum base DN length

            # Stream and filter validation limits
            MAX_STREAM_PREFIX_LENGTH: Final[int] = 50  # Max stream prefix length
            MAX_FILTER_COUNT: Final[int] = 100  # Max number of filters
            MAX_ATTRIBUTE_COUNT: Final[int] = 500  # Max attributes per entry

        class Connection:
            """LDAP tap connection configuration."""

            DEFAULT_HOST: Final[str] = "localhost"
            DEFAULT_PORT: Final[int] = DEFAULT_LDAP_PORT
            DEFAULT_SSL_PORT: Final[int] = DEFAULT_LDAPS_PORT
            DEFAULT_BASE_DN: Final[str] = ""
            DEFAULT_BIND_DN: Final[str] = ""
            DEFAULT_BIND_PASSWORD: Final[str] = ""

        class Search:
            """LDAP search configuration."""

            DEFAULT_SCOPE: Final[str] = "SUBTREE"
            DEFAULT_DEREF: Final[str] = "ALWAYS"
            DEFAULT_SIZE_LIMIT: Final[int] = 0  # No limit
            DEFAULT_TIME_LIMIT: Final[int] = 0  # No limit

        # Type-safe literals - PEP 695 syntax for type checking
        # All Literal types reference StrEnum members where available - NO string duplication!
        type ReplicationMethodLiteral = Literal[
            Replication.Method.FULL_TABLE,
            Replication.Method.INCREMENTAL,
        ]
        """LDAP replication method literal - references Replication.Method StrEnum members."""

        # Tap-specific type definitions
        TapReplicationMethod = Literal["FULL_TABLE", "INCREMENTAL"]
        TapSearchScope = Literal["BASE", "ONELEVEL", "SUBTREE"]
        TapConnectionMode = Literal["anonymous", "simple", "sasl"]
        TapExecutionMode = Literal["discovery", "extraction", "test", "validate"]


c = FlextMeltanoTapLdapConstants

__all__ = ["FlextMeltanoTapLdapConstants", "c"]
