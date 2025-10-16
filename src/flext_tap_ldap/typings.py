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
class FlextMeltanoTapLdapTypes(FlextTypes):
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

        type ConnectionConfig = dict[str, str | int | bool | FlextTypes.Dict]
        type AuthenticationConfig = dict[
            str, str | bool | dict[str, FlextMeltanoTapLdapTypes.Core.JsonValue]
        ]
        type TlsConfig = dict[str, bool | str | FlextTypes.Dict]
        type ServerConfig = dict[
            str, str | int | FlextTypes.StringList | FlextTypes.Dict
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
            | FlextTypes.StringList
            | dict[str, FlextMeltanoTapLdapTypes.Core.JsonValue],
        ]
        type LdapAttribute = dict[
            str, str | FlextTypes.StringList | bytes | FlextTypes.Dict
        ]
        type LdapDn = dict[
            str, str | dict[str, FlextMeltanoTapLdapTypes.Core.JsonValue]
        ]
        type LdapObjectClass = dict[str, str | FlextTypes.StringList | FlextTypes.Dict]
        type LdapSchema = dict[
            str, str | list[dict[str, FlextMeltanoTapLdapTypes.Core.JsonValue]]
        ]
        type LdapFilter = dict[str, str | FlextTypes.Dict]

    # =========================================================================
    # LDIF PROCESSING TYPES - LDIF file processing and parsing
    # =========================================================================

    class LdifProcessing:
        """LDIF processing complex types."""

        type LdifRecord = dict[
            str,
            str
            | FlextTypes.StringList
            | dict[str, FlextMeltanoTapLdapTypes.Core.JsonValue],
        ]
        type LdifChangeRecord = dict[
            str, str | list[dict[str, FlextMeltanoTapLdapTypes.Core.JsonValue]]
        ]
        type LdifParserConfig = dict[str, bool | str | int | FlextTypes.Dict]
        type LdifValidation = dict[
            str,
            bool
            | str
            | FlextTypes.StringList
            | dict[str, FlextMeltanoTapLdapTypes.Core.JsonValue],
        ]
        type LdifBatch = dict[
            str, int | list[dict[str, FlextMeltanoTapLdapTypes.Core.JsonValue]]
        ]
        type LdifProcessingMetrics = dict[str, int | float | FlextTypes.Dict]

    # =========================================================================
    # SINGER STREAM TYPES - Singer protocol stream definitions for LDAP
    # =========================================================================

    class SingerStream:
        """Singer stream complex types for LDAP."""

        type StreamDefinition = dict[
            str, str | dict[str, FlextMeltanoTapLdapTypes.Core.JsonValue]
        ]
        type StreamSchema = dict[str, str | FlextTypes.Dict]
        type StreamMetadata = dict[
            str, str | bool | dict[str, FlextMeltanoTapLdapTypes.Core.JsonValue]
        ]
        type StreamRecord = dict[
            str, FlextMeltanoTapLdapTypes.Core.JsonValue | FlextTypes.Dict
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
            str, FlextMeltanoTapLdapTypes.Core.ConfigValue | FlextTypes.Dict
        ]
        type ExtractionConfig = dict[str, str | int | bool | FlextTypes.StringList]
        type FilteringConfig = dict[str, str | FlextTypes.StringList | FlextTypes.Dict]
        type BatchingConfig = dict[
            str, int | bool | dict[str, FlextMeltanoTapLdapTypes.Core.JsonValue]
        ]
        type ReplicationConfig = dict[str, str | bool | FlextTypes.Dict]
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
        type SearchScope = dict[str, str | int | FlextTypes.Dict]
        type SearchAttributes = dict[
            str,
            FlextTypes.StringList | dict[str, FlextMeltanoTapLdapTypes.Core.JsonValue],
        ]
        type SearchResult = dict[
            str, list[dict[str, FlextMeltanoTapLdapTypes.Core.JsonValue]]
        ]
        type PaginationConfig = dict[str, int | str | FlextTypes.Dict]
        type QueryOptimization = dict[
            str, bool | str | dict[str, FlextMeltanoTapLdapTypes.Core.JsonValue]
        ]

    # =========================================================================
    # CORE TYPES - Essential LDAP tap types extending FlextMeltanoTapLdapTypes.Core
    # =========================================================================

    class Core(FlextTypes.Dict):
        """Core LDAP tap types extending FlextMeltanoTapLdapTypes.Core.

        Essential domain-specific types for LDAP tap extraction operations.
        Replaces generic FlextTypes.Dict with semantic LDAP tap types.
        """

        # LDAP connection and authentication types
        type ConnectionDict = dict[str, str | int | bool | FlextTypes.Dict]
        type AuthDict = dict[str, str | bool | FlextTypes.Dict]
        type TlsDict = dict[str, bool | str | FlextTypes.Dict]
        type ServerDict = dict[str, str | int | FlextTypes.StringList | FlextTypes.Dict]

        # LDAP data and record types
        type LdapRecordDict = dict[str, object | FlextTypes.Dict]
        type EntryDict = dict[str, object | FlextTypes.StringList]
        type AttributeDict = dict[str, str | FlextTypes.StringList | FlextTypes.Dict]
        type SchemaDict = dict[str, str | FlextTypes.Dict]

        # Singer stream types for LDAP tap
        type StreamDict = dict[str, object | FlextTypes.Dict]
        type CatalogDict = dict[str, object | FlextTypes.Dict]
        type MetadataDict = dict[str, object | FlextTypes.Dict]
        type StateDict = dict[str, str | FlextTypes.Dict]

        # LDAP query and configuration types
        type QueryDict = dict[str, str | FlextTypes.StringList | FlextTypes.Dict]
        type FilterDict = dict[str, str | FlextTypes.Dict]
        type ConfigDict = dict[str, object | FlextTypes.Dict]
        type ExtractionDict = dict[str, str | int | bool | FlextTypes.StringList]

        # Data processing types
        type RecordDict = FlextTypes.Dict
        type ResultDict = FlextTypes.Dict
        type ContextDict = FlextTypes.Dict
        type EntityDict = FlextTypes.Dict
        type DataDict = FlextTypes.Dict

        # Collection types for LDAP tap operations
        type RecordList = list[RecordDict]
        type EntityList = list[EntityDict]
        type ResultList = list[ResultDict]
        type StringList = FlextTypes.StringList

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
        type TapLdapProjectConfig = dict[
            str, FlextMeltanoTapLdapTypes.Core.ConfigValue | object
        ]
        type LdapExtractionConfig = dict[str, str | int | bool | FlextTypes.StringList]
        type LdapIntegrationConfig = dict[str, bool | str | FlextTypes.Dict]
        type TapLdapPipelineConfig = dict[
            str, FlextMeltanoTapLdapTypes.Core.ConfigValue | object
        ]


# =============================================================================
# PUBLIC API EXPORTS - LDAP tap TypeVars and types
# =============================================================================

__all__: FlextTypes.StringList = [
    "FlextMeltanoTapLdapTypes",
]
