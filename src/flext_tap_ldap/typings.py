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
            FlextMeltanoTypes.Scalar
            | Mapping[str, FlextMeltanoTypes.ContainerValueMapping],
        ]
        type AuthenticationConfig = Mapping[
            str,
            str | bool | Mapping[str, FlextMeltanoTypes.ContainerValueMapping],
        ]
        type TlsConfig = Mapping[
            str,
            bool | str | Mapping[str, FlextMeltanoTypes.ContainerValueMapping],
        ]
        type ServerConfig = Mapping[
            str,
            str
            | int
            | FlextMeltanoTypes.StrSequence
            | Mapping[str, FlextMeltanoTypes.ContainerValueMapping],
        ]
        type PoolingConfig = Mapping[
            str,
            int | bool | Mapping[str, FlextMeltanoTypes.ContainerValueMapping],
        ]
        type TimeoutConfig = Mapping[str, int | float]

    class LdapData:
        """LDAP data complex types."""

        type LdapEntry = Mapping[
            str,
            str
            | FlextMeltanoTypes.StrSequence
            | Mapping[str, FlextMeltanoTypes.ContainerValueMapping],
        ]
        type LdapAttribute = Mapping[
            str,
            str
            | FlextMeltanoTypes.StrSequence
            | bytes
            | Mapping[str, FlextMeltanoTypes.ContainerValueMapping],
        ]
        type LdapDn = Mapping[
            str,
            str | Mapping[str, FlextMeltanoTypes.ContainerValueMapping],
        ]
        type LdapObjectClass = Mapping[
            str,
            str
            | FlextMeltanoTypes.StrSequence
            | Mapping[str, FlextMeltanoTypes.ContainerValueMapping],
        ]
        type LdapSchema = Mapping[
            str,
            str | Sequence[Mapping[str, FlextMeltanoTypes.ContainerValueMapping]],
        ]
        type LdapFilter = Mapping[
            str,
            str | Mapping[str, FlextMeltanoTypes.ContainerValueMapping],
        ]

    class LdifProcessing:
        """LDIF processing complex types."""

        type LdifRecord = Mapping[
            str,
            str
            | FlextMeltanoTypes.StrSequence
            | Mapping[str, FlextMeltanoTypes.ContainerValueMapping],
        ]
        type LdifChangeRecord = Mapping[
            str,
            str | Sequence[Mapping[str, FlextMeltanoTypes.ContainerValueMapping]],
        ]
        type LdifParserConfig = Mapping[
            str,
            bool | str | int | Mapping[str, FlextMeltanoTypes.ContainerValueMapping],
        ]
        type LdifValidation = Mapping[
            str,
            bool
            | str
            | FlextMeltanoTypes.StrSequence
            | Mapping[str, FlextMeltanoTypes.ContainerValueMapping],
        ]
        type LdifBatch = Mapping[
            str,
            int | Sequence[Mapping[str, FlextMeltanoTypes.ContainerValueMapping]],
        ]
        type LdifProcessingMetrics = Mapping[
            str,
            int | float | Mapping[str, FlextMeltanoTypes.ContainerValueMapping],
        ]

    class SingerStream:
        """Singer stream complex types for LDAP."""

        type StreamDefinition = Mapping[
            str,
            str | Mapping[str, FlextMeltanoTypes.ContainerValueMapping],
        ]
        type StreamSchema = Mapping[
            str,
            str | Mapping[str, FlextMeltanoTypes.ContainerValueMapping],
        ]
        type StreamMetadata = Mapping[
            str,
            str | bool | Mapping[str, FlextMeltanoTypes.ContainerValueMapping],
        ]
        type StreamRecord = Mapping[
            str,
            Mapping[str, FlextMeltanoTypes.ContainerValue],
        ]
        type StreamState = Mapping[
            str,
            str | Mapping[str, FlextMeltanoTypes.ContainerValueMapping],
        ]
        type StreamCatalog = Mapping[
            str,
            str | Sequence[Mapping[str, FlextMeltanoTypes.ContainerValueMapping]],
        ]

    class TapConfiguration:
        """LDAP tap configuration complex types."""

        type TapConfig = Mapping[
            str,
            Mapping[str, FlextMeltanoTypes.ContainerValue],
        ]
        type ExtractionConfig = Mapping[
            str,
            FlextMeltanoTypes.Scalar | FlextMeltanoTypes.StrSequence,
        ]
        type FilteringConfig = Mapping[
            str,
            str
            | FlextMeltanoTypes.StrSequence
            | Mapping[str, FlextMeltanoTypes.ContainerValueMapping],
        ]
        type BatchingConfig = Mapping[
            str,
            int | bool | Mapping[str, FlextMeltanoTypes.ContainerValueMapping],
        ]
        type ReplicationConfig = Mapping[
            str,
            str | bool | Mapping[str, FlextMeltanoTypes.ContainerValueMapping],
        ]
        type PerformanceConfig = Mapping[
            str,
            int | float | Mapping[str, FlextMeltanoTypes.ContainerValueMapping],
        ]

    class LdapQuery:
        """LDAP query complex types."""

        type SearchFilter = Mapping[
            str,
            str | Mapping[str, FlextMeltanoTypes.ContainerValueMapping],
        ]
        type SearchScope = Mapping[
            str,
            str | int | Mapping[str, FlextMeltanoTypes.ContainerValueMapping],
        ]
        type SearchAttributes = Mapping[
            str,
            FlextMeltanoTypes.StrSequence
            | Mapping[str, FlextMeltanoTypes.ContainerValue],
        ]
        type SearchResult = Mapping[
            str,
            Sequence[Mapping[str, FlextMeltanoTypes.ContainerValue]],
        ]
        type PaginationConfig = Mapping[
            str,
            int | str | Mapping[str, FlextMeltanoTypes.ContainerValueMapping],
        ]
        type QueryOptimization = Mapping[
            str,
            bool | str | Mapping[str, FlextMeltanoTypes.ContainerValueMapping],
        ]

    class TapLdapCore:
        """Core LDAP tap types.

        Essential domain-specific types for LDAP tap extraction operations.
        Uses direct type composition with FlextTypes - no aliases.
        """

        type ConnectionDict = Mapping[
            str,
            FlextMeltanoTypes.Scalar
            | Mapping[str, FlextMeltanoTypes.ContainerValueMapping],
        ]
        type AuthDict = Mapping[
            str,
            str | bool | Mapping[str, FlextMeltanoTypes.ContainerValueMapping],
        ]
        type TlsDict = Mapping[
            str,
            bool | str | Mapping[str, FlextMeltanoTypes.ContainerValueMapping],
        ]
        type ServerDict = Mapping[
            str,
            str
            | int
            | FlextMeltanoTypes.StrSequence
            | Mapping[str, FlextMeltanoTypes.ContainerValueMapping],
        ]
        type LdapRecordDict = Mapping[
            str,
            Mapping[str, FlextMeltanoTypes.ContainerValue],
        ]
        type EntryDict = Mapping[
            str,
            Mapping[str, FlextMeltanoTypes.ContainerValue]
            | FlextMeltanoTypes.StrSequence,
        ]
        type AttributeDict = Mapping[
            str,
            str
            | FlextMeltanoTypes.StrSequence
            | Mapping[str, FlextMeltanoTypes.ContainerValueMapping],
        ]
        type SchemaDict = Mapping[
            str,
            str | Mapping[str, FlextMeltanoTypes.ContainerValueMapping],
        ]
        type StreamDict = Mapping[
            str,
            Mapping[str, FlextMeltanoTypes.ContainerValue],
        ]
        type CatalogDict = Mapping[
            str,
            Mapping[str, FlextMeltanoTypes.ContainerValue],
        ]
        type MetadataDict = Mapping[
            str,
            Mapping[str, FlextMeltanoTypes.ContainerValue],
        ]
        type StateDict = Mapping[
            str,
            str | Mapping[str, FlextMeltanoTypes.ContainerValueMapping],
        ]
        type QueryDict = Mapping[
            str,
            str
            | FlextMeltanoTypes.StrSequence
            | Mapping[str, FlextMeltanoTypes.ContainerValueMapping],
        ]
        type FilterDict = Mapping[
            str,
            str | Mapping[str, FlextMeltanoTypes.ContainerValueMapping],
        ]
        type ConfigDict = Mapping[
            str,
            Mapping[str, FlextMeltanoTypes.ContainerValue],
        ]
        type ExtractionDict = Mapping[
            str,
            FlextMeltanoTypes.Scalar | FlextMeltanoTypes.StrSequence,
        ]
        type RecordDict = Mapping[str, FlextMeltanoTypes.ContainerValue]
        type ResultDict = Mapping[str, FlextMeltanoTypes.ContainerValue]
        type ContextDict = Mapping[str, FlextMeltanoTypes.ContainerValue]
        type EntityDict = Mapping[str, FlextMeltanoTypes.ContainerValue]
        type DataDict = Mapping[str, FlextMeltanoTypes.ContainerValue]
        type RecordList = Sequence[RecordDict]
        type EntityList = Sequence[EntityDict]
        type ResultList = Sequence[ResultDict]
        type StringList = FlextMeltanoTypes.StrSequence

        class Project:
            """LDAP tap-specific project types.

            Adds LDAP tap extraction-specific project types.
            Follows domain separation principle:
            LDAP tap domain owns LDAP data extraction-specific types.
            """

            type ProjectType = c.ProjectType
            type TapLdapProjectConfig = Mapping[str, FlextMeltanoTypes.ContainerValue]
            type LdapExtractionConfig = Mapping[
                str,
                FlextMeltanoTypes.Scalar | FlextMeltanoTypes.StrSequence,
            ]
            type LdapIntegrationConfig = Mapping[
                str,
                bool | str | Mapping[str, FlextMeltanoTypes.ContainerValueMapping],
            ]
            type TapLdapPipelineConfig = Mapping[str, FlextMeltanoTypes.ContainerValue]


t = FlextTapLdapTypes
__all__ = ["FlextTapLdapTypes", "t"]
