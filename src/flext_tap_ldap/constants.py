"""FLEXT Tap LDAP Constants - LDAP tap extraction constants.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from enum import StrEnum, unique
from typing import TYPE_CHECKING, Final

from flext_ldap import FlextLdapConstants
from flext_meltano import c

if TYPE_CHECKING:
    from flext_meltano import t


class FlextTapLdapConstants(c, FlextLdapConstants):
    """LDAP tap extraction-specific constants following FLEXT unified pattern.

    Inherits from FlextMeltanoConstants for universal constants, defines only
    LDAP tap-specific constants using nested namespace classes.

    Composes with FlextLdapConstants to avoid duplication and ensure consistency.
    """

    class TapLdap:
        """Tap LDAP namespace for cross-project access.

        LDAP-generic constants are inherited from c.Ldap via MRO:
        - c.Ldap.PORT (389)
        - c.Ldap.TIMEOUT (30)

        Meltano-generic constants are inherited from c.Meltano via MRO:
        - c.DEFAULT_BATCH_SIZE (page size)
        """

        DEFAULT_PAGE_SIZE: Final[int] = 1000
        DEFAULT_SEARCH_TIMEOUT: Final[int] = FlextLdapConstants.Ldap.TIMEOUT

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

        class Connection:
            """LDAP tap connection configuration."""

            DEFAULT_HOST: Final[str] = FlextLdapConstants.LOCALHOST
            DEFAULT_BASE_DN: Final[str] = ""

        class Search:
            """LDAP search configuration."""

            DEFAULT_SCOPE: Final[str] = "SUBTREE"


c = FlextTapLdapConstants
__all__: t.StrSequence = ("FlextTapLdapConstants", "c")
