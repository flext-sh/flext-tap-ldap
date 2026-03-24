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

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from flext_ldap import FlextLdapTypes
from flext_meltano import FlextMeltanoTypes
from pydantic import ConfigDict, TypeAdapter

from flext_tap_ldap.constants import c

if TYPE_CHECKING:
    from flext_tap_ldap.ldif_streams import FlextTapLdapLdifStreams
    from flext_tap_ldap.streams import FlextTapLdapStreams


class FlextTapLdapTypes(FlextMeltanoTypes, FlextLdapTypes):
    """LDAP tap-specific type definitions extending t.

    Domain-specific type system for LDAP data extraction operations.
    Contains ONLY complex LDAP tap-specific types, no simple aliases.
    Uses Python 3.13+ type syntax and patterns.
    """

    CONFIG_MAP_ADAPTER: TypeAdapter[Mapping[str, FlextMeltanoTypes.ContainerValue]] = (
        TypeAdapter(
            Mapping[str, FlextMeltanoTypes.ContainerValue],
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

        type ConnectionConfig = Mapping[
            str,
            t.Scalar | Mapping[str, t.ContainerValueMapping],
        ]
        type AuthenticationConfig = Mapping[
            str,
            str | bool | Mapping[str, t.ContainerValueMapping],
        ]
        type TlsConfig = Mapping[
            str,
            bool | str | Mapping[str, t.ContainerValueMapping],
        ]
        type ServerConfig = Mapping[
            str,
            str | int | Sequence[str] | Mapping[str, t.ContainerValueMapping],
        ]
        type PoolingConfig = Mapping[
            str,
            int | bool | Mapping[str, t.ContainerValueMapping],
        ]
        type TimeoutConfig = Mapping[str, int | float]

    class LdapData:
        """LDAP data complex types."""

        type LdapEntry = Mapping[
            str,
            str | Sequence[str] | Mapping[str, t.ContainerValueMapping],
        ]
        type LdapAttribute = Mapping[
            str,
            str | Sequence[str] | bytes | Mapping[str, t.ContainerValueMapping],
        ]
        type LdapDn = Mapping[str, str | Mapping[str, t.ContainerValueMapping]]
        type LdapObjectClass = Mapping[
            str,
            str | Sequence[str] | Mapping[str, t.ContainerValueMapping],
        ]
        type LdapSchema = Mapping[
            str,
            str | Sequence[Mapping[str, t.ContainerValueMapping]],
        ]
        type LdapFilter = Mapping[
            str,
            str | Mapping[str, t.ContainerValueMapping],
        ]

    class LdifProcessing:
        """LDIF processing complex types."""

        type LdifRecord = Mapping[
            str, str | Sequence[str] | Mapping[str, t.ContainerValueMapping]
        ]
        type LdifChangeRecord = Mapping[
            str, str | Sequence[Mapping[str, t.ContainerValueMapping]]
        ]
        type LdifParserConfig = Mapping[
            str,
            bool | str | int | Mapping[str, t.ContainerValueMapping],
        ]
        type LdifValidation = Mapping[
            str,
            bool | str | Sequence[str] | Mapping[str, t.ContainerValueMapping],
        ]
        type LdifBatch = Mapping[
            str,
            int | Sequence[Mapping[str, t.ContainerValueMapping]],
        ]
        type LdifProcessingMetrics = Mapping[
            str,
            int | float | Mapping[str, t.ContainerValueMapping],
        ]

    class SingerStream:
        """Singer stream complex types for LDAP."""

        type StreamDefinition = Mapping[
            str,
            str | Mapping[str, t.ContainerValueMapping],
        ]
        type StreamSchema = Mapping[str, str | Mapping[str, t.ContainerValueMapping]]
        type StreamMetadata = Mapping[
            str,
            str | bool | Mapping[str, t.ContainerValueMapping],
        ]
        type StreamRecord = Mapping[
            str,
            Mapping[str, t.ContainerValue],
        ]
        type StreamState = Mapping[str, str | Mapping[str, t.ContainerValueMapping]]
        type StreamCatalog = Mapping[
            str,
            str | Sequence[Mapping[str, t.ContainerValueMapping]],
        ]

    class TapConfiguration:
        """LDAP tap configuration complex types."""

        type TapConfig = Mapping[
            str,
            Mapping[str, t.ContainerValue],
        ]
        type ExtractionConfig = Mapping[str, t.Scalar | Sequence[str]]
        type FilteringConfig = Mapping[
            str,
            str | Sequence[str] | Mapping[str, t.ContainerValueMapping],
        ]
        type BatchingConfig = Mapping[
            str,
            int | bool | Mapping[str, t.ContainerValueMapping],
        ]
        type ReplicationConfig = Mapping[
            str, str | bool | Mapping[str, t.ContainerValueMapping]
        ]
        type PerformanceConfig = Mapping[
            str, int | float | Mapping[str, t.ContainerValueMapping]
        ]

    class LdapQuery:
        """LDAP query complex types."""

        type SearchFilter = Mapping[
            str,
            str | Mapping[str, t.ContainerValueMapping],
        ]
        type SearchScope = Mapping[
            str,
            str | int | Mapping[str, t.ContainerValueMapping],
        ]
        type SearchAttributes = Mapping[
            str, Sequence[str] | Mapping[str, t.ContainerValue]
        ]
        type SearchResult = Mapping[str, Sequence[Mapping[str, t.ContainerValue]]]
        type PaginationConfig = Mapping[
            str, int | str | Mapping[str, t.ContainerValueMapping]
        ]
        type QueryOptimization = Mapping[
            str, bool | str | Mapping[str, t.ContainerValueMapping]
        ]

    class TapLdapCore:
        """Core LDAP tap types.

        Essential domain-specific types for LDAP tap extraction operations.
        Uses direct type composition with FlextTypes - no aliases.
        """

        type ConnectionDict = Mapping[
            str,
            t.Scalar | Mapping[str, t.ContainerValueMapping],
        ]
        type AuthDict = Mapping[
            str,
            str | bool | Mapping[str, t.ContainerValueMapping],
        ]
        type TlsDict = Mapping[
            str,
            bool | str | Mapping[str, t.ContainerValueMapping],
        ]
        type ServerDict = Mapping[
            str,
            str | int | Sequence[str] | Mapping[str, t.ContainerValueMapping],
        ]
        type LdapRecordDict = Mapping[
            str,
            Mapping[str, t.ContainerValue],
        ]
        type EntryDict = Mapping[str, Mapping[str, t.ContainerValue] | Sequence[str]]
        type AttributeDict = Mapping[
            str, str | Sequence[str] | Mapping[str, t.ContainerValueMapping]
        ]
        type SchemaDict = Mapping[str, str | Mapping[str, t.ContainerValueMapping]]
        type StreamDict = Mapping[
            str,
            Mapping[str, t.ContainerValue],
        ]
        type CatalogDict = Mapping[
            str,
            Mapping[str, t.ContainerValue],
        ]
        type MetadataDict = Mapping[
            str,
            Mapping[str, t.ContainerValue],
        ]
        type StateDict = Mapping[str, str | Mapping[str, t.ContainerValueMapping]]
        type QueryDict = Mapping[
            str,
            str | Sequence[str] | Mapping[str, t.ContainerValueMapping],
        ]
        type FilterDict = Mapping[
            str,
            str | Mapping[str, t.ContainerValueMapping],
        ]
        type ConfigDict = Mapping[
            str,
            Mapping[str, t.ContainerValue],
        ]
        type ExtractionDict = Mapping[str, t.Scalar | Sequence[str]]
        type RecordDict = Mapping[str, t.ContainerValue]
        type ResultDict = Mapping[str, t.ContainerValue]
        type ContextDict = Mapping[str, t.ContainerValue]
        type EntityDict = Mapping[str, t.ContainerValue]
        type DataDict = Mapping[str, t.ContainerValue]
        type RecordList = Sequence[RecordDict]
        type EntityList = Sequence[EntityDict]
        type ResultList = Sequence[ResultDict]
        type StringList = Sequence[str]

        class Project:
            """LDAP tap-specific project types.

            Adds LDAP tap extraction-specific project types.
            Follows domain separation principle:
            LDAP tap domain owns LDAP data extraction-specific types.
            """

            type ProjectType = c.ProjectType
            type TapLdapProjectConfig = Mapping[str, t.ContainerValue]
            type LdapExtractionConfig = Mapping[str, t.Scalar | Sequence[str]]
            type LdapIntegrationConfig = Mapping[
                str,
                bool | str | Mapping[str, t.ContainerValueMapping],
            ]
            type TapLdapPipelineConfig = Mapping[str, t.ContainerValue]


t = FlextTapLdapTypes
__all__ = ["FlextTapLdapTypes", "t"]
