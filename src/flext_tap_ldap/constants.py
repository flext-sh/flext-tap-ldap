"""FLEXT Tap LDAP Constants - LDAP tap extraction constants.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from enum import StrEnum, unique
from typing import Final

from flext_ldap import FlextLdapConstants
from flext_meltano import c


class FlextTapLdapConstants(c, FlextLdapConstants):
    """LDAP tap extraction-specific constants following FLEXT unified pattern.

    Inherits from FlextMeltanoConstants for universal constants, defines only
    LDAP tap-specific constants using nested namespace classes.

    Composes with FlextLdapConstants to avoid duplication and ensure consistency.
    """

    class TapLdap:
        """Tap LDAP namespace for cross-project access.

        LDAP-generic constants are inherited from c.Ldap via MRO:
        - c.Ldap.ConnectionDefaults.PORT (389)
        - c.Ldap.ConnectionDefaults.TIMEOUT (30)

        Meltano-generic constants are inherited from c.Meltano via MRO:
        - c.DEFAULT_BATCH_SIZE (page size)
        """

        DEFAULT_PAGE_SIZE: Final[int] = 1000
        DEFAULT_SEARCH_TIMEOUT: Final[int] = FlextLdapConstants.Ldap.ConnectionDefaults.TIMEOUT

        class Ldap:
            """LDAP tap-specific connection constants."""

            MAX_PORT: Final[int] = 65535

        class Replication:
            """LDAP replication method constants."""

            @unique
            class Method(StrEnum):
                """LDAP replication methods using StrEnum for type safety.

                DRY Pattern:
                    StrEnum is the single source of truth. Use Method.FULL_TABLE.value
                    or Method.FULL_TABLE directly - no string duplication needed.
                """

                FULL_TABLE = "FULL_TABLE"
                INCREMENTAL = "INCREMENTAL"

        class TapValidation:
            """LDAP tap validation constants.

            Note: Does not override parent Validation class to avoid inheritance conflicts.
            """

            MAX_ATTRIBUTE_NAME_LENGTH: Final[int] = 255

        class Connection:
            """LDAP tap connection configuration."""

            DEFAULT_HOST: Final[str] = FlextLdapConstants.LOCALHOST
            DEFAULT_BASE_DN: Final[str] = ""

        class Search:
            """LDAP search configuration."""

            DEFAULT_SCOPE: Final[str] = "SUBTREE"

        @unique
        class TapStatus(StrEnum):
            """LDAP tap execution status enumeration (single source of truth).

            DRY Pattern:
                StrEnum is the single source of truth. Use TapStatus.COMPLETED.value
                or TapStatus.COMPLETED directly - no base strings needed.

            Represents the execution lifecycle states of LDAP tap operations.
            """

            RUNNING = "running"
            COMPLETED = "completed"
            FAILED = "failed"
            CANCELLED = "cancelled"


c = FlextTapLdapConstants
__all__: list[str] = ["FlextTapLdapConstants", "c"]
