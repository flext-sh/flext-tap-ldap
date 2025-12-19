"""Services for FLEXT Tap LDAP operations and utilities.

Consolidates application services, LDIF processing, and simple API utilities
with maximum integration to flext-core, flext-ldap, and flext-ldif libraries.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import override
from uuid import uuid4

from flext_core import FlextLogger, FlextResult
from flext_ldap import FlextLdapModels
from flext_ldif import FlextLdif

from flext_tap_ldap.settings import (
    FlextTapLdapSettings,
    LDIFProcessingConfig,
)

logger = FlextLogger(__name__)


@dataclass
class LDAPConnection:
    """LDAP connection model."""

    id: str = field(default_factory=lambda: str(uuid4()))
    host: str = ""
    port: int = 389
    bind_dn: str | None = None
    password: str | None = None
    use_ssl: bool = False
    timeout: int = 30
    last_tested: datetime | None = None
    last_error: str | None = None

    def __post_init__(self) -> None:
        """Initialize connection after creation."""
        if not self.id:
            self.id = str(uuid4())


@dataclass
class LDAPStream:
    """LDAP stream model."""

    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    connection_id: str = ""
    stream_type: str = ""
    search_filter: str = ""
    attributes: list[str] = field(default_factory=list)
    tap_stream_id: str = ""
    key_properties: list[str] = field(default_factory=lambda: ["dn"])
    replication_method: str = "FULL_TABLE"
    replication_key: str | None = None
    stream_schema: dict[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Initialize stream after creation."""
        if not self.id:
            self.id = str(uuid4())
        if not self.tap_stream_id:
            self.tap_stream_id = f"{self.name}_stream"

    def update_schema(self, schema: dict[str, object]) -> None:
        """Update stream schema."""
        self.stream_schema = schema


