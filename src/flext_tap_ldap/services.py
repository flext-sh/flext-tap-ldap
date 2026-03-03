"""Services for FLEXT Tap LDAP operations and utilities.

Consolidates application services, LDIF processing, and simple API utilities
with maximum integration to flext-core, flext-ldap, and flext-ldif libraries.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from flext_core import FlextLogger, FlextResult, t
from flext_ldif import FlextLdif, FlextLdifModels
from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, ValidationError

from flext_tap_ldap.constants import c
from flext_tap_ldap.settings import FlextTapLdapSettings

logger = FlextLogger(__name__)

_LIST_ADAPTER = TypeAdapter(list[t.ContainerValue], config=ConfigDict(strict=True))
_MAP_ADAPTER = TypeAdapter(
    t.ConfigurationMapping,
    config=ConfigDict(strict=True),
)
_STR_ADAPTER = TypeAdapter(str, config=ConfigDict(strict=True))


def _as_list(value: t.ContainerValue) -> list[t.ContainerValue] | None:
    try:
        return _LIST_ADAPTER.validate_python(value)
    except ValidationError:
        return None


def _as_map(value: t.ContainerValue) -> Mapping[str, t.ContainerValue] | None:
    try:
        return _MAP_ADAPTER.validate_python(value)
    except ValidationError:
        return None


def _as_str(value: t.ContainerValue) -> str | None:
    try:
        return _STR_ADAPTER.validate_python(value)
    except ValidationError:
        return None


class LDAPConnection(BaseModel):
    """LDAP connection model."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(default_factory=lambda: str(uuid4()), description="Connection ID")
    host: str = Field(default="", description="LDAP host")
    port: int = Field(default=c.TapLdap.DEFAULT_PORT, description="LDAP port")
    bind_dn: str | None = Field(default=None, description="Bind DN")
    password: str | None = Field(default=None, description="Bind password")
    use_ssl: bool = Field(default=False, description="Use SSL")
    timeout: int = Field(
        default=c.TapLdap.DEFAULT_SEARCH_TIMEOUT,
        description="Connection timeout",
    )
    last_tested: datetime | None = Field(default=None, description="Last test time")
    last_error: str | None = Field(default=None, description="Last error message")


class LDAPStream(BaseModel):
    """LDAP stream model."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(default_factory=lambda: str(uuid4()), description="Stream ID")
    name: str = Field(default="", description="Stream name")
    connection_id: str = Field(default="", description="Connection ID")
    stream_type: str = Field(default="", description="Stream type")
    search_filter: str = Field(default="", description="LDAP search filter")
    attributes: list[str] = Field(default_factory=list, description="LDAP attributes")
    tap_stream_id: str = Field(default="", description="Tap stream ID")
    key_properties: list[str] = Field(
        default_factory=lambda: ["dn"],
        description="Key properties",
    )
    replication_method: str = Field(
        default="FULL_TABLE",
        description="Replication method",
    )
    replication_key: str | None = Field(default=None, description="Replication key")
    stream_schema: dict[str, t.ContainerValue] = Field(
        default_factory=dict,
        description="Stream schema",
    )

    def update_schema(self, schema: Mapping[str, t.ContainerValue]) -> None:
        """Update stream schema."""
        self.stream_schema = dict(schema)


class TapExecution(BaseModel):
    """Tap execution model."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(default_factory=lambda: str(uuid4()), description="Execution ID")
    execution_id: str = Field(default="", description="Execution identifier")
    connection_id: str = Field(default="", description="Connection ID")
    command: str = Field(default="", description="Command executed")
    tap_status: str = Field(default="created", description="Tap status")
    config: dict[str, t.ContainerValue] = Field(
        default_factory=dict,
        description="Configuration",
    )
    catalog: dict[str, t.ContainerValue] = Field(
        default_factory=dict,
        description="Catalog",
    )
    state: dict[str, t.ContainerValue] = Field(
        default_factory=dict,
        description="State",
    )
    started_at: datetime | None = Field(default=None, description="Start time")
    completed_at: datetime | None = Field(default=None, description="Completion time")
    exit_code: int | None = Field(default=None, description="Exit code")
    stdout: str | None = Field(default=None, description="Standard output")
    stderr: str | None = Field(default=None, description="Standard error")
    records_extracted: int = Field(default=0, description="Records extracted")
    streams_processed: int = Field(default=0, description="Streams processed")

    def start_execution(self) -> None:
        """Mark execution as started."""
        self.tap_status = "discovering"
        self.started_at = datetime.now(UTC)

    def complete_execution(
        self,
        exit_code: int,
        stdout: str | None = None,
        stderr: str | None = None,
    ) -> None:
        """Mark execution as completed."""
        self.tap_status = "completed" if exit_code == 0 else "failed"
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr
        self.completed_at = datetime.now(UTC)

    def cancel_execution(self) -> None:
        """Mark execution as cancelled."""
        self.tap_status = "cancelled"
        self.completed_at = datetime.now(UTC)

    def update_metrics(self, records_extracted: int, streams_processed: int) -> None:
        """Update execution metrics."""
        self.records_extracted = records_extracted
        self.streams_processed = streams_processed


