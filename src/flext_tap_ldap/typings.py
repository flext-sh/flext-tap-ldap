"""FLEXT Tap LDAP Types - Domain-specific LDAP tap type definitions.

This module provides LDAP tap-specific type definitions extending FlextTypes.
Follows FLEXT standards:
- Domain-specific complex types only
- No simple aliases to primitive types
- Python 3.13+ syntax
- Extends FlextTypes properly

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Literal

from flext_core import FlextTypes

# =============================================================================
# TAP-LDAP-SPECIFIC TYPE VARIABLES - Domain-specific TypeVars for LDAP tap operations
# =============================================================================


# LDAP tap domain TypeVars
class FlextTapLdapTypes(FlextTypes):
    """LDAP tap-specific type definitions extending FlextTypes.

    Domain-specific type system for LDAP data extraction operations.
    Contains ONLY complex LDAP tap-specific types, no simple aliases.
    Uses Python 3.13+ type syntax and patterns.
    """

    # =========================================================================
    # LDAP CONNECTION TYPES - LDAP server connection configuration
    # =========================================================================

    class LdapConnection:
        """LDAP connection complex types."""

        type ConnectionConfig = dict[str, str | int | bool | dict[str, object]]
        type AuthenticationConfig = dict[
            str, str | bool | dict[str, FlextTypes.Core.JsonValue]
        ]
        type TlsConfig = dict[str, bool | str | dict[str, object]]
        type ServerConfig = dict[str, str | int | list[str] | dict[str, object]]
        type PoolingConfig = dict[
            str, int | bool | dict[str, FlextTypes.Core.JsonValue]
        ]
        type TimeoutConfig = dict[str, int | float]

    # =========================================================================
    # LDAP DATA TYPES - LDAP entries and attributes
    # =========================================================================

    class LdapData:
        """LDAP data complex types."""

        type LdapEntry = dict[
            str, str | list[str] | dict[str, FlextTypes.Core.JsonValue]
        ]
        type LdapAttribute = dict[str, str | list[str] | bytes | dict[str, object]]
        type LdapDn = dict[str, str | dict[str, FlextTypes.Core.JsonValue]]
        type LdapObjectClass = dict[str, str | list[str] | dict[str, object]]
        type LdapSchema = dict[str, str | list[dict[str, FlextTypes.Core.JsonValue]]]
        type LdapFilter = dict[str, str | dict[str, object]]

    # =========================================================================
    # LDIF PROCESSING TYPES - LDIF file processing and parsing
    # =========================================================================

    class LdifProcessing:
        """LDIF processing complex types."""

        type LdifRecord = dict[
            str, str | list[str] | dict[str, FlextTypes.Core.JsonValue]
        ]
        type LdifChangeRecord = dict[
            str, str | list[dict[str, FlextTypes.Core.JsonValue]]
        ]
        type LdifParserConfig = dict[str, bool | str | int | dict[str, object]]
        type LdifValidation = dict[
            str, bool | str | list[str] | dict[str, FlextTypes.Core.JsonValue]
        ]
        type LdifBatch = dict[str, int | list[dict[str, FlextTypes.Core.JsonValue]]]
        type LdifProcessingMetrics = dict[str, int | float | dict[str, object]]

    # =========================================================================
    # SINGER STREAM TYPES - Singer protocol stream definitions for LDAP
    # =========================================================================

    class SingerStream:
        """Singer stream complex types for LDAP."""

        type StreamDefinition = dict[str, str | dict[str, FlextTypes.Core.JsonValue]]
        type StreamSchema = dict[str, str | dict[str, object]]
        type StreamMetadata = dict[
            str, str | bool | dict[str, FlextTypes.Core.JsonValue]
        ]
        type StreamRecord = dict[str, FlextTypes.Core.JsonValue | dict[str, object]]
        type StreamState = dict[str, str | dict[str, FlextTypes.Core.JsonValue]]
        type StreamCatalog = dict[str, str | list[dict[str, FlextTypes.Core.JsonValue]]]

    # =========================================================================
    # TAP CONFIGURATION TYPES - LDAP tap configuration and settings
    # =========================================================================

    class TapConfiguration:
        """LDAP tap configuration complex types."""

        type TapConfig = dict[str, FlextTypes.Core.ConfigValue | dict[str, object]]
        type ExtractionConfig = dict[str, str | int | bool | list[str]]
        type FilteringConfig = dict[str, str | list[str] | dict[str, object]]
        type BatchingConfig = dict[
            str, int | bool | dict[str, FlextTypes.Core.JsonValue]
        ]
        type ReplicationConfig = dict[str, str | bool | dict[str, object]]
        type PerformanceConfig = dict[
            str, int | float | dict[str, FlextTypes.Core.JsonValue]
        ]

    # =========================================================================
    # LDAP QUERY TYPES - LDAP search and query operations
    # =========================================================================

    class LdapQuery:
        """LDAP query complex types."""

        type SearchFilter = dict[str, str | dict[str, FlextTypes.Core.JsonValue]]
        type SearchScope = dict[str, str | int | dict[str, object]]
        type SearchAttributes = dict[
            str, list[str] | dict[str, FlextTypes.Core.JsonValue]
        ]
        type SearchResult = dict[str, list[dict[str, FlextTypes.Core.JsonValue]]]
        type PaginationConfig = dict[str, int | str | dict[str, object]]
        type QueryOptimization = dict[
            str, bool | str | dict[str, FlextTypes.Core.JsonValue]
        ]

    # =========================================================================
    # TAP-LDAP PROJECT TYPES - Domain-specific project types extending FlextTypes
    # =========================================================================

    class Project(FlextTypes.Project):
        """LDAP tap-specific project types extending FlextTypes.Project.

        Adds LDAP tap extraction-specific project types while inheriting
        generic types from FlextTypes. Follows domain separation principle:
        LDAP tap domain owns LDAP data extraction-specific types.
        """

        # LDAP tap-specific project types extending the generic ones
        type ProjectType = Literal[
            # Generic types inherited from FlextTypes.Project
            "library",
            "application",
            "service",
            # LDAP tap-specific types
            "tap-ldap",
            "ldap-extractor",
            "ldap-tap",
            "ldap-connector",
            "singer-ldap-tap",
            "ldap-data-source",
            "ldap-extraction",
            "ldif-processor",
            "ldap-directory-tap",
            "enterprise-ldap-tap",
            "ldap-singer-tap",
            "directory-extractor",
            "ldap-integration",
        ]

        # LDAP tap-specific project configurations
        type TapLdapProjectConfig = dict[str, FlextTypes.Core.ConfigValue | object]
        type LdapExtractionConfig = dict[str, str | int | bool | list[str]]
        type LdapIntegrationConfig = dict[str, bool | str | dict[str, object]]
        type TapLdapPipelineConfig = dict[str, FlextTypes.Core.ConfigValue | object]


# =============================================================================
# PUBLIC API EXPORTS - LDAP tap TypeVars and types
# =============================================================================

__all__: list[str] = [
    "FlextTapLdapTypes",
]
