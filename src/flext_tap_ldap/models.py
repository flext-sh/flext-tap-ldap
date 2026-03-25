"""FLEXT Tap LDAP models - tap-specific events only.

Uses models from parent libraries (flext-ldap, flext-ldif).
Defines only tap-execution and event models specific to LDAP data extraction.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated, Self
from uuid import uuid4

from flext_core import t
from flext_ldap import FlextLdapModels
from flext_meltano import FlextMeltanoModels
from pydantic import BaseModel, Field, model_validator

from flext_tap_ldap.constants import c


class FlextTapLdapModels(FlextMeltanoModels, FlextLdapModels):
    """Complete models for LDAP tap operations extending FlextLdapModels.

    Provides standardized models for all LDAP tap domain entities including:
    - Singer stream metadata and configuration
    - LDAP table extraction configuration
    - Replication and discovery operations
    - Performance monitoring and metrics
    - Singer protocol compliance models

    All nested classes inherit FlextLdapModels validation and patterns.
    """

    class TapLdap:
        """Tap LDAP namespace for cross-project access."""

        # ── Domain Events ────────────────────────────────────────────────────

        class TapExecutionStartedEvent(FlextLdapModels.Event):
            """Event raised when tap execution starts."""

            timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
            tap_name: str = "tap-ldap"
            execution_id: str = ""
            config_hash: str | None = None

        class TapExecutionCompletedEvent(FlextLdapModels.Event):
            """Event raised when tap execution completes."""

            timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
            tap_name: str = "tap-ldap"
            execution_id: str = ""
            records_processed: int = 0
            streams_discovered: int = 0
            duration_seconds: float = 0.0

        class StreamDiscoveredEvent(FlextLdapModels.Event):
            """Event raised when a stream is discovered."""

            event_type: Annotated[str, Field(default="stream_discovered", frozen=True)]
            aggregate_id: Annotated[
                str,
                Field(
                    default="",
                    description="Stream name as aggregate identifier",
                ),
            ]
            stream_name: str
            stream_key_properties: t.StrSequence = Field(default_factory=list)
            bookmark_key: str | None = None

            @model_validator(mode="before")
            @classmethod
            def set_aggregate_id(cls, data: t.ContainerMapping) -> t.ContainerMapping:
                """Set aggregate_id from stream_name if not provided."""
                if (
                    isinstance(data, dict)
                    and "aggregate_id" not in data
                    and "stream_name" in data
                ):
                    data["aggregate_id"] = data["stream_name"]
                return data

        class RecordExtractedEvent(FlextLdapModels.Event):
            """Event raised when a record is extracted."""

            event_type: Annotated[str, Field(default="record_extracted", frozen=True)]
            aggregate_id: Annotated[
                str,
                Field(
                    default="",
                    description="Stream name as aggregate identifier",
                ),
            ]
            stream_name: str
            record_id: str | None = None
            record_size_bytes: int = 0

            @model_validator(mode="before")
            @classmethod
            def set_aggregate_id(cls, data: t.ContainerMapping) -> t.ContainerMapping:
                """Set aggregate_id from stream_name if not provided."""
                if (
                    isinstance(data, dict)
                    and "aggregate_id" not in data
                    and "stream_name" in data
                ):
                    data["aggregate_id"] = data["stream_name"]
                return data

        class TapExecution(FlextLdapModels.Entity):
            """Execution state and metrics for a tap run."""

            id: str = Field(default_factory=lambda: uuid4().hex)
            execution_id: str
            connection_id: str
            command: str
            tap_status: str = "created"
            config: t.ContainerMapping = Field(default_factory=dict)
            catalog: t.ContainerMapping = Field(default_factory=dict)
            state: t.ContainerMapping = Field(default_factory=dict)
            started_at: datetime | None = None
            completed_at: datetime | None = None
            records_extracted: int = 0
            streams_processed: int = 0
            exit_code: int | None = None
            stdout: str | None = None
            stderr: str | None = None

            def start_execution(self) -> None:
                """Mark execution as running with current timestamp."""
                self.tap_status = "running"
                self.started_at = datetime.now(UTC)

            def complete_execution(
                self,
                exit_code: int,
                stdout: str | None = None,
                stderr: str | None = None,
            ) -> None:
                """Mark execution as completed with exit code and output."""
                self.tap_status = "completed" if exit_code == 0 else "failed"
                self.completed_at = datetime.now(UTC)
                self.exit_code = exit_code
                self.stdout = stdout
                self.stderr = stderr

            def cancel_execution(self) -> None:
                """Mark execution as cancelled."""
                self.tap_status = "cancelled"
                self.completed_at = datetime.now(UTC)

            def update_metrics(
                self,
                records_extracted: int,
                streams_processed: int,
            ) -> None:
                """Update extraction metrics with record and stream counts."""
                self.records_extracted = records_extracted
                self.streams_processed = streams_processed

        class ConnectionTestedEvent(FlextLdapModels.Event):
            """Event raised after connection test."""

            event_type: Annotated[str, Field(default="connection_tested", frozen=True)]
            aggregate_id: Annotated[
                str,
                Field(
                    default="",
                    description="Server URI as aggregate identifier",
                ),
            ]
            success: bool
            server_uri: str
            error_message: str | None = None

            @model_validator(mode="before")
            @classmethod
            def set_aggregate_id(cls, data: t.ContainerMapping) -> t.ContainerMapping:
                """Set aggregate_id from server_uri if not provided."""
                if (
                    isinstance(data, dict)
                    and "aggregate_id" not in data
                    and "server_uri" in data
                ):
                    data["aggregate_id"] = data["server_uri"]
                return data

        # ── Config Parameter Objects ─────────────────────────────────────────

        class LdapConnectionConfig(BaseModel):
            """LDAP connection configuration extracted from tap config."""

            host: str = ""
            port: int = c.TapLdap.DEFAULT_PORT
            bind_dn: str | None = None
            bind_password: str | None = None
            use_ssl: bool = False
            timeout_seconds: int = c.TapLdap.DEFAULT_SEARCH_TIMEOUT
            base_dn: str = ""

        class CustomPropertyDefinition(BaseModel):
            """Definition of a custom stream property."""

            type: str = "string"
            description: str | None = None

        class CustomStreamParams(BaseModel):
            """Parameters for creating a custom LDAP stream."""

            name: str
            search_filter: str
            schema_properties: t.ContainerMapping = Field(default_factory=dict)
            primary_keys: t.StrSequence = Field(default_factory=lambda: ["dn"])
            replication_key: str | None = None

            @model_validator(mode="after")
            def validate_required_fields(self) -> Self:
                """Validate stream name, filter, and primary keys."""
                if not self.name:
                    msg = "Stream name is required"
                    raise ValueError(msg)
                if not self.search_filter:
                    msg = "Search filter is required"
                    raise ValueError(msg)
                if self.primary_keys == []:
                    msg = "Primary keys cannot be empty list"
                    raise ValueError(msg)
                return self

        class LdapClientConfig(BaseModel):
            """Parameter t.NormalizedValue for LDAP client initialization."""

            host: str
            port: int = c.TapLdap.DEFAULT_PORT
            bind_dn: str | None = None
            password: str | None = None
            use_ssl: bool = False
            timeout: int = c.TapLdap.DEFAULT_SEARCH_TIMEOUT
            page_size: int = c.TapLdap.DEFAULT_PAGE_SIZE

        # ── Value Objects ────────────────────────────────────────────────────

        class LdapConnectionParams(FlextLdapModels.Value):
            """Parameters for establishing an LDAP connection."""

            host: t.NonEmptyStr
            base_dn: t.NonEmptyStr
            port: Annotated[t.PortNumber, Field(default=c.TapLdap.DEFAULT_PORT)]
            bind_dn: str | None = None
            bind_password: str | None = None
            use_ssl: bool = False
            timeout_seconds: Annotated[
                t.PositiveInt,
                Field(default=c.TapLdap.DEFAULT_SEARCH_TIMEOUT),
            ]
            page_size: Annotated[
                t.PositiveInt,
                Field(default=c.TapLdap.DEFAULT_PAGE_SIZE),
            ]
            max_retries: Annotated[t.RetryCount, Field(default=3)]

        class StreamCreationParams(FlextLdapModels.Value):
            """Parameters for creating an LDAP data stream."""

            stream_type: t.NonEmptyStr
            connection_id: t.NonEmptyStr
            search_filter: t.NonEmptyStr
            attributes: t.StrSequence | None = None
            tap_stream_id: str | None = None
            key_properties: t.StrSequence | None = None
            replication_method: str = "FULL_TABLE"
            replication_key: str | None = None

        # ── Entities ─────────────────────────────────────────────────────────

        class LdapConnection(FlextLdapModels.Entity):
            """LDAP connection entity with test status and error tracking."""

            host: t.NonEmptyStr
            port: t.PortNumber
            bind_dn: str | None = None
            password: str | None = None
            use_ssl: bool = False
            timeout: t.PositiveInt
            id: str = Field(default_factory=lambda: uuid4().hex)
            last_tested: datetime | None = None
            last_error: str | None = None

        class LdapStream(FlextLdapModels.Entity):
            """LDAP data stream with schema and replication configuration."""

            id: str = Field(default_factory=lambda: uuid4().hex)
            name: t.NonEmptyStr
            connection_id: t.NonEmptyStr
            stream_type: t.NonEmptyStr
            search_filter: t.NonEmptyStr
            attributes: t.StrSequence = Field(default_factory=list)
            tap_stream_id: t.NonEmptyStr
            key_properties: t.StrSequence = Field(default_factory=lambda: ["dn"])
            replication_method: str = "FULL_TABLE"
            replication_key: str | None = None
            stream_schema: t.ContainerMapping = Field(default_factory=dict)

            def update_schema(self, schema: t.ContainerMapping) -> None:
                """Update stream schema from mapping."""
                self.stream_schema = dict(schema)


# Runtime alias for simplified usage
m = FlextTapLdapModels

__all__ = [
    "FlextTapLdapModels",
    "m",
]
