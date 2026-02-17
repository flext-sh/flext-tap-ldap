"""FLEXT Tap LDAP models - tap-specific events only.

Uses models from parent libraries (flext-ldap, flext-ldif).
Defines only tap-execution and event models specific to LDAP data extraction.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from datetime import UTC, datetime

from flext_core import FlextModels, FlextTypes as t
from flext_core.utilities import u
from flext_ldap import FlextLdapModels
from flext_meltano import FlextMeltanoModels
from pydantic import BaseModel, Field

# Aliases for convenience
m_core = FlextModels


class FlextMeltanoTapLdapModels(FlextMeltanoModels, FlextLdapModels):
    """Complete models for LDAP tap operations extending FlextModels.

    Provides standardized models for all LDAP tap domain entities including:
    - Singer stream metadata and configuration
    - LDAP table extraction configuration
    - Replication and discovery operations
    - Performance monitoring and metrics
    - Singer protocol compliance models

    All nested classes inherit FlextModels validation and patterns.
    """

    class TapLdap:
        """Tap LDAP namespace for cross-project access."""

        def __init_subclass__(cls, **kwargs: t.GeneralValueType) -> None:
            """Warn when FlextMeltanoTapLdapModels is subclassed directly."""
            super().__init_subclass__(**kwargs)
            u.Deprecation.warn_once(
                f"subclass:{cls.__name__}",
                "Subclassing FlextMeltanoTapLdapModels is deprecated. Use FlextModels directly with composition instead.",
            )

        class TapExecutionStartedEvent(m_core.DomainEvent):
            """Event raised when tap execution starts."""

            timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
            tap_name: str = "tap-ldap"
            execution_id: str
            config_hash: str | None = None

            def __init__(
                self,
                event_type: str,
                aggregate_id: str,
                execution_id: str,
                config: dict[str, t.JsonValue] | None = None,
                config_hash: str | None = None,
                **kwargs: t.GeneralValueType,
            ) -> None:
                """Initialize with config data."""
                super().__init__(
                    event_type=event_type,
                    aggregate_id=aggregate_id,
                    data={"config": config} if config else {},
                    **kwargs,
                )
                self.execution_id = execution_id
                self.config_hash = config_hash

            @property
            def config(self) -> dict[str, t.JsonValue] | None:
                """Get config from data field."""
                config_data = self.data.get("config")
                return config_data if isinstance(config_data, dict) else None

        class TapExecutionCompletedEvent(m_core.DomainEvent):
            """Event raised when tap execution completes."""

            timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
            tap_name: str = "tap-ldap"
            execution_id: str
            records_processed: int = 0
            streams_discovered: int = 0
            duration_seconds: float = 0.0

            def __init__(
                self,
                event_type: str,
                aggregate_id: str,
                execution_id: str,
                records_processed: int = 0,
                streams_discovered: int = 0,
                duration_seconds: float = 0.0,
                **kwargs: t.GeneralValueType,
            ) -> None:
                """Initialize with execution data."""
                super().__init__(
                    event_type=event_type,
                    aggregate_id=aggregate_id,
                    data={
                        "records_processed": records_processed,
                        "streams_discovered": streams_discovered,
                        "duration_seconds": duration_seconds,
                    },
                    **kwargs,
                )
                self.execution_id = execution_id
                self.records_processed = records_processed
                self.streams_discovered = streams_discovered
                self.duration_seconds = duration_seconds

            @property
            def records_extracted(self) -> int:
                """Alias for records_processed for backward compatibility."""
                return self.records_processed

            @property
            def duration(self) -> float:
                """Alias for duration_seconds for backward compatibility."""
                return self.duration_seconds

        class StreamDiscoveredEvent(BaseModel):
            """Event raised when a stream is discovered."""

            timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
            stream_name: str
            stream_key_properties: list[str] = Field(default_factory=list)
            bookmark_key: str | None = None

        class RecordExtractedEvent(BaseModel):
            """Event raised when a record is extracted."""

            timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
            stream_name: str
            record_id: str | None = None
            record_size_bytes: int = 0

        class ConnectionTestedEvent(BaseModel):
            """Event raised after connection test."""

            timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
            success: bool
            server_uri: str
            error_message: str | None = None

        class Tests:
            """Test models namespace for flext-tap-ldap tests.

            Contains test-specific models that extend the main models with test-only features.
            These models are only used in tests and not in production code.
            """

            class TestLdapConnection(FlextModels.Entity):
                """Test model for LDAP database connections."""

                host: str
                port: int
                base_dn: str
                bind_dn: str | None = None
                bind_password: str | None = None
                use_ssl: bool = False

                @property
                def connection_string(self) -> str:
                    """Get LDAP connection string."""
                    protocol = "ldaps" if self.use_ssl else "ldap"
                    return f"{protocol}://{self.host}:{self.port}"

            class TestLdapSearch(FlextModels.Entity):
                """Test model for LDAP search operations."""

                base_dn: str
                filter_str: str
                attributes: list[str] | None = None
                scope: str = "SUBTREE"
                size_limit: int | None = None
                time_limit: int | None = None

            class TestLdapStream(FlextModels.Entity):
                """Test model for LDAP Singer streams."""

                stream_name: str
                base_dn: str
                object_class: str
                replication_method: str = "FULL_TABLE"
                is_selected: bool = True

            class TestLdapEntry(FlextModels.Entity):
                """Test model for LDAP directory entries."""

                dn: str
                attributes: dict[str, list[str]]
                object_class: str

                @property
                def attribute_count(self) -> int:
                    """Get number of attributes."""
                    return len(self.attributes)


# Runtime alias for simplified usage
m = FlextMeltanoTapLdapModels
m_tap_ldap = FlextMeltanoTapLdapModels

__all__ = [
    "FlextMeltanoTapLdapModels",
    "m",
    "m_tap_ldap",
]
