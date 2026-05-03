"""FLEXT Tap LDAP models - tap-specific events only.

Uses models from parent libraries (flext-ldap, flext-ldif).
Defines only tap-execution and event models specific to LDAP data extraction.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from datetime import UTC, datetime
from types import MappingProxyType
from typing import Annotated, Self
from uuid import uuid4

from flext_ldap import m
from flext_meltano import FlextMeltanoModels, u
from flext_tap_ldap.constants import c
from flext_tap_ldap.typings import t


class FlextTapLdapModels(FlextMeltanoModels, m):
    """Complete models for LDAP tap operations extending m.

    Provides standardized models for all LDAP tap domain entities including:
    - Singer stream metadata and configuration
    - LDAP table extraction configuration
    - Replication and discovery operations
    - Performance monitoring and metrics
    - Singer protocol compliance models

    All nested classes inherit m validation and patterns.
    """

    class TapLdap:
        """Tap LDAP namespace for cross-project access."""

        # ── Domain Events ────────────────────────────────────────────────────

        class TapExecution(m.Entity):
            """Execution state and metrics for a tap run."""

            id: str = u.Field(
                default_factory=lambda: uuid4().hex,
                description="Unique execution entity identifier",
            )
            execution_id: str = u.Field(
                description="Identifier for the associated tap execution",
            )
            connection_id: str = u.Field(
                description="Identifier for the associated LDAP connection",
            )
            command: str = u.Field(
                description="Command executed by the tap",
            )
            tap_status: Annotated[
                str,
                u.Field(
                    description="Current status of the tap execution",
                ),
            ] = "created"
            settings: t.JsonMapping = u.Field(
                default_factory=lambda: MappingProxyType({}),
                description="Execution configuration object",
            )
            catalog: t.JsonMapping = u.Field(
                default_factory=lambda: MappingProxyType({}),
                description="Catalog data associated with the execution",
            )
            state: t.JsonMapping = u.Field(
                default_factory=lambda: MappingProxyType({}),
                description="State data for the execution",
            )
            started_at: Annotated[
                datetime | None,
                u.Field(
                    description="UTC timestamp when execution started",
                ),
            ] = None
            completed_at: Annotated[
                datetime | None,
                u.Field(
                    description="UTC timestamp when execution completed",
                ),
            ] = None
            records_extracted: Annotated[
                int,
                u.Field(
                    description="Number of records extracted during execution",
                ),
            ] = 0
            streams_processed: Annotated[
                int,
                u.Field(
                    description="Number of streams processed during execution",
                ),
            ] = 0
            exit_code: Annotated[
                int | None,
                u.Field(
                    description="Exit code returned by the execution",
                ),
            ] = None
            stdout: Annotated[
                str | None,
                u.Field(
                    description="Standard output captured during execution",
                ),
            ] = None
            stderr: Annotated[
                str | None,
                u.Field(
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

        # ── Config Parameter Objects ─────────────────────────────────────────

        class CustomPropertyDefinition(m.BaseModel):
            """Definition of a custom stream property."""

            type: Annotated[
                str,
                u.Field(
                    description="Data type for the custom stream property",
                ),
            ] = "string"
            description: Annotated[
                str | None,
                u.Field(
                    description="Optional description of the custom property",
                ),
            ] = None

        class CustomStreamParams(m.BaseModel):
            """Parameters for creating a custom LDAP stream."""

            name: str = u.Field(
                description="Name of the custom LDAP stream",
            )
            search_filter: str = u.Field(
                description="LDAP filter expression for the custom stream",
            )
            schema_properties: t.JsonMapping = u.Field(
                default_factory=lambda: MappingProxyType({}),
                description="Custom schema properties for the stream",
            )
            primary_keys: t.StrSequence = u.Field(
                default_factory=lambda: ["dn"],
                description="Primary key attributes for the custom stream",
            )
            replication_key: Annotated[
                str | None,
                u.Field(
                    description="Optional replication key for incremental processing",
                ),
            ] = None

            @u.model_validator(mode="after")
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

        class StreamCreationParams(m.Value):
            """Parameters for creating an LDAP data stream."""

            stream_type: t.NonEmptyStr = u.Field(
                description="Type of stream to create",
            )
            connection_id: t.NonEmptyStr = u.Field(
                description="Reference LDAP connection identifier",
            )
            search_filter: t.NonEmptyStr = u.Field(
                description="LDAP search filter for the stream",
            )
            attributes: Annotated[
                t.StrSequence | None,
                u.Field(
                    description="Attributes returned by the stream",
                ),
            ] = None
            tap_stream_id: Annotated[
                str | None,
                u.Field(
                    description="Optional tap stream identifier",
                ),
            ] = None
            key_properties: Annotated[
                t.StrSequence | None,
                u.Field(
                    description="Primary key properties for the stream",
                ),
            ] = None
            replication_method: Annotated[
                str,
                u.Field(
                    description="Replication method for the stream",
                ),
            ] = "FULL_TABLE"
            replication_key: Annotated[
                str | None,
                u.Field(
                    description="Optional replication key for incremental streams",
                ),
            ] = None

        # ── Entities ─────────────────────────────────────────────────────────

        class LdapConnectionParams(m.Value):
            """LDAP connection parameters for tap configuration."""

            host: t.NonEmptyStr = u.Field(description="LDAP server hostname")
            port: t.PortNumber = u.Field(description="LDAP server port")
            bind_dn: Annotated[
                str | None,
                u.Field(description="Bind DN for authentication"),
            ] = None
            bind_password: Annotated[
                str | None,
                u.Field(description="Bind password for authentication"),
            ] = None
            base_dn: Annotated[
                str | None,
                u.Field(description="Base DN for search operations"),
            ] = None
            use_ssl: bool = u.Field(description="Enable SSL")
            timeout_seconds: t.PositiveInt = u.Field(
                description="Search timeout in seconds",
            )
            page_size: Annotated[
                t.PositiveInt,
                u.Field(
                    default=c.TapLdap.DEFAULT_PAGE_SIZE,
                    description="Page size for paged results",
                ),
            ]
            max_retries: Annotated[
                t.PositiveInt,
                u.Field(
                    default=3,
                    description="Maximum connection retries",
                ),
            ]

        class LdapConnection(m.Entity):
            """LDAP connection entity with test status and error tracking."""

            host: t.NonEmptyStr = u.Field(
                description="LDAP host address for this connection",
            )
            port: t.PortNumber = u.Field(
                description="LDAP port for this connection",
            )
            bind_dn: Annotated[
                str | None,
                u.Field(
                    description="Bind DN used by the connection",
                ),
            ] = None
            password: Annotated[
                str | None,
                u.Field(
                    description="Bind password used by the connection",
                ),
            ] = None
            use_ssl: Annotated[
                bool,
                u.Field(
                    description="Whether the connection uses SSL/TLS",
                ),
            ] = False
            timeout: t.PositiveInt = u.Field(
                description="Timeout in seconds for this LDAP connection",
            )
            id: str = u.Field(
                default_factory=lambda: uuid4().hex,
                description="Unique identifier for this LDAP connection",
            )
            last_tested: Annotated[
                datetime | None,
                u.Field(
                    description="Timestamp when the connection was last tested",
                ),
            ] = None
            last_error: Annotated[
                str | None,
                u.Field(
                    description="Latest error message from connection testing",
                ),
            ] = None

        class LdapStream(m.Entity):
            """LDAP data stream with schema and replication configuration."""

            id: str = u.Field(
                default_factory=lambda: uuid4().hex,
                description="Unique identifier for this stream",
            )
            name: t.NonEmptyStr = u.Field(
                description="Name of the LDAP stream",
            )
            connection_id: t.NonEmptyStr = u.Field(
                description="Identifier of the connection used by the stream",
            )
            stream_type: t.NonEmptyStr = u.Field(
                description="LDAP stream type",
            )
            search_filter: t.NonEmptyStr = u.Field(
                description="Search filter used by the stream",
            )
            attributes: t.StrSequence = u.Field(
                default_factory=tuple,
                description="Attributes included in the stream",
            )
            tap_stream_id: t.NonEmptyStr = u.Field(
                description="Identifier assigned to the tap stream",
            )
            key_properties: t.StrSequence = u.Field(
                default_factory=lambda: ["dn"],
                description="Primary key properties for the stream",
            )
            replication_method: Annotated[
                str,
                u.Field(
                    description="Replication method for the stream",
                ),
            ] = "FULL_TABLE"
            replication_key: Annotated[
                str | None,
                u.Field(
                    description="Optional replication key for incremental replication",
                ),
            ] = None
            stream_schema: t.JsonMapping = u.Field(
                default_factory=lambda: MappingProxyType({}),
                description="Stream schema mapping for Singer records",
            )

            def update_schema(self, schema: t.JsonMapping) -> None:
                """Update stream schema from mapping."""
                self.stream_schema = dict(schema)


# Runtime alias for simplified usage
m = FlextTapLdapModels

__all__: list[str] = [
    "FlextTapLdapModels",
    "m",
]
