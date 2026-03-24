"""FLEXT Tap LDAP Constants - LDAP tap extraction constants.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from enum import StrEnum, unique
from typing import Final

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
        DEFAULT_PAGE_SIZE: Final[int] = FlextMeltanoConstants.DEFAULT_BATCH_SIZE
        DEFAULT_SEARCH_TIMEOUT: Final[int] = FlextLdapConstants.DEFAULT_TIMEOUT_SECONDS

        class Ldap:
            """LDAP connection constants."""

            DEFAULT_PORT: Final[int] = FlextLdapConstants.Ldap.ConnectionDefaults.PORT
            DEFAULT_PAGE_SIZE: Final[int] = FlextMeltanoConstants.DEFAULT_BATCH_SIZE
            DEFAULT_TIMEOUT: Final[int] = (
                FlextLdapConstants.Ldap.ConnectionDefaults.TIMEOUT
            )
            MAX_PORT: Final[int] = 65535

        class Singer:
            """Singer tap configuration constants."""

            DEFAULT_BATCH_SIZE: Final[int] = FlextMeltanoConstants.DEFAULT_BATCH_SIZE
            MAX_BATCH_SIZE: Final[int] = FlextMeltanoConstants.MAX_BATCH_SIZE

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
            DEFAULT_PORT: Final[int] = 389
            DEFAULT_BASE_DN: Final[str] = ""

        class Search:
            """LDAP search configuration."""

            DEFAULT_SCOPE: Final[str] = "SUBTREE"

    @unique
    class ProjectType(StrEnum):
        """Project-type identifiers for LDAP tap packages."""

        LIBRARY = "library"
        APPLICATION = "application"
        SERVICE = "service"
        TAP_LDAP = "tap-ldap"
        LDAP_EXTRACTOR = "ldap-extractor"
        LDAP_TAP = "ldap-tap"
        LDAP_CONNECTOR = "ldap-connector"
        SINGER_LDAP_TAP = "singer-ldap-tap"
        LDAP_DATA_SOURCE = "ldap-data-source"
        LDAP_EXTRACTION = "ldap-extraction"
        LDIF_PROCESSOR = "ldif-processor"
        LDAP_DIRECTORY_TAP = "ldap-directory-tap"
        ENTERPRISE_LDAP_TAP = "enterprise-ldap-tap"
        LDAP_SINGER_TAP = "ldap-singer-tap"
        DIRECTORY_EXTRACTOR = "directory-extractor"
        LDAP_INTEGRATION = "ldap-integration"


c = FlextTapLdapConstants
__all__ = ["FlextTapLdapConstants", "c"]
