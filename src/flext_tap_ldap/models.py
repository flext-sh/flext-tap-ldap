"""FLEXT Tap LDAP models - tap-specific events only.

Uses models from parent libraries (flext-ldap, flext-ldif).
Defines only tap-execution and event models specific to LDAP data extraction.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Annotated, Self
from uuid import uuid4

from pydantic import model_validator

from flext_ldap import FlextLdapModels
from flext_meltano import FlextMeltanoModels
from flext_tap_ldap import c, m

if TYPE_CHECKING:
    from flext_tap_ldap import t


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

            timestamp: datetime = m.Field(
                default_factory=lambda: datetime.now(UTC),
                description="Timestamp when tap execution started",
            )
            tap_name: Annotated[
                str,
                m.Field(
                    description="Name of the LDAP tap",
                ),
            ] = "tap-ldap"
            execution_id: Annotated[
                str,
                m.Field(
                    description="Unique execution identifier",
                ),
            ] = ""
            config_hash: Annotated[
                str | None,
                m.Field(
                    description="Hash of the effective execution configuration",
                ),
            ] = None

        class TapExecutionCompletedEvent(FlextLdapModels.Event):
            """Event raised when tap execution completes."""

            timestamp: datetime = m.Field(
                default_factory=lambda: datetime.now(UTC),
                description="Timestamp when tap execution completed",
            )
            tap_name: Annotated[
                str,
                m.Field(
                    description="Name of the LDAP tap",
                ),
            ] = "tap-ldap"
            execution_id: Annotated[
                str,
                m.Field(
                    description="Unique execution identifier",
                ),
            ] = ""
            records_processed: Annotated[
                int,
                m.Field(
                    description="Total records processed during tap execution",
                ),
            ] = 0
            streams_discovered: Annotated[
                int,
                m.Field(
                    description="Number of streams discovered during execution",
                ),
            ] = 0
            duration_seconds: Annotated[
                float,
                m.Field(
                    description="Execution duration in seconds",
                ),
            ] = 0.0

        class StreamDiscoveredEvent(FlextLdapModels.Event):
            """Event raised when a stream is discovered."""

            event_type: Annotated[
                str,
                m.Field(
                    frozen=True,
                    description="Event type for discovered streams",
                ),
            ] = "stream_discovered"
            aggregate_id: Annotated[
                str,
                m.Field(
                    description="Stream aggregate identifier derived from stream_name",
                ),
            ] = ""
            stream_name: str = m.Field(
                description="Name of the discovered stream",
            )
            stream_key_properties: t.StrSequence = m.Field(
                default_factory=list,
                description="Primary key properties for the discovered stream",
            )
            bookmark_key: Annotated[
                str | None,
                m.Field(
                    description="Optional bookmark key used for incremental sync",
                ),
            ] = None

            @model_validator(mode="before")
            @classmethod
            def populate_aggregate_id(
                cls,
                data: t.RecursiveContainerMapping,
            ) -> t.RecursiveContainerMapping:
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
                m.Field(
                    frozen=True,
                    description="Event type for record extraction",
                ),
            ] = "record_extracted"
            aggregate_id: Annotated[
                str,
                m.Field(
                    description="Stream name as aggregate identifier",
                ),
            ] = ""
            stream_name: str = m.Field(
                description="Name of the stream associated with the extracted record",
            )
            record_id: Annotated[
                str | None,
                m.Field(
                    description="Identifier of the extracted record",
                ),
            ] = None
            record_size_bytes: Annotated[
                int,
                m.Field(
                    description="Extracted record size in bytes",
                ),
            ] = 0

            @model_validator(mode="before")
            @classmethod
            def populate_aggregate_id(
                cls,
                data: t.RecursiveContainerMapping,
            ) -> t.RecursiveContainerMapping:
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

            id: str = m.Field(
                default_factory=lambda: uuid4().hex,
                description="Unique execution entity identifier",
            )
            execution_id: str = m.Field(
                description="Identifier for the associated tap execution",
            )
            connection_id: str = m.Field(
                description="Identifier for the associated LDAP connection",
            )
            command: str = m.Field(
                description="Command executed by the tap",
            )
            tap_status: Annotated[
                str,
                m.Field(
                    description="Current status of the tap execution",
                ),
            ] = "created"
            settings: t.RecursiveContainerMapping = m.Field(
                default_factory=dict,
                description="Execution configuration object",
            )
            catalog: t.RecursiveContainerMapping = m.Field(
                default_factory=dict,
                description="Catalog data associated with the execution",
            )
            state: t.RecursiveContainerMapping = m.Field(
                default_factory=dict,
                description="State data for the execution",
            )
            started_at: Annotated[
                datetime | None,
                m.Field(
                    description="UTC timestamp when execution started",
                ),
            ] = None
            completed_at: Annotated[
                datetime | None,
                m.Field(
                    description="UTC timestamp when execution completed",
                ),
            ] = None
            records_extracted: Annotated[
                int,
                m.Field(
                    description="Number of records extracted during execution",
                ),
            ] = 0
            streams_processed: Annotated[
                int,
                m.Field(
                    description="Number of streams processed during execution",
                ),
            ] = 0
            exit_code: Annotated[
                int | None,
                m.Field(
                    description="Exit code returned by the execution",
                ),
            ] = None
            stdout: Annotated[
                str | None,
                m.Field(
                    description="Standard output captured during execution",
                ),
            ] = None
            stderr: Annotated[
                str | None,
                m.Field(
                    description="Standard error captured during execution",
                ),
            ] = None

            def start_execution(self) -> None:
                """Mark execution as running with current timestamp."""
                self.tap_status = c.TapLdap.TapStatus.RUNNING.value
                self.started_at = datetime.now(UTC)

            def complete_execution(
                self,
                exit_code: int,
                stdout: str | None = None,
                stderr: str | None = None,
            ) -> None:
                """Mark execution as completed with exit code and output."""
                self.tap_status = (
                    c.TapLdap.TapStatus.COMPLETED.value
                    if exit_code == 0
                    else c.TapLdap.TapStatus.FAILED.value
                )
                self.completed_at = datetime.now(UTC)
                self.exit_code = exit_code
                self.stdout = stdout
                self.stderr = stderr

            def cancel_execution(self) -> None:
                """Mark execution as cancelled."""
                self.tap_status = c.TapLdap.TapStatus.CANCELLED.value
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
                m.Field(
                    frozen=True,
                    description="Event type for connection test results",
                ),
            ] = "connection_tested"
            aggregate_id: Annotated[
                str,
                m.Field(
                    description="Server URI used as aggregate identifier",
                ),
            ] = ""
            success: bool = m.Field(
                description="Whether the connection test succeeded",
            )
            server_uri: str = m.Field(
                description="LDAP server URI used for the connection test",
            )
            error_message: Annotated[
                str | None,
                m.Field(
                    description="Optional error message when connection test fails",
                ),
            ] = None

            @model_validator(mode="before")
            @classmethod
            def populate_aggregate_id(
                cls,
                data: t.RecursiveContainerMapping,
            ) -> t.RecursiveContainerMapping:
                """Set aggregate_id from server_uri if not provided."""
                if (
                    isinstance(data, dict)
                    and "aggregate_id" not in data
                    and "server_uri" in data
                ):
                    data["aggregate_id"] = data["server_uri"]
                return data

        # ── Config Parameter Objects ─────────────────────────────────────────

        class LdapConnectionConfig(m.BaseModel):
            """LDAP connection configuration extracted from tap settings."""

            host: Annotated[
                str,
                m.Field(
                    description="LDAP server host name or address",
                ),
            ] = ""
            port: Annotated[
                int,
                m.Field(
                    description="LDAP server port",
                ),
            ] = c.Ldap.ConnectionDefaults.PORT
            bind_dn: Annotated[
                str | None,
                m.Field(
                    description="Distinguished Name used to bind to LDAP",
                ),
            ] = None
            bind_password: Annotated[
                str | None,
                m.Field(
                    description="Password used to bind to LDAP",
                ),
            ] = None
            use_ssl: Annotated[
                bool,
                m.Field(
                    description="Whether to use LDAPS for the connection",
                ),
            ] = False
            timeout_seconds: Annotated[
                int,
                m.Field(
                    description="Timeout for LDAP operations in seconds",
                ),
            ] = c.TapLdap.DEFAULT_SEARCH_TIMEOUT
            base_dn: Annotated[
                str,
                m.Field(
                    description="Base DN for LDAP searches",
                ),
            ] = ""

        class CustomPropertyDefinition(m.BaseModel):
            """Definition of a custom stream property."""

            type: Annotated[
                str,
                m.Field(
                    description="Data type for the custom stream property",
                ),
            ] = "string"
            description: Annotated[
                str | None,
                m.Field(
                    description="Optional description of the custom property",
                ),
            ] = None

        class CustomStreamParams(m.BaseModel):
            """Parameters for creating a custom LDAP stream."""

            name: str = m.Field(
                description="Name of the custom LDAP stream",
            )
            search_filter: str = m.Field(
                description="LDAP filter expression for the custom stream",
            )
            schema_properties: t.RecursiveContainerMapping = m.Field(
                default_factory=dict,
                description="Custom schema properties for the stream",
            )
            primary_keys: t.StrSequence = m.Field(
                default_factory=lambda: ["dn"],
                description="Primary key attributes for the custom stream",
            )
            replication_key: Annotated[
                str | None,
                m.Field(
                    description="Optional replication key for incremental processing",
                ),
            ] = None

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

        class LdapClientConfig(m.BaseModel):
            """Parameter t.RecursiveContainer for LDAP client initialization."""

            host: str = m.Field(
                description="LDAP server host name or address",
            )
            port: Annotated[
                int,
                m.Field(
                    description="LDAP server port",
                ),
            ] = c.Ldap.ConnectionDefaults.PORT
            bind_dn: Annotated[
                str | None,
                m.Field(
                    description="Bind Distinguished Name for LDAP operations",
                ),
            ] = None
            password: Annotated[
                str | None,
                m.Field(
                    description="Password used for LDAP bind operations",
                ),
            ] = None
            use_ssl: Annotated[
                bool,
                m.Field(
                    description="Whether to use SSL/TLS for the LDAP connection",
                ),
            ] = False
            timeout: Annotated[
                int,
                m.Field(
                    description="Timeout for LDAP client operations in seconds",
                ),
            ] = c.TapLdap.DEFAULT_SEARCH_TIMEOUT
            page_size: Annotated[
                int,
                m.Field(
                    description="LDAP page size for search results",
                ),
            ] = c.TapLdap.DEFAULT_PAGE_SIZE

        # ── Value Objects ────────────────────────────────────────────────────

        class LdapConnectionParams(FlextLdapModels.Value):
            """Parameters for establishing an LDAP connection."""

            host: t.NonEmptyStr = m.Field(
                description="LDAP host to connect to",
            )
            base_dn: t.NonEmptyStr = m.Field(
                description="Base distinguished name for LDAP searches",
            )
            port: Annotated[
                t.PortNumber,
                m.Field(
                    description="LDAP port number",
                ),
            ] = c.Ldap.ConnectionDefaults.PORT
            bind_dn: Annotated[
                str | None,
                m.Field(
                    description="Bind DN for LDAP connection",
                ),
            ] = None
            bind_password: Annotated[
                str | None,
                m.Field(
                    description="Bind password for LDAP connection",
                ),
            ] = None
            use_ssl: Annotated[
                bool,
                m.Field(
                    description="Whether to use SSL/TLS for the LDAP connection",
                ),
            ] = False
            timeout_seconds: Annotated[
                t.PositiveInt,
                m.Field(
                    description="Timeout in seconds for LDAP operations",
                ),
            ] = c.TapLdap.DEFAULT_SEARCH_TIMEOUT
            page_size: Annotated[
                t.PositiveInt,
                m.Field(
                    description="Page size used for LDAP searches",
                ),
            ] = c.TapLdap.DEFAULT_PAGE_SIZE
            max_retries: Annotated[
                t.RetryCount,
                m.Field(
                    description="Maximum retry attempts for LDAP operations",
                ),
            ] = 3

        class StreamCreationParams(FlextLdapModels.Value):
            """Parameters for creating an LDAP data stream."""

            stream_type: t.NonEmptyStr = m.Field(
                description="Type of stream to create",
            )
            connection_id: t.NonEmptyStr = m.Field(
                description="Reference LDAP connection identifier",
            )
            search_filter: t.NonEmptyStr = m.Field(
                description="LDAP search filter for the stream",
            )
            attributes: Annotated[
                t.StrSequence | None,
                m.Field(
                    description="Attributes returned by the stream",
                ),
            ] = None
            tap_stream_id: Annotated[
                str | None,
                m.Field(
                    description="Optional tap stream identifier",
                ),
            ] = None
            key_properties: Annotated[
                t.StrSequence | None,
                m.Field(
                    description="Primary key properties for the stream",
                ),
            ] = None
            replication_method: Annotated[
                str,
                m.Field(
                    description="Replication method for the stream",
                ),
            ] = "FULL_TABLE"
            replication_key: Annotated[
                str | None,
                m.Field(
                    description="Optional replication key for incremental streams",
                ),
            ] = None

        # ── Entities ─────────────────────────────────────────────────────────

        class LdapConnection(FlextLdapModels.Entity):
            """LDAP connection entity with test status and error tracking."""

            host: t.NonEmptyStr = m.Field(
                description="LDAP host address for this connection",
            )
            port: t.PortNumber = m.Field(
                description="LDAP port for this connection",
            )
            bind_dn: Annotated[
                str | None,
                m.Field(
                    description="Bind DN used by the connection",
                ),
            ] = None
            password: Annotated[
                str | None,
                m.Field(
                    description="Bind password used by the connection",
                ),
            ] = None
            use_ssl: Annotated[
                bool,
                m.Field(
                    description="Whether the connection uses SSL/TLS",
                ),
            ] = False
            timeout: t.PositiveInt = m.Field(
                description="Timeout in seconds for this LDAP connection",
            )
            id: str = m.Field(
                default_factory=lambda: uuid4().hex,
                description="Unique identifier for this LDAP connection",
            )
            last_tested: Annotated[
                datetime | None,
                m.Field(
                    description="Timestamp when the connection was last tested",
                ),
            ] = None
            last_error: Annotated[
                str | None,
                m.Field(
                    description="Latest error message from connection testing",
                ),
            ] = None

        class LdapStream(FlextLdapModels.Entity):
            """LDAP data stream with schema and replication configuration."""

            id: str = m.Field(
                default_factory=lambda: uuid4().hex,
                description="Unique identifier for this stream",
            )
            name: t.NonEmptyStr = m.Field(
                description="Name of the LDAP stream",
            )
            connection_id: t.NonEmptyStr = m.Field(
                description="Identifier of the connection used by the stream",
            )
            stream_type: t.NonEmptyStr = m.Field(
                description="LDAP stream type",
            )
            search_filter: t.NonEmptyStr = m.Field(
                description="Search filter used by the stream",
            )
            attributes: t.StrSequence = m.Field(
                default_factory=list,
                description="Attributes included in the stream",
            )
            tap_stream_id: t.NonEmptyStr = m.Field(
                description="Identifier assigned to the tap stream",
            )
            key_properties: t.StrSequence = m.Field(
                default_factory=lambda: ["dn"],
                description="Primary key properties for the stream",
            )
            replication_method: Annotated[
                str,
                m.Field(
                    description="Replication method for the stream",
                ),
            ] = "FULL_TABLE"
            replication_key: Annotated[
                str | None,
                m.Field(
                    description="Optional replication key for incremental replication",
                ),
            ] = None
            stream_schema: t.RecursiveContainerMapping = m.Field(
                default_factory=dict,
                description="Stream schema mapping for Singer records",
            )

            def update_schema(self, schema: t.RecursiveContainerMapping) -> None:
                """Update stream schema from mapping."""
                self.stream_schema = dict(schema)


# Runtime alias for simplified usage
m = FlextTapLdapModels

__all__: list[str] = [
    "FlextTapLdapModels",
    "m",
]