class FlextTapLdapServices:
    """Unified services class for LDAP tap operations with complete service management.

    This class consolidates all LDAP tap services including connection management,
    stream processing, record handling, and LDIF processing following the unified
    class pattern with Clean Architecture and Domain-Driven Design.

    Contains all service classes and utility functions as nested classes and methods
    to maintain single responsibility while providing complete LDAP/LDIF
    data extraction and processing capabilities.
    """

    # Constants
    EXPECTED_DATA_COUNT = 3

    class LDAPConnectionParams(BaseModel):
        """Parameter object for LDAP connection configuration.

        Implements Parameter Object Pattern to reduce parameter count
        and improve maintainability
        """

        model_config = ConfigDict(extra="forbid")

        host: str = Field(description="LDAP host")
        base_dn: str = Field(description="Base DN")
        port: int = Field(
            default=c.TapLdap.DEFAULT_PORT,
            ge=1,
            le=c.TapLdap.Ldap.MAX_PORT,
            description="LDAP port",
        )
        use_ssl: bool = Field(default=False, description="Use SSL")
        bind_dn: str | None = Field(default=None, description="Bind DN")
        bind_password: str | None = Field(default=None, description="Bind password")
        timeout_seconds: int = Field(
            default=c.TapLdap.DEFAULT_SEARCH_TIMEOUT,
            gt=0,
            description="Timeout in seconds",
        )
        page_size: int = Field(
            default=c.TapLdap.DEFAULT_PAGE_SIZE,
            gt=0,
            description="Page size",
        )
        max_retries: int = Field(default=3, ge=0, description="Max retries")

    class StreamCreationParams(BaseModel):
        """Parameter object for LDAP stream creation.

        Implements Parameter Object Pattern to reduce parameter count in create_stream method
        following SOLID principles for better maintainability.
        """

        model_config = ConfigDict(extra="forbid")

        connection_id: str = Field(description="Connection ID")
        stream_type: str = Field(description="Stream type")
        search_filter: str = Field(description="Search filter")
        attributes: list[str] | None = Field(
            default=None,
            description="LDAP attributes",
        )
        tap_stream_id: str | None = Field(default=None, description="Tap stream ID")
        key_properties: list[str] | None = Field(
            default=None,
            description="Key properties",
        )
        replication_method: str = Field(
            default="FULL_TABLE",
            description="Replication method",
        )
        replication_key: str | None = Field(default=None, description="Replication key")

    class LDIFConfigBuilder(BaseModel):
        """Builder for LDIF processing configuration.

        Implements Builder Pattern to eliminate parameter proliferation
        following Interface Segregation Principle.
        """

        model_config = ConfigDict(extra="forbid")

        ldif_files: list[str] = Field(default_factory=list, description="LDIF files")
        ldif_directory: str | None = Field(default=None, description="LDIF directory")
        ldif_file_pattern: str = Field(default="*.ldif", description="File pattern")
        ldif_ignore_errors: bool = Field(default=True, description="Ignore errors")
        ldif_max_errors: int = Field(default=100, description="Max errors")
        ldif_ignore_file_errors: bool = Field(
            default=True,
            description="Ignore file errors",
        )
        ldif_ignore_entry_errors: bool = Field(
            default=True,
            description="Ignore entry errors",
        )
        ldif_apply_transformations: bool = Field(
            default=False,
            description="Apply transformations",
        )
        ldif_transformation_rules: dict[str, t.ContainerValue] = Field(
            default_factory=dict,
            description="Transformation rules",
        )
        migration_batch: str | None = Field(default=None, description="Migration batch")
        enable_ldif_streams: bool = Field(
            default=False,
            description="Enable LDIF streams",
        )

    class LDAPConnectionService:
        """Service for managing LDAP connections with flext-core patterns."""

        def __init__(self) -> None:
            """Initialize the connection service."""
            self._connections: dict[str, LDAPConnection] = {}

        def create_connection(
            self,
            params: FlextTapLdapServices.LDAPConnectionParams,
        ) -> FlextResult[LDAPConnection]:
            """Create LDAP connection using parameter object pattern."""
            try:
                # Parameter Object Pattern eliminates complex parameter passing
                connection = LDAPConnection(
                    host=params.host,
                    port=params.port,
                    bind_dn=params.bind_dn,
                    password=params.bind_password,
                    use_ssl=params.use_ssl,
                    timeout=params.timeout_seconds,
                )

                self._connections[str(connection.id)] = connection
                return FlextResult[LDAPConnection].ok(connection)
            except (RuntimeError, ValueError, TypeError) as e:
                return FlextResult[LDAPConnection].fail(
                    f"Failed to create connection: {e}",
                )

        def test_connection(
            self,
            connection_id: str,
        ) -> FlextResult[Mapping[str, t.ContainerValue]]:
            """Test LDAP connection."""
            try:
                connection = self._connections.get(connection_id)
                if not connection:
                    return FlextResult[t.ConfigurationMapping].fail(
                        "Connection not found",
                    )

                # Simulate test by marking last_tested and clearing last_error
                connection.last_tested = datetime.now(UTC)
                connection.last_error = None
                self._connections[connection_id] = connection

                return FlextResult[t.ConfigurationMapping].ok({
                    "success": True,
                    "connection": connection.id,
                })
            except (RuntimeError, ValueError, TypeError) as e:
                connection = self._connections.get(connection_id)
                if connection:
                    connection.last_tested = datetime.now(UTC)
                    connection.last_error = str(e)
                    self._connections[connection_id] = connection
                return FlextResult[t.ConfigurationMapping].fail(
                    f"Failed to test connection: {e}",
                )

        def get_connection(
            self,
            connection_id: str,
        ) -> FlextResult[LDAPConnection]:
            """Get LDAP connection by ID."""
            try:
                connection = self._connections.get(connection_id)
                if not connection:
                    return FlextResult[LDAPConnection].fail("Connection not found")
                return FlextResult[LDAPConnection].ok(connection)
            except (RuntimeError, ValueError, TypeError) as e:
                return FlextResult[LDAPConnection].fail(
                    f"Failed to get connection: {e}",
                )

        def list_connections(self) -> FlextResult[list[LDAPConnection]]:
            """List all LDAP connections."""
            try:
                connections = list(self._connections.values())
                return FlextResult[list[LDAPConnection]].ok(connections)
            except (RuntimeError, ValueError, TypeError) as e:
                return FlextResult[list[LDAPConnection]].fail(
                    f"Failed to list connections: {e}",
                )

    class LDAPStreamService:
        """Service for managing LDAP streams with flext-core patterns."""

        def __init__(self) -> None:
            """Initialize the stream service."""
            self._streams: dict[str, LDAPStream] = {}

        def create_stream(
            self,
            params: FlextTapLdapServices.StreamCreationParams,
        ) -> FlextResult[LDAPStream]:
            """Create LDAP stream using parameter object pattern."""
            try:
                # Generate tap_stream_id if not provided
                tap_stream_id = params.tap_stream_id
                if not tap_stream_id:
                    tap_stream_id = f"{params.stream_type.lower()}_stream"

                # Create stream using the correct model
                stream = LDAPStream(
                    name=params.stream_type.lower(),
                    connection_id=params.connection_id,
                    stream_type=params.stream_type.lower(),
                    search_filter=params.search_filter,
                    attributes=params.attributes or [],
                    tap_stream_id=tap_stream_id,
                    key_properties=params.key_properties or ["dn"],
                    replication_method=params.replication_method,
                    replication_key=params.replication_key,
                    stream_schema={},
                )

                self._streams[str(stream.id)] = stream
                return FlextResult[LDAPStream].ok(stream)
            except (RuntimeError, ValueError, TypeError) as e:
                return FlextResult[LDAPStream].fail(f"Failed to create stream: {e}")

        def discover_schema(
            self,
            stream_id: str,
        ) -> FlextResult[Mapping[str, t.ContainerValue]]:
            """Discover schema for LDAP stream."""
            try:
                stream = self._streams.get(stream_id)
                if not stream:
                    return FlextResult[t.ConfigurationMapping].fail(
                        "Stream not found",
                    )

                # Basic schema for LDAP entries
                schema: dict[str, t.ContainerValue] = {
                    "type": "object",
                    "properties": {
                        "dn": {"type": "string"},
                        "objectClass": {"type": "array", "items": {"type": "string"}},
                    },
                    "additionalProperties": True,
                }

                # Update stream with schema
                stream.update_schema(schema)
                self._streams[stream_id] = stream

                return FlextResult[t.ConfigurationMapping].ok(schema)
            except (RuntimeError, ValueError, TypeError) as e:
                return FlextResult[t.ConfigurationMapping].fail(
                    f"Failed to discover schema: {e}",
                )

        def get_stream(self, stream_id: str) -> FlextResult[LDAPStream]:
            """Get LDAP stream by ID."""
            try:
                stream = self._streams.get(stream_id)
                if not stream:
                    return FlextResult[LDAPStream].fail("Stream not found")
                return FlextResult[LDAPStream].ok(stream)
            except (RuntimeError, ValueError, TypeError) as e:
                return FlextResult[LDAPStream].fail(f"Failed to get stream: {e}")

        def list_streams(
            self,
            connection_id: str | None = None,
        ) -> FlextResult[list[LDAPStream]]:
            """List LDAP streams, optionally filtered by connection ID."""
            try:
                streams = list(self._streams.values())

                if connection_id:
                    streams = [s for s in streams if s.connection_id == connection_id]

                return FlextResult[list[LDAPStream]].ok(streams)
            except (RuntimeError, ValueError, TypeError) as e:
                return FlextResult[list[LDAPStream]].fail(
                    f"Failed to list streams: {e}",
                )

    class TapExecutionService:
        """Service for managing tap executions with flext-core patterns."""

        def __init__(self) -> None:
            """Initialize the execution service."""
            self._executions: dict[str, TapExecution] = {}

        def create_execution(
            self,
            connection_id: str,
            command: str,
            config: Mapping[str, t.ContainerValue] | None = None,
            catalog: Mapping[str, t.ContainerValue] | None = None,
            state: Mapping[str, t.ContainerValue] | None = None,
        ) -> FlextResult[TapExecution]:
            """Create tap execution."""
            try:
                execution = TapExecution(
                    execution_id=f"exec_{uuid4().hex[:8]}",
                    connection_id=connection_id,
                    command=command,
                    tap_status="created",
                    config=dict(config or {}),
                    catalog=dict(catalog or {}),
                    state=dict(state or {}),
                )

                self._executions[str(execution.id)] = execution
                return FlextResult[TapExecution].ok(execution)
            except (RuntimeError, ValueError, TypeError) as e:
                return FlextResult[TapExecution].fail(
                    f"Failed to create execution: {e}",
                )

        def start_execution(
            self,
            execution_id: str,
        ) -> FlextResult[TapExecution]:
            """Start tap execution."""
            try:
                execution = self._executions.get(execution_id)
                if not execution:
                    return FlextResult[TapExecution].fail("Execution not found")

                execution.start_execution()
                self._executions[execution_id] = execution
                return FlextResult[TapExecution].ok(execution)
            except (RuntimeError, ValueError, TypeError) as e:
                return FlextResult[TapExecution].fail(f"Failed to start execution: {e}")

        def complete_execution(
            self,
            execution_id: str,
            exit_code: int,
            stdout: str | None = None,
            stderr: str | None = None,
        ) -> FlextResult[TapExecution]:
            """Complete tap execution."""
            try:
                execution = self._executions.get(execution_id)
                if not execution:
                    return FlextResult[TapExecution].fail("Execution not found")

                execution.complete_execution(exit_code, stdout, stderr)
                self._executions[execution_id] = execution
                return FlextResult[TapExecution].ok(execution)
            except (RuntimeError, ValueError, TypeError) as e:
                return FlextResult[TapExecution].fail(
                    f"Failed to complete execution: {e}",
                )

        def cancel_execution(
            self,
            execution_id: str,
        ) -> FlextResult[TapExecution]:
            """Cancel tap execution."""
            try:
                execution = self._executions.get(execution_id)
                if not execution:
                    return FlextResult[TapExecution].fail("Execution not found")

                execution.cancel_execution()
                self._executions[execution_id] = execution
                return FlextResult[TapExecution].ok(execution)
            except (RuntimeError, ValueError, TypeError) as e:
                return FlextResult[TapExecution].fail(
                    f"Failed to cancel execution: {e}",
                )

        def update_metrics(
            self,
            execution_id: str,
            records_extracted: int,
            streams_processed: int,
        ) -> FlextResult[TapExecution]:
            """Update execution metrics."""
            try:
                execution = self._executions.get(execution_id)
                if not execution:
                    return FlextResult[TapExecution].fail("Execution not found")

                execution.update_metrics(
                    records_extracted,
                    streams_processed,
                )
                self._executions[execution_id] = execution
                return FlextResult[TapExecution].ok(execution)
            except (RuntimeError, ValueError, TypeError) as e:
                return FlextResult[TapExecution].fail(f"Failed to update metrics: {e}")

        def get_execution(
            self,
            execution_id: str,
        ) -> FlextResult[TapExecution]:
            """Get tap execution by ID."""
            try:
                execution = self._executions.get(execution_id)
                if not execution:
                    return FlextResult[TapExecution].fail("Execution not found")
                return FlextResult[TapExecution].ok(execution)
            except (RuntimeError, ValueError, TypeError) as e:
                return FlextResult[TapExecution].fail(f"Failed to get execution: {e}")

        def list_executions(
            self,
            connection_id: str | None = None,
        ) -> FlextResult[list[TapExecution]]:
            """List tap executions, optionally filtered by connection ID."""
            try:
                executions = list(self._executions.values())

                if connection_id:
                    executions = [
                        e for e in executions if e.connection_id == connection_id
                    ]

                # Sort by started_at descending
                executions.sort(
                    key=lambda e: e.started_at or datetime.min.replace(tzinfo=UTC),
                    reverse=True,
                )

                return FlextResult[list[TapExecution]].ok(executions)
            except (RuntimeError, ValueError, TypeError) as e:
                return FlextResult[list[TapExecution]].fail(
                    f"Failed to list executions: {e}",
                )

    # LDIF PROCESSING SERVICE using flext-ldif integration

    class LDIFProcessingService:
        """Service for LDIF file processing using flext-ldif library."""

        def __init__(self) -> None:
            """Initialize LDIF processing service."""
            self._ldif_api = FlextLdif()

        def process_ldif_file(
            self,
            file_path: str,
        ) -> FlextResult[list[Mapping[str, t.ContainerValue]]]:
            """Process LDIF file using flext-ldif library."""
            try:
                logger.info("Processing LDIF file: %s", file_path)

                # Use flext-ldif to parse the file
                result: FlextResult[list[FlextLdifModels.Ldif.Entry]] = (
                    self._ldif_api.parse(
                        Path(file_path),
                    )
                )

                if not result.is_success:
                    return FlextResult[list[t.ConfigurationMapping]].fail(
                        f"Failed to parse LDIF file: {result.error}",
                    )

                entries: list[FlextLdifModels.Ldif.Entry] = result.data or []
                entry_count = len(entries)
                logger.info(
                    "Successfully processed %s entries from %s",
                    entry_count,
                    file_path,
                )

                # Normalize to list[dict[str, t.ContainerValue]]
                normalized: list[Mapping[str, t.ContainerValue]] = []
                for entry in entries:
                    dn_value = entry.dn.value if entry.dn is not None else ""
                    attributes_raw: Mapping[str, t.ContainerValue] = (
                        entry.attributes.attributes
                        if entry.attributes is not None
                        else {}
                    )
                    attrs = _as_map(attributes_raw) or {}
                    normalized.append({"dn": dn_value, "attributes": attrs})

                return FlextResult[list[t.ConfigurationMapping]].ok(
                    normalized,
                )

            except (
                ValueError,
                TypeError,
                KeyError,
                AttributeError,
                OSError,
                RuntimeError,
                ImportError,
            ) as e:
                logger.exception("Error processing LDIF file %s", file_path)
                return FlextResult[list[t.ConfigurationMapping]].fail(
                    f"LDIF processing failed: {e}",
                )

        def validate_ldif_file(
            self,
            file_path: str,
        ) -> FlextResult[Mapping[str, t.ContainerValue]]:
            """Validate LDIF file using flext-ldif library."""
            try:
                logger.info("Validating LDIF file: %s", file_path)

                # Basic validation via parsing using flext-ldif
                result: FlextResult[list[FlextLdifModels.Ldif.Entry]] = (
                    self._ldif_api.parse(
                        Path(file_path),
                    )
                )

                if not result.is_success:
                    return FlextResult[t.ConfigurationMapping].fail(
                        f"Validation failed: {result.error}",
                    )

                entries: list[FlextLdifModels.Ldif.Entry] = result.data or []
                total_entries = len(entries)
                # Consider parse success as valid
                validation_data: dict[str, t.ContainerValue] = {
                    "total_entries": total_entries,
                    "valid_entries": total_entries,
                    "invalid_entries": 0,
                    "errors": [],
                }
                logger.info("LDIF file validation completed: %s", file_path)

                return FlextResult[t.ConfigurationMapping].ok(
                    validation_data,
                )

            except (
                ValueError,
                TypeError,
                KeyError,
                AttributeError,
                OSError,
                RuntimeError,
                ImportError,
            ) as e:
                logger.exception("Error validating LDIF file %s", file_path)
                return FlextResult[t.ConfigurationMapping].fail(
                    f"LDIF validation failed: {e}",
                )

        def get_ldif_statistics(
            self,
            file_path: str,
        ) -> FlextResult[Mapping[str, t.ContainerValue]]:
            """Get LDIF file statistics using flext-ldif library."""
            try:
                # First validate to get statistics
                validation_result: FlextResult[Mapping[str, t.ContainerValue]] = (
                    self.validate_ldif_file(file_path)
                )

                if not validation_result.is_success:
                    return validation_result

                validation_data: Mapping[str, t.ContainerValue] = (
                    _as_map(validation_result.data) or {}
                )

                # Add file-level statistics
                file_stats: dict[str, t.ContainerValue] = {
                    "file_path": file_path,
                    "file_size_bytes": Path(file_path).stat().st_size
                    if Path(file_path).exists()
                    else 0,
                    **validation_data,
                }

                return FlextResult[t.ConfigurationMapping].ok(
                    file_stats,
                )

            except (
                ValueError,
                TypeError,
                KeyError,
                AttributeError,
                OSError,
                RuntimeError,
                ImportError,
            ) as e:
                logger.exception("Error getting LDIF statistics for %s", file_path)
                return FlextResult[t.ConfigurationMapping].fail(
                    f"LDIF statistics failed: {e}",
                )

    # SIMPLE API UTILITIES

    @staticmethod
    def setup_ldap_tap(
        config: FlextTapLdapSettings | None = None,
    ) -> FlextResult[FlextTapLdapSettings]:
        """Set up the LDAP tap with configuration.

        Args:
        config: Optional configuration. If None, creates defaults.

        Returns:
        FlextResult with FlextTapLdapSettings or error message.

        """
        try:
            if config is None:
                # Create with intelligent defaults
                config = FlextTapLdapSettings.create_for_development()

            # Validate configuration
            validation_result: FlextResult[bool] = config.validate_tap_configuration()
            if not validation_result.is_success:
                return FlextResult[FlextTapLdapSettings].fail(
                    validation_result.error or "Configuration validation failed",
                )

            return FlextResult[FlextTapLdapSettings].ok(config)

        except (RuntimeError, ValueError, TypeError) as e:
            return FlextResult[FlextTapLdapSettings].fail(
                f"Failed to setup LDAP tap: {e}",
            )

    @staticmethod
    def create_ldap_connection_config(
        params: FlextTapLdapServices.LDAPConnectionParams,
    ) -> FlextResult[Mapping[str, t.ContainerValue]]:
        """Create LDAP connection configuration using Parameter Object Pattern.

        Args:
        params: LDAP connection parameters object

        Returns:
        FlextResult with connection configuration or error message.

        """
        try:
            config: dict[str, t.ContainerValue] = {
                "host": params.host,
                "port": params.port,
                "bind_dn": params.bind_dn,
                "bind_password": params.bind_password,
                "base_dn": params.base_dn,
                "use_ssl": params.use_ssl,
                "timeout_seconds": params.timeout_seconds,
                "page_size": params.page_size,
                "max_retries": params.max_retries,
            }

            return FlextResult[t.ConfigurationMapping].ok(config)

        except (RuntimeError, ValueError, TypeError) as e:
            return FlextResult[t.ConfigurationMapping].fail(
                f"Failed to create LDAP connection config: {e}",
            )

    @staticmethod
    def create_ldap_connection_config_convenience(
        host: str,
        base_dn: str,
        port: int = c.TapLdap.DEFAULT_PORT,
        **kwargs: t.ContainerValue,
    ) -> FlextResult[Mapping[str, t.ContainerValue]]:
        """Create LDAP connection configuration (testing convenience interface).

        Testing convenience wrapper for the Parameter Object Pattern implementation.
        Use FlextTapLdapServices.create_ldap_connection_config() with FlextTapLdapServices.LDAPConnectionParams for new code.
        """
        params = FlextTapLdapServices.LDAPConnectionParams(
            host=host,
            base_dn=base_dn,
            port=port,
            use_ssl=bool(kwargs.get("use_ssl")),
            bind_dn=_as_str(kwargs.get("bind_dn")),
            bind_password=_as_str(kwargs.get("bind_password")),
        )
        return FlextTapLdapServices.create_ldap_connection_config(
            params,
        )

    @staticmethod
    def validate_ldap_config(
        config: FlextTapLdapSettings,
    ) -> FlextResult[bool]:
        """Validate LDAP tap configuration.

        Args:
        config: Configuration to validate

        Returns:
        FlextResult with validation success or error message.

        """
        try:
            validation_result: FlextResult[bool] = config.validate_tap_configuration()
            return FlextResult[bool].ok(validation_result.is_success)

        except (RuntimeError, ValueError, TypeError) as e:
            return FlextResult[bool].fail(f"Configuration validation failed: {e}")

    @staticmethod
    def create_development_ldap_config(
        **overrides: t.ContainerValue,
    ) -> FlextResult[FlextTapLdapSettings]:
        """Create development LDAP configuration with defaults.

        Args:
        **overrides: Configuration overrides

        Returns:
        FlextResult with FlextTapLdapSettings for development use.

        """
        try:
            config = FlextTapLdapSettings.create_for_development(**overrides)
            return FlextResult[FlextTapLdapSettings].ok(config)

        except (RuntimeError, ValueError, TypeError) as e:
            return FlextResult[FlextTapLdapSettings].fail(
                f"Failed to create development config: {e}",
            )

    @staticmethod
    def create_production_ldap_config(
        **overrides: t.ContainerValue,
    ) -> FlextResult[FlextTapLdapSettings]:
        """Create production LDAP configuration with security defaults.

        Args:
        **overrides: Configuration overrides

        Returns:
        FlextResult with FlextTapLdapSettings for production use.

        """
        try:
            config = FlextTapLdapSettings.create_for_production(**overrides)
            return FlextResult[FlextTapLdapSettings].ok(config)

        except (RuntimeError, ValueError, TypeError) as e:
            return FlextResult[FlextTapLdapSettings].fail(
                f"Failed to create production config: {e}",
            )


__all__ = [
    "FlextTapLdapServices",
]
