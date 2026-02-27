"""FLEXT Tap LDAP models - tap-specific events only.

Uses models from parent libraries (flext-ldap, flext-ldif).
Defines only tap-execution and event models specific to LDAP data extraction.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from flext_core import FlextModels
from flext_ldap import FlextLdapModels
from flext_meltano import FlextMeltanoModels
from pydantic import Field


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

        class TapExecutionStartedEvent(FlextModels.DomainEvent):
            """Event raised when tap execution starts."""

            timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
            tap_name: str = "tap-ldap"
            execution_id: str = ""
            config_hash: str | None = None

        class TapExecutionCompletedEvent(FlextModels.DomainEvent):
            """Event raised when tap execution completes."""

            timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
            tap_name: str = "tap-ldap"
            execution_id: str = ""
            records_processed: int = 0
            streams_discovered: int = 0
            duration_seconds: float = 0.0

            @property
            def records_extracted(self) -> int:
                """Alias for records_processed for backward compatibility."""
                return self.records_processed

            @property
            def duration(self) -> float:
                """Alias for duration_seconds for backward compatibility."""
                return self.duration_seconds

        class StreamDiscoveredEvent(FlextModels.DomainEvent):
            """Event raised when a stream is discovered."""

            event_type: str = Field(default="stream_discovered", frozen=True)
            aggregate_id: str = Field(
                default="", description="Stream name as aggregate identifier"
            )
            stream_name: str
            stream_key_properties: list[str] = Field(default_factory=list)
            bookmark_key: str | None = None

            def __init__(self, **data: Any) -> None:
                """Initialize StreamDiscoveredEvent and set aggregate_id."""
                # Set aggregate_id from stream_name if not provided
                if "aggregate_id" not in data and "stream_name" in data:
                    data["aggregate_id"] = data["stream_name"]
                super().__init__(**data)

        class RecordExtractedEvent(FlextModels.DomainEvent):
            """Event raised when a record is extracted."""

            event_type: str = Field(default="record_extracted", frozen=True)
            aggregate_id: str = Field(
                default="", description="Stream name as aggregate identifier"
            )
            stream_name: str
            record_id: str | None = None
            record_size_bytes: int = 0

            def __init__(self, **data: Any) -> None:
                """Initialize RecordExtractedEvent and set aggregate_id."""
                # Set aggregate_id from stream_name if not provided
                if "aggregate_id" not in data and "stream_name" in data:
                    data["aggregate_id"] = data["stream_name"]
                super().__init__(**data)

        class ConnectionTestedEvent(FlextModels.DomainEvent):
            """Event raised after connection test."""

            event_type: str = Field(default="connection_tested", frozen=True)
            aggregate_id: str = Field(
                default="", description="Server URI as aggregate identifier"
            )
            success: bool
            server_uri: str
            error_message: str | None = None

            def __init__(self, **data: Any) -> None:
                """Initialize ConnectionTestedEvent and set aggregate_id."""
                # Set aggregate_id from server_uri if not provided
                if "aggregate_id" not in data and "server_uri" in data:
                    data["aggregate_id"] = data["server_uri"]
                super().__init__(**data)

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
m: type[FlextMeltanoTapLdapModels] = FlextMeltanoTapLdapModels

__all__ = [
    "FlextMeltanoTapLdapModels",
    "m",
]
