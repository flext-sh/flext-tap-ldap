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

from pydantic import BaseModel, Field, model_validator

from flext_ldap import FlextLdapModels
from flext_meltano import FlextMeltanoModels
from flext_tap_ldap import c, t


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

            timestamp: datetime = Field(
                default_factory=lambda: datetime.now(UTC),
                description="Timestamp when tap execution started",
            )
            tap_name: str = Field(
                default="tap-ldap",
                description="Name of the LDAP tap",
            )
            execution_id: str = Field(
                default="",
                description="Unique execution identifier",
            )
            config_hash: str | None = Field(
                default=None,
                description="Hash of the effective execution configuration",
            )

        class TapExecutionCompletedEvent(FlextLdapModels.Event):
            """Event raised when tap execution completes."""

            timestamp: datetime = Field(
                default_factory=lambda: datetime.now(UTC),
                description="Timestamp when tap execution completed",
            )
            tap_name: str = Field(
                default="tap-ldap",
                description="Name of the LDAP tap",
            )
            execution_id: str = Field(
                default="",
                description="Unique execution identifier",
            )
            records_processed: int = Field(
                default=0,
                description="Total records processed during tap execution",
            )
            streams_discovered: int = Field(
                default=0,
                description="Number of streams discovered during execution",
            )
            duration_seconds: float = Field(
                default=0.0,
                description="Execution duration in seconds",
            )

        class StreamDiscoveredEvent(FlextLdapModels.Event):
            """Event raised when a stream is discovered."""

            event_type: Annotated[
                str,
                Field(
                    default="stream_discovered",
                    frozen=True,
                    description="Event type for discovered streams",
                ),
            ]
            aggregate_id: Annotated[
                str,
                Field(
                    default="",
                    description="Stream aggregate identifier derived from stream_name",
                ),
            ]
            stream_name: str = Field(
                description="Name of the discovered stream",
            )
            stream_key_properties: t.StrSequence = Field(
                default_factory=list,
                description="Primary key properties for the discovered stream",
            )
            bookmark_key: str | None = Field(
                default=None,
                description="Optional bookmark key used for incremental sync",
            )

            @model_validator(mode="before")
            @classmethod
            def populate_aggregate_id(
                cls,
                data: t.ContainerMapping,
            ) -> t.ContainerMapping:
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

            event_type: Annotated[
                str,
                Field(
                    default="record_extracted",
                    frozen=True,
                    description="Event type for record extraction",
                ),
            ]
            aggregate_id: Annotated[
                str,
                Field(
                    default="",
                    description="Stream name as aggregate identifier",
                ),
            ]
            stream_name: str = Field(
                description="Name of the stream associated with the extracted record",
            )
            record_id: str | None = Field(
                default=None,
                description="Identifier of the extracted record",
            )
            record_size_bytes: int = Field(
                default=0,
                description="Extracted record size in bytes",
            )

            @model_validator(mode="before")
            @classmethod
            def populate_aggregate_id(
                cls,
                data: t.ContainerMapping,
            ) -> t.ContainerMapping:
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

            id: str = Field(
                default_factory=lambda: uuid4().hex,
                description="Unique execution entity identifier",
            )
            execution_id: str = Field(
                description="Identifier for the associated tap execution",
            )
            connection_id: str = Field(
                description="Identifier for the associated LDAP connection",
            )
            command: str = Field(
                description="Command executed by the tap",
            )
            tap_status: str = Field(
                default="created",
                description="Current status of the tap execution",
            )
            settings: t.ContainerMapping = Field(
                default_factory=dict,
                description="Execution configuration object",
            )
            catalog: t.ContainerMapping = Field(
                default_factory=dict,
                description="Catalog data associated with the execution",
            )
            state: t.ContainerMapping = Field(
                default_factory=dict,
                description="State data for the execution",
            )
            started_at: datetime | None = Field(
                default=None,
                description="UTC timestamp when execution started",
            )
            completed_at: datetime | None = Field(
                default=None,
                description="UTC timestamp when execution completed",
            )
            records_extracted: int = Field(
                default=0,
                description="Number of records extracted during execution",
            )
            streams_processed: int = Field(
                default=0,
                description="Number of streams processed during execution",
            )
            exit_code: int | None = Field(
                default=None,
                description="Exit code returned by the execution",
            )
            stdout: str | None = Field(
                default=None,
                description="Standard output captured during execution",
            )
            stderr: str | None = Field(
                default=None,
                description="Standard error captured during execution",
            )

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

            event_type: Annotated[
                str,
                Field(
                    default="connection_tested",
                    frozen=True,
                    description="Event type for connection test results",
                ),
            ]
            aggregate_id: Annotated[
                str,
                Field(
                    default="",
                    description="Server URI used as aggregate identifier",
                ),
            ]
            success: bool = Field(
                description="Whether the connection test succeeded",
            )
            server_uri: str = Field(
                description="LDAP server URI used for the connection test",
            )
            error_message: str | None = Field(
                default=None,
                description="Optional error message when connection test fails",
            )

            @model_validator(mode="before")
            @classmethod
            def populate_aggregate_id(
                cls,
                data: t.ContainerMapping,
            ) -> t.ContainerMapping:
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
            """LDAP connection configuration extracted from tap settings."""

            host: str = Field(
                default="",
                description="LDAP server host name or address",
            )
            port: int = Field(
                default=c.Ldap.ConnectionDefaults.PORT,
                description="LDAP server port",
            )
            bind_dn: str | None = Field(
                default=None,
                description="Distinguished Name used to bind to LDAP",
            )
            bind_password: str | None = Field(
                default=None,
                description="Password used to bind to LDAP",
            )
            use_ssl: bool = Field(
                default=False,
                description="Whether to use LDAPS for the connection",
            )
            timeout_seconds: int = Field(
                default=c.TapLdap.DEFAULT_SEARCH_TIMEOUT,
                description="Timeout for LDAP operations in seconds",
            )
            base_dn: str = Field(
                default="",
                description="Base DN for LDAP searches",
            )

        class CustomPropertyDefinition(BaseModel):
            """Definition of a custom stream property."""

            type: str = Field(
                default="string",
                description="Data type for the custom stream property",
            )
            description: str | None = Field(
                default=None,
                description="Optional description of the custom property",
            )

        class CustomStreamParams(BaseModel):
            """Parameters for creating a custom LDAP stream."""

            name: str = Field(
                description="Name of the custom LDAP stream",
            )
            search_filter: str = Field(
                description="LDAP filter expression for the custom stream",
            )
            schema_properties: t.ContainerMapping = Field(
                default_factory=dict,
                description="Custom schema properties for the stream",
            )
            primary_keys: t.StrSequence = Field(
                default_factory=lambda: ["dn"],
                description="Primary key attributes for the custom stream",
            )
            replication_key: str | None = Field(
                default=None,
                description="Optional replication key for incremental processing",
            )

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

            host: str = Field(
                description="LDAP server host name or address",
            )
            port: int = Field(
                default=c.Ldap.ConnectionDefaults.PORT,
                description="LDAP server port",
            )
            bind_dn: str | None = Field(
                default=None,
                description="Bind Distinguished Name for LDAP operations",
            )
            password: str | None = Field(
                default=None,
                description="Password used for LDAP bind operations",
            )
            use_ssl: bool = Field(
                default=False,
                description="Whether to use SSL/TLS for the LDAP connection",
            )
            timeout: int = Field(
                default=c.TapLdap.DEFAULT_SEARCH_TIMEOUT,
                description="Timeout for LDAP client operations in seconds",
            )
            page_size: int = Field(
                default=c.TapLdap.DEFAULT_PAGE_SIZE,
                description="LDAP page size for search results",
            )

        # ── Value Objects ────────────────────────────────────────────────────

        class LdapConnectionParams(FlextLdapModels.Value):
            """Parameters for establishing an LDAP connection."""

            host: t.NonEmptyStr = Field(
                description="LDAP host to connect to",
            )
            base_dn: t.NonEmptyStr = Field(
                description="Base distinguished name for LDAP searches",
            )
            port: Annotated[
                t.PortNumber,
                Field(
                    default=c.Ldap.ConnectionDefaults.PORT,
                    description="LDAP port number",
                ),
            ]
            bind_dn: str | None = Field(
                default=None,
                description="Bind DN for LDAP connection",
            )
            bind_password: str | None = Field(
                default=None,
                description="Bind password for LDAP connection",
            )
            use_ssl: bool = Field(
                default=False,
                description="Whether to use SSL/TLS for the LDAP connection",
            )
            timeout_seconds: Annotated[
                t.PositiveInt,
                Field(
                    default=c.TapLdap.DEFAULT_SEARCH_TIMEOUT,
                    description="Timeout in seconds for LDAP operations",
                ),
            ]
            page_size: Annotated[
                t.PositiveInt,
                Field(
                    default=c.TapLdap.DEFAULT_PAGE_SIZE,
                    description="Page size used for LDAP searches",
                ),
            ]
            max_retries: Annotated[
                t.RetryCount,
                Field(
                    default=3,
                    description="Maximum retry attempts for LDAP operations",
                ),
            ]

        class StreamCreationParams(FlextLdapModels.Value):
            """Parameters for creating an LDAP data stream."""

            stream_type: t.NonEmptyStr = Field(
                description="Type of stream to create",
            )
            connection_id: t.NonEmptyStr = Field(
                description="Reference LDAP connection identifier",
            )
            search_filter: t.NonEmptyStr = Field(
                description="LDAP search filter for the stream",
            )
            attributes: t.StrSequence | None = Field(
                default=None,
                description="Attributes returned by the stream",
            )
            tap_stream_id: str | None = Field(
                default=None,
                description="Optional tap stream identifier",
            )
            key_properties: t.StrSequence | None = Field(
                default=None,
                description="Primary key properties for the stream",
            )
            replication_method: str = Field(
                default="FULL_TABLE",
                description="Replication method for the stream",
            )
            replication_key: str | None = Field(
                default=None,
                description="Optional replication key for incremental streams",
            )

        # ── Entities ─────────────────────────────────────────────────────────

        class LdapConnection(FlextLdapModels.Entity):
            """LDAP connection entity with test status and error tracking."""

            host: t.NonEmptyStr = Field(
                description="LDAP host address for this connection",
            )
            port: t.PortNumber = Field(
                description="LDAP port for this connection",
            )
            bind_dn: str | None = Field(
                default=None,
                description="Bind DN used by the connection",
            )
            password: str | None = Field(
                default=None,
                description="Bind password used by the connection",
            )
            use_ssl: bool = Field(
                default=False,
                description="Whether the connection uses SSL/TLS",
            )
            timeout: t.PositiveInt = Field(
                description="Timeout in seconds for this LDAP connection",
            )
            id: str = Field(
                default_factory=lambda: uuid4().hex,
                description="Unique identifier for this LDAP connection",
            )
            last_tested: datetime | None = Field(
                default=None,
                description="Timestamp when the connection was last tested",
            )
            last_error: str | None = Field(
                default=None,
                description="Latest error message from connection testing",
            )

        class LdapStream(FlextLdapModels.Entity):
            """LDAP data stream with schema and replication configuration."""

            id: str = Field(
                default_factory=lambda: uuid4().hex,
                description="Unique identifier for this stream",
            )
            name: t.NonEmptyStr = Field(
                description="Name of the LDAP stream",
            )
            connection_id: t.NonEmptyStr = Field(
                description="Identifier of the connection used by the stream",
            )
            stream_type: t.NonEmptyStr = Field(
                description="LDAP stream type",
            )
            search_filter: t.NonEmptyStr = Field(
                description="Search filter used by the stream",
            )
            attributes: t.StrSequence = Field(
                default_factory=list,
                description="Attributes included in the stream",
            )
            tap_stream_id: t.NonEmptyStr = Field(
                description="Identifier assigned to the tap stream",
            )
            key_properties: t.StrSequence = Field(
                default_factory=lambda: ["dn"],
                description="Primary key properties for the stream",
            )
            replication_method: str = Field(
                default="FULL_TABLE",
                description="Replication method for the stream",
            )
            replication_key: str | None = Field(
                default=None,
                description="Optional replication key for incremental replication",
            )
            stream_schema: t.ContainerMapping = Field(
                default_factory=dict,
                description="Stream schema mapping for Singer records",
            )

            def update_schema(self, schema: t.ContainerMapping) -> None:
                """Update stream schema from mapping."""
                self.stream_schema = dict(schema)


# Runtime alias for simplified usage
m = FlextTapLdapModels

__all__: list[str] = [
    "FlextTapLdapModels",
    "m",
]
