"""FLEXT Tap LDAP Types - Domain-specific LDAP tap type definitions.

This module provides LDAP tap-specific type definitions extending t.
Follows FLEXT standards:
- Domain-specific complex types only
- No simple aliases to primitive types
- Python 3.13+ syntax
- Extends t properly

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
    """LDAP tap-specific type definitions extending t.

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
            str,
            str | bool | dict[str, FlextTypes.JsonValue],
        ]
        type TlsConfig = dict[str, bool | str | dict[str, object]]
        type ServerConfig = dict[str, str | int | list[str] | dict[str, object]]
        type PoolingConfig = dict[
            str,
            int | bool | dict[str, FlextTypes.JsonValue],
        ]
        type TimeoutConfig = dict[str, int | float]

    # =========================================================================
    # LDAP DATA TYPES - LDAP entries and attributes
    # =========================================================================

    class LdapData:
        """LDAP data complex types."""

        type LdapEntry = dict[
            str,
            str | list[str] | dict[str, FlextTypes.JsonValue],
        ]
        type LdapAttribute = dict[str, str | list[str] | bytes | dict[str, object]]
        type LdapDn = dict[
            str,
            str | dict[str, FlextTypes.JsonValue],
        ]
        type LdapObjectClass = dict[str, str | list[str] | dict[str, object]]
        type LdapSchema = dict[
            str,
            str | list[dict[str, FlextTypes.JsonValue]],
        ]
        type LdapFilter = dict[str, str | dict[str, object]]

    # =========================================================================
    # LDIF PROCESSING TYPES - LDIF file processing and parsing
    # =========================================================================

    class LdifProcessing:
        """LDIF processing complex types."""

        type LdifRecord = dict[
            str,
            str | list[str] | dict[str, FlextTypes.JsonValue],
        ]
        type LdifChangeRecord = dict[
            str,
            str | list[dict[str, FlextTypes.JsonValue]],
        ]
        type LdifParserConfig = dict[str, bool | str | int | dict[str, object]]
        type LdifValidation = dict[
            str,
            bool | str | list[str] | dict[str, FlextTypes.JsonValue],
        ]
        type LdifBatch = dict[
            str,
            int | list[dict[str, FlextTypes.JsonValue]],
        ]
        type LdifProcessingMetrics = dict[str, int | float | dict[str, object]]

    # =========================================================================
    # SINGER STREAM TYPES - Singer protocol stream definitions for LDAP
    # =========================================================================

    class SingerStream:
        """Singer stream complex types for LDAP."""

        type StreamDefinition = dict[
            str,
            str | dict[str, FlextTypes.JsonValue],
        ]
        type StreamSchema = dict[str, str | dict[str, object]]
        type StreamMetadata = dict[
            str,
            str | bool | dict[str, FlextTypes.JsonValue],
        ]
        type StreamRecord = dict[
            str,
            FlextTypes.JsonValue | dict[str, object],
        ]
        type StreamState = dict[
            str,
            str | dict[str, FlextTypes.JsonValue],
        ]
        type StreamCatalog = dict[
            str,
            str | list[dict[str, FlextTypes.JsonValue]],
        ]

    # =========================================================================
    # TAP CONFIGURATION TYPES - LDAP tap configuration and settings
    # =========================================================================

    class TapConfiguration:
        """LDAP tap configuration complex types."""

        type TapConfig = dict[
            str,
            FlextTypes.GeneralValueType | dict[str, object],
        ]
        type ExtractionConfig = dict[str, str | int | bool | list[str]]
        type FilteringConfig = dict[str, str | list[str] | dict[str, object]]
        type BatchingConfig = dict[
            str,
            int | bool | dict[str, FlextTypes.JsonValue],
        ]
        type ReplicationConfig = dict[str, str | bool | dict[str, object]]
        type PerformanceConfig = dict[
            str,
            int | float | dict[str, FlextTypes.JsonValue],
        ]

    # =========================================================================
    # LDAP QUERY TYPES - LDAP search and query operations
    # =========================================================================

    class LdapQuery:
        """LDAP query complex types."""

        type SearchFilter = dict[
            str,
            str | dict[str, FlextTypes.JsonValue],
        ]
        type SearchScope = dict[str, str | int | dict[str, object]]
        type SearchAttributes = dict[
            str,
            list[str] | dict[str, FlextTypes.JsonValue],
        ]
        type SearchResult = dict[
            str,
            list[dict[str, FlextTypes.JsonValue]],
        ]
        type PaginationConfig = dict[str, int | str | dict[str, object]]
        type QueryOptimization = dict[
            str,
            bool | str | dict[str, FlextTypes.JsonValue],
        ]

    # =========================================================================
    # CORE TYPES - Essential LDAP tap types extending FlextMeltanoTapLdapTypes.Core
    # =========================================================================

    class TapLdapCore:
        """Core LDAP tap types.

        Essential domain-specific types for LDAP tap extraction operations.
        Uses direct type composition with FlextTypes - no aliases.
        """

        # LDAP connection and authentication types
        type ConnectionDict = dict[str, str | int | bool | dict[str, object]]
        type AuthDict = dict[str, str | bool | dict[str, object]]
        type TlsDict = dict[str, bool | str | dict[str, object]]
        type ServerDict = dict[str, str | int | list[str] | dict[str, object]]

        # LDAP data and record types
        type LdapRecordDict = dict[str, object | dict[str, object]]
        type EntryDict = dict[str, object | list[str]]
        type AttributeDict = dict[str, str | list[str] | dict[str, object]]
        type SchemaDict = dict[str, str | dict[str, object]]

        # Singer stream types for LDAP tap
        type StreamDict = dict[str, object | dict[str, object]]
        type CatalogDict = dict[str, object | dict[str, object]]
        type MetadataDict = dict[str, object | dict[str, object]]
        type StateDict = dict[str, str | dict[str, object]]

        # LDAP query and configuration types
        type QueryDict = dict[str, str | list[str] | dict[str, object]]
        type FilterDict = dict[str, str | dict[str, object]]
        type ConfigDict = dict[str, object | dict[str, object]]
        type ExtractionDict = dict[str, str | int | bool | list[str]]

        # Data processing types
        type RecordDict = dict[str, object]
        type ResultDict = dict[str, object]
        type ContextDict = dict[str, object]
        type EntityDict = dict[str, object]
        type DataDict = dict[str, object]

        # Collection types for LDAP tap operations
        type RecordList = list[RecordDict]
        type EntityList = list[EntityDict]
        type ResultList = list[ResultDict]
        type StringList = list[str]

    # =========================================================================
    # TAP-LDAP PROJECT TYPES - Domain-specific project types extending t
    # =========================================================================

    class Project:
        """LDAP tap-specific project types.

        Adds LDAP tap extraction-specific project types.
        Follows domain separation principle:
        LDAP tap domain owns LDAP data extraction-specific types.
        """

        # LDAP tap-specific project types extending the generic ones
        type ProjectType = Literal[
            # Generic types inherited from t
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
            str,
            FlextTypes.GeneralValueType | object,
        ]
        type LdapExtractionConfig = dict[str, str | int | bool | list[str]]
        type LdapIntegrationConfig = dict[str, bool | str | dict[str, object]]
        type TapLdapPipelineConfig = dict[
            str,
            FlextTypes.GeneralValueType | object,
        ]

    class TapLdap:
        """Tap LDAP types namespace for cross-project access.

        Provides organized access to all Tap LDAP types for other FLEXT projects.
        Usage: Other projects can reference `t.TapLdap.LdapData.*`, `t.TapLdap.Project.*`, etc.
        This enables consistent namespace patterns for cross-project type access.

        Examples:
            from flext_tap_ldap.typings import t
            config: t.TapLdap.Project.TapLdapProjectConfig = ...
            entry: t.TapLdap.LdapData.LdapEntry = ...

        Note: Namespace composition via inheritance - no aliases needed.
        Access parent namespaces directly through inheritance.

        """


# Alias for simplified usage
t = FlextMeltanoTapLdapTypes

# Namespace composition via class inheritance
# TapLdap namespace provides access to nested classes through inheritance
# Access patterns:
# - t.TapLdap.* for Tap LDAP-specific types
# - t.Project.* for project types
# - t.Core.* for core types (inherited from parent)

# =============================================================================
# PUBLIC API EXPORTS - LDAP tap TypeVars and types
# =============================================================================

__all__ = [
    "FlextMeltanoTapLdapTypes",
    "t",
]
