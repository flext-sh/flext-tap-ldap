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

from collections.abc import Mapping

from flext_ldap import FlextLdapTypes
from flext_meltano import FlextMeltanoTypes

from flext_tap_ldap import c


class FlextTapLdapTypes(FlextMeltanoTypes, FlextLdapTypes):
    """LDAP tap-specific type definitions extending t.

    Domain-specific type system for LDAP data extraction operations.
    Contains ONLY complex LDAP tap-specific types, no simple aliases.
    Uses Python 3.13+ type syntax and patterns.
    """

    class TapLdap:
        """LDAP connection complex types."""

        type ConnectionConfig = dict[
            str, str | int | bool | Mapping[str, t.ContainerValue]
        ]
        type AuthenticationConfig = dict[
            str, str | bool | Mapping[str, t.ContainerValue]
        ]
        type TlsConfig = dict[str, bool | str | Mapping[str, t.ContainerValue]]
        type ServerConfig = dict[
            str, str | int | list[str] | Mapping[str, t.ContainerValue]
        ]
        type PoolingConfig = dict[str, int | bool | Mapping[str, t.ContainerValue]]
        type TimeoutConfig = dict[str, int | float]

    class LdapData:
        """LDAP data complex types."""

        type LdapEntry = dict[str, str | list[str] | Mapping[str, t.ContainerValue]]
        type LdapAttribute = dict[
            str, str | list[str] | bytes | Mapping[str, t.ContainerValue]
        ]
        type LdapDn = dict[str, str | Mapping[str, t.ContainerValue]]
        type LdapObjectClass = dict[
            str, str | list[str] | Mapping[str, t.ContainerValue]
        ]
        type LdapSchema = dict[str, str | list[Mapping[str, t.ContainerValue]]]
        type LdapFilter = dict[str, str | Mapping[str, t.ContainerValue]]

    class LdifProcessing:
        """LDIF processing complex types."""

        type LdifRecord = dict[str, str | list[str] | Mapping[str, t.ContainerValue]]
        type LdifChangeRecord = dict[str, str | list[Mapping[str, t.ContainerValue]]]
        type LdifParserConfig = dict[
            str, bool | str | int | Mapping[str, t.ContainerValue]
        ]
        type LdifValidation = dict[
            str, bool | str | list[str] | Mapping[str, t.ContainerValue]
        ]
        type LdifBatch = dict[str, int | list[Mapping[str, t.ContainerValue]]]
        type LdifProcessingMetrics = dict[
            str, int | float | Mapping[str, t.ContainerValue]
        ]

    class SingerStream:
        """Singer stream complex types for LDAP."""

        type StreamDefinition = dict[str, str | Mapping[str, t.ContainerValue]]
        type StreamSchema = dict[str, str | Mapping[str, t.ContainerValue]]
        type StreamMetadata = dict[str, str | bool | Mapping[str, t.ContainerValue]]
        type StreamRecord = dict[str, t.ContainerValue | Mapping[str, t.ContainerValue]]
        type StreamState = dict[str, str | Mapping[str, t.ContainerValue]]
        type StreamCatalog = dict[str, str | list[Mapping[str, t.ContainerValue]]]

    class TapConfiguration:
        """LDAP tap configuration complex types."""

        type TapConfig = dict[str, t.ContainerValue | Mapping[str, t.ContainerValue]]
        type ExtractionConfig = dict[str, str | int | bool | list[str]]
        type FilteringConfig = dict[
            str, str | list[str] | Mapping[str, t.ContainerValue]
        ]
        type BatchingConfig = dict[str, int | bool | Mapping[str, t.ContainerValue]]
        type ReplicationConfig = dict[str, str | bool | Mapping[str, t.ContainerValue]]
        type PerformanceConfig = dict[str, int | float | Mapping[str, t.ContainerValue]]

    class LdapQuery:
        """LDAP query complex types."""

        type SearchFilter = dict[str, str | Mapping[str, t.ContainerValue]]
        type SearchScope = dict[str, str | int | Mapping[str, t.ContainerValue]]
        type SearchAttributes = dict[str, list[str] | dict[str, t.ContainerValue]]
        type SearchResult = dict[str, list[dict[str, t.ContainerValue]]]
        type PaginationConfig = dict[str, int | str | Mapping[str, t.ContainerValue]]
        type QueryOptimization = dict[str, bool | str | Mapping[str, t.ContainerValue]]

    class TapLdapCore:
        """Core LDAP tap types.

        Essential domain-specific types for LDAP tap extraction operations.
        Uses direct type composition with FlextTypes - no aliases.
        """

        type ConnectionDict = dict[
            str, str | int | bool | Mapping[str, t.ContainerValue]
        ]
        type AuthDict = dict[str, str | bool | Mapping[str, t.ContainerValue]]
        type TlsDict = dict[str, bool | str | Mapping[str, t.ContainerValue]]
        type ServerDict = dict[
            str, str | int | list[str] | Mapping[str, t.ContainerValue]
        ]
        type LdapRecordDict = dict[
            str, t.ContainerValue | Mapping[str, t.ContainerValue]
        ]
        type EntryDict = dict[str, t.ContainerValue | list[str]]
        type AttributeDict = dict[str, str | list[str] | Mapping[str, t.ContainerValue]]
        type SchemaDict = dict[str, str | Mapping[str, t.ContainerValue]]
        type StreamDict = dict[str, t.ContainerValue | Mapping[str, t.ContainerValue]]
        type CatalogDict = dict[str, t.ContainerValue | Mapping[str, t.ContainerValue]]
        type MetadataDict = dict[str, t.ContainerValue | Mapping[str, t.ContainerValue]]
        type StateDict = dict[str, str | Mapping[str, t.ContainerValue]]
        type QueryDict = dict[str, str | list[str] | Mapping[str, t.ContainerValue]]
        type FilterDict = dict[str, str | Mapping[str, t.ContainerValue]]
        type ConfigDict = dict[str, t.ContainerValue | Mapping[str, t.ContainerValue]]
        type ExtractionDict = dict[str, str | int | bool | list[str]]
        type RecordDict = dict[str, t.ContainerValue]
        type ResultDict = dict[str, t.ContainerValue]
        type ContextDict = dict[str, t.ContainerValue]
        type EntityDict = dict[str, t.ContainerValue]
        type DataDict = dict[str, t.ContainerValue]
        type RecordList = list[RecordDict]
        type EntityList = list[EntityDict]
        type ResultList = list[ResultDict]
        type StringList = list[str]

    class Project:
        """LDAP tap-specific project types.

        Adds LDAP tap extraction-specific project types.
        Follows domain separation principle:
        LDAP tap domain owns LDAP data extraction-specific types.
        """

        type ProjectType = c.ProjectType
        type TapLdapProjectConfig = dict[str, t.ContainerValue]
        type LdapExtractionConfig = dict[str, str | int | bool | list[str]]
        type LdapIntegrationConfig = dict[
            str, bool | str | Mapping[str, t.ContainerValue]
        ]
        type TapLdapPipelineConfig = dict[str, t.ContainerValue]


t = FlextTapLdapTypes
__all__ = ["FlextTapLdapTypes", "t"]