@dataclass
class TapExecution:
    """Tap execution model."""

    id: str = field(default_factory=lambda: str(uuid4()))
    execution_id: str = ""
    connection_id: str = ""
    command: str = ""
    tap_status: str = "created"
    config: dict[str, object] = field(default_factory=dict)
    catalog: dict[str, object] = field(default_factory=dict)
    state: dict[str, object] = field(default_factory=dict)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    exit_code: int | None = None
    stdout: str | None = None
    stderr: str | None = None
    records_extracted: int = 0
    streams_processed: int = 0

    def __post_init__(self) -> None:
        """Initialize execution after creation."""
        if not self.id:
            self.id = str(uuid4())
        if not self.execution_id:
            self.execution_id = f"exec_{self.id[:8]}"

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

    @dataclass
    class LDAPConnectionParams:
        """Parameter object for LDAP connection configuration.

        Implements Parameter Object Pattern to reduce parameter count
        and improve maintainability
        """

        host: str
        base_dn: str
        port: int = 389
        use_ssl: bool = False
        bind_dn: str | None = None
        bind_password: str | None = None
        timeout_seconds: int = 30
        page_size: int = 1000
        max_retries: int = 3

        def __post_init__(self) -> None:
            """Validate connection parameters after initialization."""
            # Constants for port validation
            max_port_number = 65535

            if not self.host:
                msg = "Host is required"
                raise ValueError(msg)
            if self.port <= 0 or self.port > max_port_number:
                msg = f"Port must be between 1 and {max_port_number}"
                raise ValueError(msg)
            if self.timeout_seconds <= 0:
                msg = "Timeout must be positive"
                raise ValueError(msg)
            if self.page_size <= 0:
                msg = "Page size must be positive"
                raise ValueError(msg)
            if self.max_retries < 0:
                msg = "Max retries cannot be negative"
                raise ValueError(msg)

    @dataclass
    class StreamCreationParams:
        """Parameter object for LDAP stream creation.

        Implements Parameter Object Pattern to reduce parameter count in create_stream method
        following SOLID principles for better maintainability.
        """

        connection_id: str
        stream_type: str
        search_filter: str
        attributes: list[str] | None = None
        tap_stream_id: str | None = None
        key_properties: list[str] | None = None
        replication_method: str = "FULL_TABLE"
        replication_key: str | None = None

        def __post_init__(self) -> None:
            """Validate stream creation parameters after initialization."""
            if not self.stream_type:
                msg = "Stream type is required"
                raise ValueError(msg)
            if not self.search_filter:
                msg = "Search filter is required"
                raise ValueError(msg)
            if self.replication_method not in {"FULL_TABLE", "INCREMENTAL"}:
                msg = "Replication method must be FULL_TABLE or INCREMENTAL"
                raise ValueError(msg)

    @dataclass
    class LDIFConfigBuilder:
        """Builder for LDIF processing configuration.

        Implements Builder Pattern to eliminate parameter proliferation
        following Interface Segregation Principle.
        """

        ldif_files: list[str] = field(
            default_factory=list,
        )
        ldif_directory: str | None = None
        ldif_file_pattern: str = "*.ldif"
        ldif_ignore_errors: bool = True
        ldif_max_errors: int = 100
        ldif_ignore_file_errors: bool = True
        ldif_ignore_entry_errors: bool = True
        ldif_apply_transformations: bool = False
        ldif_transformation_rules: dict[str, object] = field(
            default_factory=dict,
        )
        migration_batch: str | None = None
        enable_ldif_streams: bool = False

    class LDAPConnectionService:
        """Service for managing LDAP connections with flext-core patterns."""

        @override
        def __init__(self: object) -> None:
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
        ) -> FlextResult[dict[str, object]]:
            """Test LDAP connection."""
            try:
                connection = self._connections.get(connection_id)
                if not connection:
                    return FlextResult[dict[str, object]].fail(
                        "Connection not found",
                    )

                # Simulate test by marking last_tested and clearing last_error
                connection.last_tested = datetime.now(UTC)
                connection.last_error = None
                self._connections[connection_id] = connection

                return FlextResult[dict[str, object]].ok({
                    "success": "True",
                    "connection": "connection",
                })
            except (RuntimeError, ValueError, TypeError) as e:
                connection = self._connections.get(connection_id)
                if connection:
                    connection.last_tested = datetime.now(UTC)
                    connection.last_error = str(e)
                    self._connections[connection_id] = connection
                return FlextResult[dict[str, object]].fail(
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

        @override
        def __init__(self: object) -> None:
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
        ) -> FlextResult[dict[str, object]]:
            """Discover schema for LDAP stream."""
            try:
                stream = self._streams.get(stream_id)
                if not stream:
                    return FlextResult[dict[str, object]].fail(
                        "Stream not found",
                    )

                # Basic schema for LDAP entries
                schema = {
                    "type": "object",
                    "properties": {
                        "dn": {"type": "string"},
                        "objectClass": {"type": "array", "items": {"type": "string"}},
                    },
                    "additionalProperties": "True",
                }

                # Update stream with schema
                stream.update_schema(schema)
                self._streams[stream_id] = stream

                return FlextResult[dict[str, object]].ok(schema)
            except (RuntimeError, ValueError, TypeError) as e:
                return FlextResult[dict[str, object]].fail(
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

        @override
        def __init__(self: object) -> None:
            """Initialize the execution service."""
            self._executions: dict[str, TapExecution] = {}

        def create_execution(
            self,
            connection_id: str,
            command: str,
            config: dict[str, object] | None = None,
            catalog: dict[str, object] | None = None,
            state: dict[str, object] | None = None,
        ) -> FlextResult[TapExecution]:
            """Create tap execution."""
            try:
                execution = TapExecution(
                    execution_id=f"exec_{uuid4().hex[:8]}",
                    connection_id=connection_id,
                    command=command,
                    tap_status="created",
                    config=config or {},
                    catalog=catalog or {},
                    state=state or {},
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

        @override
        def __init__(self: object) -> None:
            """Initialize LDIF processing service."""
            self._ldif_api = FlextLdif()

        def process_ldif_file(
            self,
            file_path: str,
        ) -> FlextResult[list[dict[str, object]]]:
            """Process LDIF file using flext-ldif library."""
            try:
                logger.info("Processing LDIF file: %s", file_path)

                # Use flext-ldif to parse the file
                result: FlextResult[object] = self._ldif_api.parse_file(file_path)

                if not result.success:
                    return FlextResult[list[dict[str, object]]].fail(
                        f"Failed to parse LDIF file: {result.error}",
                    )

                entries = result.data or []
                logger.info(
                    f"Successfully processed {len(entries)} entries from {file_path}",
                )

                # Normalize to list[dict[str, object]]
                normalized: list[dict[str, object]] = []
                for entry in entries:
                    # FlextLdifEntry: expose minimal dict
                    getattr(getattr(entry, "dn", None), "value", None) or getattr(
                        entry,
                        "dn",
                        None,
                    )
                    attributes_obj: dict[str, object] = getattr(entry, "attributes", {})
                    getattr(attributes_obj, "attributes", attributes_obj)
                    normalized.append({"dn": "dn", "attributes": "attributes"})

                return FlextResult[list[dict[str, object]]].ok(
                    normalized,
                )

            except Exception as e:
                logger.exception("Error processing LDIF file %s", file_path)
                return FlextResult[list[dict[str, object]]].fail(
                    f"LDIF processing failed: {e}",
                )

        def validate_ldif_file(
            self,
            file_path: str,
        ) -> FlextResult[dict[str, object]]:
            """Validate LDIF file using flext-ldif library."""
            try:
                logger.info("Validating LDIF file: %s", file_path)

                # Basic validation via parsing using flext-ldif
                result: FlextResult[list[dict[str, object]]] = (
                    self._ldif_api.parse_file(file_path)
                )

                if not result.success:
                    return FlextResult[list[dict[str, object]]].fail(
                        f"Validation failed: {result.error}",
                    )

                entries = result.data or []
                len(entries)
                # Consider parse success as valid
                validation_data: dict[str, object] = {
                    "total_entries": "total_entries",
                    "valid_entries": "total_entries",
                    "invalid_entries": 0,
                    "errors": [],
                }
                logger.info("LDIF file validation completed: %s", file_path)

                return FlextResult[list[dict[str, object]]].ok(
                    validation_data,
                )

            except Exception as e:
                logger.exception("Error validating LDIF file %s", file_path)
                return FlextResult[list[dict[str, object]]].fail(
                    f"LDIF validation failed: {e}",
                )

        def get_ldif_statistics(
            self,
            file_path: str,
        ) -> FlextResult[dict[str, object]]:
            """Get LDIF file statistics using flext-ldif library."""
            try:
                # First validate to get statistics
                validation_result: FlextResult[list[dict[str, object]]] = (
                    self.validate_ldif_file(file_path)
                )

                if not validation_result.success:
                    return validation_result

                validation_data = validation_result.data or {}

                # Add file-level statistics
                file_stats = {
                    "file_path": "file_path",
                    "file_size_bytes": Path(file_path).stat().st_size
                    if Path(file_path).exists()
                    else 0,
                    **validation_data,
                }

                return FlextResult[list[dict[str, object]]].ok(
                    file_stats,
                )

            except Exception as e:
                logger.exception("Error getting LDIF statistics for %s", file_path)
                return FlextResult[list[dict[str, object]]].fail(
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
                config = FlextTapLdapSettings.create_with_defaults()

            # Validate configuration
            validation_result: FlextResult[FlextTapLdapSettings] = (
                config.validate_complete_config()
            )
            if not validation_result.success:
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
    ) -> FlextResult[dict[str, object]]:
        """Create LDAP connection configuration using Parameter Object Pattern.

        Args:
        params: LDAP connection parameters object

        Returns:
        FlextResult with connection configuration or error message.

        """
        try:
            config: dict[str, object] = {
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

            return FlextResult[object].ok(config)

        except (RuntimeError, ValueError, TypeError) as e:
            return FlextResult[object].fail(
                f"Failed to create LDAP connection config: {e}",
            )

    @staticmethod
    def create_ldap_connection_config_convenience(
        host: str,
        base_dn: str,
        port: int = 389,
        **kwargs: object,
    ) -> FlextResult[dict[str, object]]:
        """Create LDAP connection configuration (testing convenience interface).

        Testing convenience wrapper for the Parameter Object Pattern implementation.
        Use FlextTapLdapServices.create_ldap_connection_config() with FlextTapLdapServices.LDAPConnectionParams for new code.
        """
        params = FlextTapLdapServices.LDAPConnectionParams(
            host=host,
            base_dn=base_dn,
            port=port,
            use_ssl=bool(kwargs.get("use_ssl")),
            bind_dn=str(kwargs.get("bind_dn"))
            if isinstance(kwargs.get("bind_dn"), str)
            else None,
            bind_password=str(kwargs.get("bind_password"))
            if isinstance(kwargs.get("bind_password"), str)
            else None,
        )
        return FlextTapLdapServices.FlextTapLdapServices.create_ldap_connection_config(
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
            validation_result: FlextResult[bool] = config.validate_complete_config()
            return FlextResult[bool].ok(validation_result.success)

        except (RuntimeError, ValueError, TypeError) as e:
            return FlextResult[bool].fail(f"Configuration validation failed: {e}")

    @staticmethod
    def create_development_ldap_config(
        **overrides: object,
    ) -> FlextResult[FlextTapLdapSettings]:
        """Create development LDAP configuration with defaults.

        Args:
        **overrides: Configuration overrides

        Returns:
        FlextResult with FlextTapLdapSettings for development use.

        """
        try:
            connection_config = FlextLdapModels.ConnectionConfig.model_validate(
                {"server": "localhost", "port": 389, "use_ssl": "False", "timeout": 30},
            )

            config = FlextTapLdapSettings(
                connection=connection_config,
                ldif_processing=LDIFProcessingConfig(enable_ldif_streams=False),
                project_name="flext-data.taps.flext-tap-ldap",
                project_version="0.9.0",
            )

            # Apply overrides
            if overrides:
                config_dict: dict[str, object] = config.model_dump()
                config_dict.update(overrides)
                config = FlextTapLdapSettings(**config_dict)

            return FlextResult[FlextTapLdapSettings].ok(config)

        except (RuntimeError, ValueError, TypeError) as e:
            return FlextResult[FlextTapLdapSettings].fail(
                f"Failed to create development config: {e}",
            )

    @staticmethod
    def create_production_ldap_config(
        **overrides: object,
    ) -> FlextResult[FlextTapLdapSettings]:
        """Create production LDAP configuration with security defaults.

        Args:
        **overrides: Configuration overrides

        Returns:
        FlextResult with FlextTapLdapSettings for production use.

        """
        try:
            connection_config = FlextLdapModels.ConnectionConfig.model_validate(
                {
                    "server": "ldap.company.com",
                    "port": 636,
                    "use_ssl": "True",
                    "timeout": 30,
                },
            )

            config = FlextTapLdapSettings(
                connection=connection_config,
                ldif_processing=LDIFProcessingConfig(
                    enable_ldif_streams=False,
                    ldif_ignore_errors=False,
                    ldif_max_errors=10,
                ),
                project_name="flext-data.taps.flext-tap-ldap",
                project_version="0.9.0",
            )

            # Apply overrides
            if overrides:
                config_dict: dict[str, object] = config.model_dump()
                config_dict.update(overrides)
                config = FlextTapLdapSettings(**config_dict)

            return FlextResult[FlextTapLdapSettings].ok(config)

        except (RuntimeError, ValueError, TypeError) as e:
            return FlextResult[FlextTapLdapSettings].fail(
                f"Failed to create production config: {e}",
            )


__all__ = [
    "FlextTapLdapServices",
]
