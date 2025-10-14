"""FLEXT Tap LDAP Types - Domain-specific LDAP tap type definitions.

This module provides LDAP tap-specific type definitions extending FlextCore.Types.
Follows FLEXT standards:
- Domain-specific complex types only
- No simple aliases to primitive types
- Python 3.13+ syntax
- Extends FlextCore.Types properly

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import Literal

from flext_core import FlextCore

# =============================================================================
# TAP-LDAP-SPECIFIC TYPE VARIABLES - Domain-specific TypeVars for LDAP tap operations
# =============================================================================


# LDAP tap domain TypeVars
class FlextMeltanoTapLdapTypes(FlextCore.Types):
    """LDAP tap-specific type definitions extending FlextCore.Types.

    Domain-specific type system for LDAP data extraction operations.
    Contains ONLY complex LDAP tap-specific types, no simple aliases.
    Uses Python 3.13+ type syntax and patterns.
    """

    # =========================================================================
    # LDAP CONNECTION TYPES - LDAP server connection configuration
    # =========================================================================

    class LdapConnection:
        """LDAP connection complex types."""

        type ConnectionConfig = dict[str, str | int | bool | FlextCore.Types.Dict]
        type AuthenticationConfig = dict[
            str, str | bool | dict[str, FlextMeltanoTapLdapTypes.Core.JsonValue]
        ]
        type TlsConfig = dict[str, bool | str | FlextCore.Types.Dict]
        type ServerConfig = dict[
            str, str | int | FlextCore.Types.StringList | FlextCore.Types.Dict
        ]
        type PoolingConfig = dict[
            str, int | bool | dict[str, FlextMeltanoTapLdapTypes.Core.JsonValue]
        ]
        type TimeoutConfig = dict[str, int | float]

    # =========================================================================
    # LDAP DATA TYPES - LDAP entries and attributes
    # =========================================================================

    class LdapData:
        """LDAP data complex types."""

        type LdapEntry = dict[
            str,
            str
            | FlextCore.Types.StringList
            | dict[str, FlextMeltanoTapLdapTypes.Core.JsonValue],
        ]
        type LdapAttribute = dict[
            str, str | FlextCore.Types.StringList | bytes | FlextCore.Types.Dict
        ]
        type LdapDn = dict[
            str, str | dict[str, FlextMeltanoTapLdapTypes.Core.JsonValue]
        ]
        type LdapObjectClass = dict[
            str, str | FlextCore.Types.StringList | FlextCore.Types.Dict
        ]
        type LdapSchema = dict[
            str, str | list[dict[str, FlextMeltanoTapLdapTypes.Core.JsonValue]]
        ]
        type LdapFilter = dict[str, str | FlextCore.Types.Dict]

    # =========================================================================
    # LDIF PROCESSING TYPES - LDIF file processing and parsing
    # =========================================================================

    class LdifProcessing:
        """LDIF processing complex types."""

        type LdifRecord = dict[
            str,
            str
            | FlextCore.Types.StringList
            | dict[str, FlextMeltanoTapLdapTypes.Core.JsonValue],
        ]
        type LdifChangeRecord = dict[
            str, str | list[dict[str, FlextMeltanoTapLdapTypes.Core.JsonValue]]
        ]
        type LdifParserConfig = dict[str, bool | str | int | FlextCore.Types.Dict]
        type LdifValidation = dict[
            str,
            bool
            | str
            | FlextCore.Types.StringList
            | dict[str, FlextMeltanoTapLdapTypes.Core.JsonValue],
        ]
        type LdifBatch = dict[
            str, int | list[dict[str, FlextMeltanoTapLdapTypes.Core.JsonValue]]
        ]
        type LdifProcessingMetrics = dict[str, int | float | FlextCore.Types.Dict]

    # =========================================================================
    # SINGER STREAM TYPES - Singer protocol stream definitions for LDAP
    # =========================================================================

    class SingerStream:
        """Singer stream complex types for LDAP."""

        type StreamDefinition = dict[
            str, str | dict[str, FlextMeltanoTapLdapTypes.Core.JsonValue]
        ]
        type StreamSchema = dict[str, str | FlextCore.Types.Dict]
        type StreamMetadata = dict[
            str, str | bool | dict[str, FlextMeltanoTapLdapTypes.Core.JsonValue]
        ]
        type StreamRecord = dict[
            str, FlextMeltanoTapLdapTypes.Core.JsonValue | FlextCore.Types.Dict
        ]
        type StreamState = dict[
            str, str | dict[str, FlextMeltanoTapLdapTypes.Core.JsonValue]
        ]
        type StreamCatalog = dict[
            str, str | list[dict[str, FlextMeltanoTapLdapTypes.Core.JsonValue]]
        ]

    # =========================================================================
    # TAP CONFIGURATION TYPES - LDAP tap configuration and settings
    # =========================================================================

    class TapConfiguration:
        """LDAP tap configuration complex types."""

        type TapConfig = dict[
            str, FlextMeltanoTapLdapTypes.Core.ConfigValue | FlextCore.Types.Dict
        ]
        type ExtractionConfig = dict[str, str | int | bool | FlextCore.Types.StringList]
        type FilteringConfig = dict[
            str, str | FlextCore.Types.StringList | FlextCore.Types.Dict
        ]
        type BatchingConfig = dict[
            str, int | bool | dict[str, FlextMeltanoTapLdapTypes.Core.JsonValue]
        ]
        type ReplicationConfig = dict[str, str | bool | FlextCore.Types.Dict]
        type PerformanceConfig = dict[
            str, int | float | dict[str, FlextMeltanoTapLdapTypes.Core.JsonValue]
        ]

    # =========================================================================
    # LDAP QUERY TYPES - LDAP search and query operations
    # =========================================================================

    class LdapQuery:
        """LDAP query complex types."""

        type SearchFilter = dict[
            str, str | dict[str, FlextMeltanoTapLdapTypes.Core.JsonValue]
        ]
        type SearchScope = dict[str, str | int | FlextCore.Types.Dict]
        type SearchAttributes = dict[
            str,
            FlextCore.Types.StringList
            | dict[str, FlextMeltanoTapLdapTypes.Core.JsonValue],
        ]
        type SearchResult = dict[
            str, list[dict[str, FlextMeltanoTapLdapTypes.Core.JsonValue]]
        ]
        type PaginationConfig = dict[str, int | str | FlextCore.Types.Dict]
        type QueryOptimization = dict[
            str, bool | str | dict[str, FlextMeltanoTapLdapTypes.Core.JsonValue]
        ]

    # =========================================================================
    # CORE TYPES - Essential LDAP tap types extending FlextMeltanoTapLdapTypes.Core
    # =========================================================================

    class Core(FlextCore.Types):
        """Core LDAP tap types extending FlextMeltanoTapLdapTypes.Core.

        Essential domain-specific types for LDAP tap extraction operations.
        Replaces generic FlextCore.Types.Dict with semantic LDAP tap types.
        """

        # LDAP connection and authentication types
        type ConnectionDict = dict[str, str | int | bool | FlextCore.Types.Dict]
        type AuthDict = dict[str, str | bool | FlextCore.Types.Dict]
        type TlsDict = dict[str, bool | str | FlextCore.Types.Dict]
        type ServerDict = dict[
            str, str | int | FlextCore.Types.StringList | FlextCore.Types.Dict
        ]

        # LDAP data and record types
        type LdapRecordDict = dict[str, object | FlextCore.Types.Dict]
        type EntryDict = dict[str, object | FlextCore.Types.StringList]
        type AttributeDict = dict[
            str, str | FlextCore.Types.StringList | FlextCore.Types.Dict
        ]
        type SchemaDict = dict[str, str | FlextCore.Types.Dict]

        # Singer stream types for LDAP tap
        type StreamDict = dict[str, object | FlextCore.Types.Dict]
        type CatalogDict = dict[str, object | FlextCore.Types.Dict]
        type MetadataDict = dict[str, object | FlextCore.Types.Dict]
        type StateDict = dict[str, str | FlextCore.Types.Dict]

        # LDAP query and configuration types
        type QueryDict = dict[
            str, str | FlextCore.Types.StringList | FlextCore.Types.Dict
        ]
        type FilterDict = dict[str, str | FlextCore.Types.Dict]
        type ConfigDict = dict[str, object | FlextCore.Types.Dict]
        type ExtractionDict = dict[str, str | int | bool | FlextCore.Types.StringList]

        # Data processing types
        type RecordDict = FlextCore.Types.Dict
        type ResultDict = FlextCore.Types.Dict
        type ContextDict = FlextCore.Types.Dict
        type EntityDict = FlextCore.Types.Dict
        type DataDict = FlextCore.Types.Dict

        # Collection types for LDAP tap operations
        type RecordList = list[RecordDict]
        type EntityList = list[EntityDict]
        type ResultList = list[ResultDict]
        type StringList = FlextCore.Types.StringList

    # =========================================================================
    # TAP-LDAP PROJECT TYPES - Domain-specific project types extending FlextCore.Types
    # =========================================================================

    class Project(FlextCore.Types.Project):
        """LDAP tap-specific project types extending FlextCore.Types.Project.

        Adds LDAP tap extraction-specific project types while inheriting
        generic types from FlextCore.Types. Follows domain separation principle:
        LDAP tap domain owns LDAP data extraction-specific types.
        """

        # LDAP tap-specific project types extending the generic ones
        type ProjectType = Literal[
            # Generic types inherited from FlextCore.Types.Project
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
        type TapLdapProjectConfig = dict[
            str, FlextMeltanoTapLdapTypes.Core.ConfigValue | object
        ]
        type LdapExtractionConfig = dict[
            str, str | int | bool | FlextCore.Types.StringList
        ]
        type LdapIntegrationConfig = dict[str, bool | str | FlextCore.Types.Dict]
        type TapLdapPipelineConfig = dict[
            str, FlextMeltanoTapLdapTypes.Core.ConfigValue | object
        ]


# =============================================================================
# PUBLIC API EXPORTS - LDAP tap TypeVars and types
# =============================================================================

__all__: FlextCore.Types.StringList = [
    "FlextMeltanoTapLdapTypes",
]
