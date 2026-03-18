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
from typing import TYPE_CHECKING

from flext_ldap import FlextLdapTypes
from flext_meltano import FlextMeltanoTypes
from pydantic import ConfigDict, TypeAdapter

from flext_tap_ldap import c

if TYPE_CHECKING:
    from flext_tap_ldap.ldif_streams import FlextTapLdapLdifStreams
    from flext_tap_ldap.streams import FlextTapLdapStreams


class FlextTapLdapTypes(FlextMeltanoTypes, FlextLdapTypes):
    """LDAP tap-specific type definitions extending t.

    Domain-specific type system for LDAP data extraction operations.
    Contains ONLY complex LDAP tap-specific types, no simple aliases.
    Uses Python 3.13+ type syntax and patterns.
    """

    CONFIG_MAP_ADAPTER: TypeAdapter[dict[str, FlextMeltanoTypes.ContainerValue]] = (
        TypeAdapter(
            dict[str, FlextMeltanoTypes.ContainerValue],
            config=ConfigDict(strict=False),
        )
    )
    STRICT_STR_ADAPTER: TypeAdapter[str] = TypeAdapter(
        str,
        config=ConfigDict(strict=True),
    )

    type TapLdapStream = (
        FlextTapLdapStreams.LDAPBaseStream
        | FlextTapLdapLdifStreams.LdifStream
        | FlextTapLdapLdifStreams.LdifAnalysisStream
    )

    class TapLdap:
        """LDAP connection complex types."""

        type ConnectionConfig = dict[
            str,
            str | int | bool | Mapping[str, Mapping[str, object]],
        ]
        type AuthenticationConfig = dict[
            str,
            str | bool | Mapping[str, Mapping[str, object]],
        ]
        type TlsConfig = dict[str, bool | str | Mapping[str, Mapping[str, object]]]
        type ServerConfig = dict[
            str,
            str | int | list[str] | Mapping[str, Mapping[str, object]],
        ]
        type PoolingConfig = dict[str, int | bool | Mapping[str, Mapping[str, object]]]
        type TimeoutConfig = dict[str, int | float]

    class LdapData:
        """LDAP data complex types."""

        type LdapEntry = dict[str, str | list[str] | Mapping[str, Mapping[str, object]]]
        type LdapAttribute = dict[
            str,
            str | list[str] | bytes | Mapping[str, Mapping[str, object]],
        ]
        type LdapDn = dict[str, str | Mapping[str, Mapping[str, object]]]
        type LdapObjectClass = dict[
            str,
            str | list[str] | Mapping[str, Mapping[str, object]],
        ]
        type LdapSchema = dict[str, str | list[Mapping[str, Mapping[str, object]]]]
        type LdapFilter = dict[str, str | Mapping[str, Mapping[str, object]]]

    class LdifProcessing:
        """LDIF processing complex types."""

        type LdifRecord = dict[
            str, str | list[str] | Mapping[str, Mapping[str, object]]
        ]
        type LdifChangeRecord = dict[
            str, str | list[Mapping[str, Mapping[str, object]]]
        ]
        type LdifParserConfig = dict[
            str,
            bool | str | int | Mapping[str, Mapping[str, object]],
        ]
        type LdifValidation = dict[
            str,
            bool | str | list[str] | Mapping[str, Mapping[str, object]],
        ]
        type LdifBatch = dict[str, int | list[Mapping[str, Mapping[str, object]]]]
        type LdifProcessingMetrics = dict[
            str,
            int | float | Mapping[str, Mapping[str, object]],
        ]

    class SingerStream:
        """Singer stream complex types for LDAP."""

        type StreamDefinition = dict[str, str | Mapping[str, Mapping[str, object]]]
        type StreamSchema = dict[str, str | Mapping[str, Mapping[str, object]]]
        type StreamMetadata = dict[str, str | bool | Mapping[str, Mapping[str, object]]]
        type StreamRecord = dict[
            str, dict[str, object] | Mapping[str, object]
        ]
        type StreamState = dict[str, str | Mapping[str, Mapping[str, object]]]
        type StreamCatalog = dict[str, str | list[Mapping[str, Mapping[str, object]]]]

    class TapConfiguration:
        """LDAP tap configuration complex types."""

        type TapConfig = dict[str, dict[str, object] | Mapping[str, object]]
        type ExtractionConfig = dict[str, str | int | bool | list[str]]
        type FilteringConfig = dict[
            str,
            str | list[str] | Mapping[str, Mapping[str, object]],
        ]
        type BatchingConfig = dict[str, int | bool | Mapping[str, Mapping[str, object]]]
        type ReplicationConfig = dict[
            str, str | bool | Mapping[str, Mapping[str, object]]
        ]
        type PerformanceConfig = dict[
            str, int | float | Mapping[str, Mapping[str, object]]
        ]

    class LdapQuery:
        """LDAP query complex types."""

        type SearchFilter = dict[str, str | Mapping[str, Mapping[str, object]]]
        type SearchScope = dict[str, str | int | Mapping[str, Mapping[str, object]]]
        type SearchAttributes = dict[str, list[str] | dict[str, object]]
        type SearchResult = dict[str, list[dict[str, object]]]
        type PaginationConfig = dict[
            str, int | str | Mapping[str, Mapping[str, object]]
        ]
        type QueryOptimization = dict[
            str, bool | str | Mapping[str, Mapping[str, object]]
        ]

    class TapLdapCore:
        """Core LDAP tap types.

        Essential domain-specific types for LDAP tap extraction operations.
        Uses direct type composition with FlextTypes - no aliases.
        """

        type ConnectionDict = dict[
            str,
            str | int | bool | Mapping[str, Mapping[str, object]],
        ]
        type AuthDict = dict[str, str | bool | Mapping[str, Mapping[str, object]]]
        type TlsDict = dict[str, bool | str | Mapping[str, Mapping[str, object]]]
        type ServerDict = dict[
            str,
            str | int | list[str] | Mapping[str, Mapping[str, object]],
        ]
        type LdapRecordDict = dict[
            str,
            dict[str, object] | Mapping[str, object],
        ]
        type EntryDict = dict[str, dict[str, object] | list[str]]
        type AttributeDict = dict[
            str, str | list[str] | Mapping[str, Mapping[str, object]]
        ]
        type SchemaDict = dict[str, str | Mapping[str, Mapping[str, object]]]
        type StreamDict = dict[str, dict[str, object] | Mapping[str, object]]
        type CatalogDict = dict[
            str, dict[str, object] | Mapping[str, object]
        ]
        type MetadataDict = dict[
            str, dict[str, object] | Mapping[str, object]
        ]
        type StateDict = dict[str, str | Mapping[str, Mapping[str, object]]]
        type QueryDict = dict[str, str | list[str] | Mapping[str, Mapping[str, object]]]
        type FilterDict = dict[str, str | Mapping[str, Mapping[str, object]]]
        type ConfigDict = dict[str, dict[str, object] | Mapping[str, object]]
        type ExtractionDict = dict[str, str | int | bool | list[str]]
        type RecordDict = dict[str, object]
        type ResultDict = dict[str, object]
        type ContextDict = dict[str, object]
        type EntityDict = dict[str, object]
        type DataDict = dict[str, object]
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
            type TapLdapProjectConfig = dict[str, object]
            type LdapExtractionConfig = dict[str, str | int | bool | list[str]]
            type LdapIntegrationConfig = dict[
                str,
                bool | str | Mapping[str, Mapping[str, object]],
            ]
            type TapLdapPipelineConfig = dict[str, object]


t = FlextTapLdapTypes
__all__ = ["FlextTapLdapTypes", "t"]
