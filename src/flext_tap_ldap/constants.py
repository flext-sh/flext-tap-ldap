"""FLEXT Tap LDAP Constants - LDAP tap extraction constants.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from enum import StrEnum
from typing import Final, Literal

from flext_ldap import FlextLdapConstants
from flext_meltano import FlextMeltanoConstants


class FlextTapLdapConstants(FlextMeltanoConstants, FlextLdapConstants):
    """LDAP tap extraction-specific constants following FLEXT unified pattern.

    Inherits from FlextMeltanoConstants for universal constants, defines only
    LDAP tap-specific constants using nested namespace classes.

    Composes with FlextLdapConstants to avoid duplication and ensure consistency.
    """

    class TapLdap:
        """Tap LDAP namespace for cross-project access."""

        DEFAULT_PORT: Final[int] = 389
        DEFAULT_SSL_PORT: Final[int] = 636
        DEFAULT_PAGE_SIZE: Final[int] = 1000
        MAX_LDAP_FILTER_LENGTH: Final[int] = 2048
        DEFAULT_SEARCH_TIMEOUT: Final[int] = 30

        class Ldap:
            """LDAP connection constants."""

            DEFAULT_PORT: Final[int] = FlextLdapConstants.Ldap.ConnectionDefaults.PORT
            DEFAULT_SSL_PORT: Final[int] = 636
            DEFAULT_PAGE_SIZE: Final[int] = 1000
            MAX_FILTER_LENGTH: Final[int] = 2048
            DEFAULT_TIMEOUT: Final[int] = (
                FlextLdapConstants.Ldap.ConnectionDefaults.TIMEOUT
            )
            MAX_PORT: Final[int] = 65535

        class Singer:
            """Singer tap configuration constants."""

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

            MIN_BATCH_SIZE: Final[int] = 1
            MAX_TIMEOUT: Final[int] = (
                FlextMeltanoConstants.Performance.MAX_TIMEOUT_SECONDS
            )
            MAX_DN_LENGTH: Final[int] = 1024
            MAX_ATTRIBUTE_NAME_LENGTH: Final[int] = 255
            MAX_BASE_DN_LENGTH: Final[int] = 512
            MAX_STREAM_PREFIX_LENGTH: Final[int] = 50
            MAX_FILTER_COUNT: Final[int] = 100
            MAX_ATTRIBUTE_COUNT: Final[int] = 500

        class Connection:
            """LDAP tap connection configuration."""

            DEFAULT_HOST: Final[str] = "localhost"
            DEFAULT_PORT: Final[int] = 389
            DEFAULT_SSL_PORT: Final[int] = 636
            DEFAULT_BASE_DN: Final[str] = ""
            DEFAULT_BIND_DN: Final[str] = ""
            DEFAULT_BIND_PASSWORD: Final[str] = ""

        class Search:
            """LDAP search configuration."""

            DEFAULT_SCOPE: Final[str] = "SUBTREE"
            DEFAULT_DEREF: Final[str] = "ALWAYS"
            DEFAULT_SIZE_LIMIT: Final[int] = 0
            DEFAULT_TIME_LIMIT: Final[int] = 0

        type ReplicationMethodLiteral = Literal[
            Replication.Method.FULL_TABLE, Replication.Method.INCREMENTAL
        ]
        "LDAP replication method literal - references Replication.Method StrEnum members."
        TapReplicationMethod = Literal["FULL_TABLE", "INCREMENTAL"]
        TapSearchScope = Literal["BASE", "ONELEVEL", "SUBTREE"]
        TapConnectionMode = Literal["anonymous", "simple", "sasl"]
        TapExecutionMode = Literal["discovery", "extraction", "test", "validate"]


c = FlextTapLdapConstants
__all__ = ["FlextTapLdapConstants", "c"]
