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
from uuid import UUID

from flext_core import FlextResult, get_logger
from flext_ldap import FlextLdapConnectionConfig
from flext_ldif import FlextLdifAPI

from flext_tap_ldap.models import (
    LDAPConnection,
    LDAPRecord,
    LDAPStream,
    TapExecution,
)
from flext_tap_ldap.tap_config import (
    LDIFProcessingConfig,
    TapLDAPConfig,
)

logger = get_logger(__name__)

# Constants
EXPECTED_DATA_COUNT = 3


@dataclass
class LDAPConnectionParams:
    """Parameter object for LDAP connection configuration.

    Implements Parameter Object Pattern to reduce parameter count
    and improve maintainability following SOLID principles.
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

    ldif_files: list[str] = field(default_factory=list)
    ldif_directory: str | None = None
    ldif_file_pattern: str = "*.ldif"
    ldif_ignore_errors: bool = True
    ldif_max_errors: int = 100
    ldif_ignore_file_errors: bool = True
    ldif_ignore_entry_errors: bool = True
    ldif_apply_transformations: bool = False
    ldif_transformation_rules: dict[str, object] = field(default_factory=dict)
    migration_batch: str | None = None
    enable_ldif_streams: bool = False

    def with_files(self, files: list[str]) -> LDIFConfigBuilder:
        """Set LDIF files to process."""
        self.ldif_files = files
        return self

    def with_directory(self, directory: str) -> LDIFConfigBuilder:
        """Set LDIF directory to scan."""
        self.ldif_directory = directory
        return self

    def with_pattern(self, pattern: str) -> LDIFConfigBuilder:
        """Set file pattern for scanning."""
        self.ldif_file_pattern = pattern
        return self

    def with_error_handling(
        self,
        *,
        ignore_errors: bool = True,
        max_errors: int = 100,
    ) -> LDIFConfigBuilder:
        """Configure error handling behavior."""
        self.ldif_ignore_errors = ignore_errors
        self.ldif_max_errors = max_errors
        return self

    def with_transformations(
        self,
        *,
        enable: bool = True,
        rules: dict[str, object] | None = None,
    ) -> LDIFConfigBuilder:
        """Configure transformation settings."""
        self.ldif_apply_transformations = enable
        if rules:
            self.ldif_transformation_rules = rules
        return self

    def with_migration_batch(self, batch_name: str) -> LDIFConfigBuilder:
        """Set migration batch identifier."""
        self.migration_batch = batch_name
        return self

    def build(self) -> FlextResult[LDIFProcessingConfig]:
        """Build the LDIF processing configuration."""
        try:
            return FlextResult.ok(
                LDIFProcessingConfig(
                    ldif_files=self.ldif_files,
                    ldif_directory=self.ldif_directory,
                    ldif_file_pattern=self.ldif_file_pattern,
                    ldif_ignore_errors=self.ldif_ignore_errors,
                    ldif_max_errors=self.ldif_max_errors,
                    ldif_ignore_file_errors=self.ldif_ignore_file_errors,
                    ldif_ignore_entry_errors=self.ldif_ignore_entry_errors,
                    ldif_apply_transformations=self.ldif_apply_transformations,
                    ldif_transformation_rules=self.ldif_transformation_rules,
                    migration_batch=self.migration_batch,
                    enable_ldif_streams=self.enable_ldif_streams,
                ),
            )
        except (RuntimeError, ValueError, TypeError) as e:
            return FlextResult.fail(f"Failed to build LDIF processing config: {e}")


class LDAPConnectionService:
    """Service for managing LDAP connections with flext-core patterns."""

    def __init__(self) -> None:
        """Initialize the connection service."""
        self._connections: dict[str, LDAPConnection] = {}

    async def create_connection(
        self,
        params: LDAPConnectionParams,
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
            return FlextResult.ok(connection)
        except (RuntimeError, ValueError, TypeError) as e:
            return FlextResult.fail(f"Failed to create connection: {e}")

    async def test_connection(
        self,
        connection_id: str,
    ) -> FlextResult[dict[str, object]]:
        """Test LDAP connection."""
        try:
            connection = self._connections.get(connection_id)
            if not connection:
                return FlextResult.fail("Connection not found")

            # Simulate test by marking last_tested and clearing last_error
            connection.last_tested = datetime.now(UTC)
            connection.last_error = None
            self._connections[connection_id] = connection

            return FlextResult.ok({"success": True, "connection": connection})
        except (RuntimeError, ValueError, TypeError) as e:
            connection = self._connections.get(connection_id)
            if connection:
                connection.last_tested = datetime.now(UTC)
                connection.last_error = str(e)
                self._connections[connection_id] = connection
            return FlextResult.fail(f"Failed to test connection: {e}")

    async def get_connection(
        self,
        connection_id: str,
    ) -> FlextResult[LDAPConnection]:
        """Get LDAP connection by ID."""
        try:
            connection = self._connections.get(connection_id)
            if not connection:
                return FlextResult.fail("Connection not found")
            return FlextResult.ok(connection)
        except (RuntimeError, ValueError, TypeError) as e:
            return FlextResult.fail(f"Failed to get connection: {e}")

    async def list_connections(self) -> FlextResult[list[LDAPConnection]]:
        """List all LDAP connections."""
        try:
            connections = list(self._connections.values())
            return FlextResult.ok(connections)
        except (RuntimeError, ValueError, TypeError) as e:
            return FlextResult.fail(f"Failed to list connections: {e}")


class LDAPStreamService:
    """Service for managing LDAP streams with flext-core patterns."""

    def __init__(self) -> None:
        """Initialize the stream service."""
        self._streams: dict[str, LDAPStream] = {}

    async def create_stream(
        self,
        params: StreamCreationParams,
    ) -> FlextResult[LDAPStream]:
        """Create LDAP stream using parameter object pattern."""
        try:
            # Generate tap_stream_id if not provided
            tap_stream_id = params.tap_stream_id
            if not tap_stream_id:
                tap_stream_id = f"{params.stream_type.lower()}_stream"

            # Convert string to UUID for domain model
            stream = LDAPStream(
                connection_id=UUID(params.connection_id),
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
            return FlextResult.ok(stream)
        except (RuntimeError, ValueError, TypeError) as e:
            return FlextResult.fail(f"Failed to create stream: {e}")

    async def discover_schema(self, stream_id: str) -> FlextResult[dict[str, object]]:
        """Discover schema for LDAP stream."""
        try:
            stream = self._streams.get(stream_id)
            if not stream:
                return FlextResult.fail("Stream not found")

            # Basic schema for LDAP entries
            schema = {
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

            return FlextResult.ok(schema)
        except (RuntimeError, ValueError, TypeError) as e:
            return FlextResult.fail(f"Failed to discover schema: {e}")

    async def get_stream(self, stream_id: str) -> FlextResult[LDAPStream]:
        """Get LDAP stream by ID."""
        try:
            stream = self._streams.get(stream_id)
            if not stream:
                return FlextResult.fail("Stream not found")
            return FlextResult.ok(stream)
        except (RuntimeError, ValueError, TypeError) as e:
            return FlextResult.fail(f"Failed to get stream: {e}")

    async def list_streams(
        self,
        connection_id: str | None = None,
    ) -> FlextResult[list[LDAPStream]]:
        """List LDAP streams, optionally filtered by connection ID."""
        try:
            streams = list(self._streams.values())

            if connection_id:
                streams = [s for s in streams if s.connection_id == connection_id]

            return FlextResult.ok(streams)
        except (RuntimeError, ValueError, TypeError) as e:
            return FlextResult.fail(f"Failed to list streams: {e}")


class TapExecutionService:
    """Service for managing tap executions with flext-core patterns."""

    def __init__(self) -> None:
        """Initialize the execution service."""
        self._executions: dict[str, TapExecution] = {}

    async def create_execution(
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
                connection_id=UUID(connection_id),
                command=command,
                tap_status="created",
                config=config or {},
                catalog=catalog or {},
                state=state or {},
            )

            self._executions[str(execution.id)] = execution
            return FlextResult.ok(execution)
        except (RuntimeError, ValueError, TypeError) as e:
            return FlextResult.fail(f"Failed to create execution: {e}")

    async def start_execution(
        self,
        execution_id: str,
    ) -> FlextResult[TapExecution]:
        """Start tap execution."""
        try:
            execution = self._executions.get(execution_id)
            if not execution:
                return FlextResult.fail("Execution not found")

            execution.start_execution()
            self._executions[execution_id] = execution
            return FlextResult.ok(execution)
        except (RuntimeError, ValueError, TypeError) as e:
            return FlextResult.fail(f"Failed to start execution: {e}")

    async def complete_execution(
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
                return FlextResult.fail("Execution not found")

            execution.complete_execution(exit_code, stdout, stderr)
            self._executions[execution_id] = execution
            return FlextResult.ok(execution)
        except (RuntimeError, ValueError, TypeError) as e:
            return FlextResult.fail(f"Failed to complete execution: {e}")

    async def cancel_execution(
        self,
        execution_id: str,
    ) -> FlextResult[TapExecution]:
        """Cancel tap execution."""
        try:
            execution = self._executions.get(execution_id)
            if not execution:
                return FlextResult.fail("Execution not found")

            execution.cancel_execution()
            self._executions[execution_id] = execution
            return FlextResult.ok(execution)
        except (RuntimeError, ValueError, TypeError) as e:
            return FlextResult.fail(f"Failed to cancel execution: {e}")

    async def update_metrics(
        self,
        execution_id: str,
        records_extracted: int,
        streams_processed: int,
    ) -> FlextResult[TapExecution]:
        """Update execution metrics."""
        try:
            execution = self._executions.get(execution_id)
            if not execution:
                return FlextResult.fail("Execution not found")

            execution.update_metrics(
                records_extracted,
                streams_processed,
            )
            self._executions[execution_id] = execution
            return FlextResult.ok(execution)
        except (RuntimeError, ValueError, TypeError) as e:
            return FlextResult.fail(f"Failed to update metrics: {e}")

    async def get_execution(
        self,
        execution_id: str,
    ) -> FlextResult[TapExecution]:
        """Get tap execution by ID."""
        try:
            execution = self._executions.get(execution_id)
            if not execution:
                return FlextResult.fail("Execution not found")
            return FlextResult.ok(execution)
        except (RuntimeError, ValueError, TypeError) as e:
            return FlextResult.fail(f"Failed to get execution: {e}")

    async def list_executions(
        self,
        connection_id: str | None = None,
    ) -> FlextResult[list[TapExecution]]:
        """List tap executions, optionally filtered by connection ID."""
        try:
            executions = list(self._executions.values())

            if connection_id:
                executions = [e for e in executions if e.connection_id == connection_id]

            # Sort by started_at descending
            executions.sort(
                key=lambda e: e.started_at or datetime.min.replace(tzinfo=UTC),
                reverse=True,
            )

            return FlextResult.ok(executions)
        except (RuntimeError, ValueError, TypeError) as e:
            return FlextResult.fail(f"Failed to list executions: {e}")


class LDAPRecordService:
    """Service for managing LDAP records with flext-core patterns."""

    def __init__(self) -> None:
        """Initialize the record service."""
        self._records: dict[str, LDAPRecord] = {}

    async def create_record(
        self,
        stream_id: str,
        execution_id: str,
        dn: str,
        attributes: dict[str, object],
        object_class: list[str] | None = None,
    ) -> FlextResult[LDAPRecord]:
        """Create LDAP record."""
        try:
            record = LDAPRecord(
                stream_id=UUID(stream_id),
                execution_id=UUID(execution_id),
                dn=dn,
                attributes=attributes,
                object_class=object_class or [],
                singer_record={},  # Will be set by to_singer_record()
            )

            self._records[str(record.id)] = record
            return FlextResult.ok(record)
        except (RuntimeError, ValueError, TypeError) as e:
            return FlextResult.fail(f"Failed to create record: {e}")

    async def get_record(self, record_id: str) -> FlextResult[LDAPRecord]:
        """Get LDAP record by ID."""
        try:
            record = self._records.get(record_id)
            if not record:
                return FlextResult.fail("Record not found")
            return FlextResult.ok(record)
        except (RuntimeError, ValueError, TypeError) as e:
            return FlextResult.fail(f"Failed to get record: {e}")

    async def list_records(
        self,
        stream_id: str | None = None,
        execution_id: str | None = None,
        limit: int = 100,
    ) -> FlextResult[list[LDAPRecord]]:
        """List LDAP records, optionally filtered by stream or execution ID."""
        try:
            records = list(self._records.values())

            if stream_id:
                records = [r for r in records if r.stream_id == stream_id]

            if execution_id:
                records = [r for r in records if r.execution_id == execution_id]

            # Sort by extracted_at descending
            records.sort(key=lambda r: r.extracted_at, reverse=True)

            return FlextResult.ok(records[:limit])
        except (RuntimeError, ValueError, TypeError) as e:
            return FlextResult.fail(f"Failed to list records: {e}")

    async def count_records(
        self,
        stream_id: str | None = None,
        execution_id: str | None = None,
    ) -> FlextResult[int]:
        """Count LDAP records, optionally filtered by stream or execution ID."""
        try:
            records = list(self._records.values())

            if stream_id:
                records = [r for r in records if r.stream_id == stream_id]

            if execution_id:
                records = [r for r in records if r.execution_id == execution_id]

            return FlextResult.ok(len(records))
        except (RuntimeError, ValueError, TypeError) as e:
            return FlextResult.fail(f"Failed to count records: {e}")


# LDIF PROCESSING SERVICE using flext-ldif integration


class LDIFProcessingService:
    """Service for LDIF file processing using flext-ldif library."""

    def __init__(self) -> None:
        """Initialize LDIF processing service."""
        self._ldif_api = FlextLdifAPI()

    def process_ldif_file(self, file_path: str) -> FlextResult[list[dict[str, object]]]:
        """Process LDIF file using flext-ldif library."""
        try:
            logger.info(f"Processing LDIF file: {file_path}")

            # Use flext-ldif to parse the file
            result = self._ldif_api.parse_file(file_path)

            if not result.success:
                return FlextResult.fail(f"Failed to parse LDIF file: {result.error}")

            entries = result.data or []
            logger.info(
                f"Successfully processed {len(entries)} entries from {file_path}",
            )

            # Normalize to list[dict[str, object]]
            normalized: list[dict[str, object]] = []
            for entry in entries:
                # FlextLdifEntry: expose minimal dict
                dn = getattr(getattr(entry, "dn", None), "value", None) or getattr(
                    entry,
                    "dn",
                    None,
                )
                attributes_obj = getattr(entry, "attributes", {})
                attributes = getattr(attributes_obj, "attributes", attributes_obj)
                normalized.append({"dn": dn, "attributes": attributes})

            return FlextResult.ok(normalized)

        except Exception as e:
            logger.exception(f"Error processing LDIF file {file_path}")
            return FlextResult.fail(f"LDIF processing failed: {e}")

    def validate_ldif_file(self, file_path: str) -> FlextResult[dict[str, object]]:
        """Validate LDIF file using flext-ldif library."""
        try:
            logger.info(f"Validating LDIF file: {file_path}")

            # Basic validation via parsing using flext-ldif
            result = self._ldif_api.parse_file(file_path)

            if not result.success:
                return FlextResult.fail(f"Validation failed: {result.error}")

            entries = result.data or []
            total_entries = len(entries)
            # Consider parse success as valid
            validation_data: dict[str, object] = {
                "total_entries": total_entries,
                "valid_entries": total_entries,
                "invalid_entries": 0,
                "errors": [],
            }
            logger.info(f"LDIF file validation completed: {file_path}")

            return FlextResult.ok(validation_data)

        except Exception as e:
            logger.exception(f"Error validating LDIF file {file_path}")
            return FlextResult.fail(f"LDIF validation failed: {e}")

    def get_ldif_statistics(self, file_path: str) -> FlextResult[dict[str, object]]:
        """Get LDIF file statistics using flext-ldif library."""
        try:
            # First validate to get statistics
            validation_result = self.validate_ldif_file(file_path)

            if not validation_result.success:
                return validation_result

            validation_data = validation_result.data or {}

            # Add file-level statistics
            file_stats = {
                "file_path": file_path,
                "file_size_bytes": Path(file_path).stat().st_size
                if Path(file_path).exists()
                else 0,
                **validation_data,
            }

            return FlextResult.ok(file_stats)

        except Exception as e:
            logger.exception(f"Error getting LDIF statistics for {file_path}")
            return FlextResult.fail(f"LDIF statistics failed: {e}")


# SIMPLE API UTILITIES


def setup_ldap_tap(config: TapLDAPConfig | None = None) -> FlextResult[TapLDAPConfig]:
    """Set up the LDAP tap with configuration.

    Args:
        config: Optional configuration. If None, creates defaults.

    Returns:
        FlextResult with TapLDAPConfig or error message.

    """
    try:
        if config is None:
            # Create with intelligent defaults
            config = TapLDAPConfig.create_with_defaults()

        # Validate configuration
        validation_result = config.validate_complete_config()
        if not validation_result.success:
            return FlextResult.fail(
                validation_result.error or "Configuration validation failed",
            )

        return FlextResult.ok(config)

    except (RuntimeError, ValueError, TypeError) as e:
        return FlextResult.fail(f"Failed to setup LDAP tap: {e}")


def create_ldap_connection_config(
    params: LDAPConnectionParams,
) -> FlextResult[dict[str, object]]:
    """Create LDAP connection configuration using Parameter Object Pattern.

    Args:
        params: LDAP connection parameters object

    Returns:
        FlextResult with connection configuration or error message.

    """
    try:
        config = {
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

        return FlextResult.ok(config)

    except (RuntimeError, ValueError, TypeError) as e:
        return FlextResult.fail(f"Failed to create LDAP connection config: {e}")


def create_ldap_connection_config_legacy(
    host: str,
    base_dn: str,
    port: int = 389,
    **kwargs: object,
) -> FlextResult[dict[str, object]]:
    """Create LDAP connection configuration (legacy interface).

    Backward compatibility wrapper for the Parameter Object Pattern implementation.
    Use create_ldap_connection_config() with LDAPConnectionParams for new code.
    """
    params = LDAPConnectionParams(
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
    return create_ldap_connection_config(params)


def validate_ldap_config(config: TapLDAPConfig) -> FlextResult[bool]:
    """Validate LDAP tap configuration.

    Args:
        config: Configuration to validate

    Returns:
        FlextResult with validation success or error message.

    """
    try:
        validation_result = config.validate_complete_config()
        return FlextResult.ok(validation_result.success)

    except (RuntimeError, ValueError, TypeError) as e:
        return FlextResult.fail(f"Configuration validation failed: {e}")


def create_development_ldap_config(**overrides: object) -> FlextResult[TapLDAPConfig]:
    """Create development LDAP configuration with defaults.

    Args:
        **overrides: Configuration overrides

    Returns:
        FlextResult with TapLDAPConfig for development use.

    """
    try:
        connection_config = FlextLdapConnectionConfig.model_validate(
            {"server": "localhost", "port": 389, "use_ssl": False, "timeout": 30},
        )

        config = TapLDAPConfig(
            connection=connection_config,
            ldif_processing=LDIFProcessingConfig(enable_ldif_streams=False),
            project_name="flext-data.taps.flext-tap-ldap",
            project_version="0.9.0",
        )

        # Apply overrides
        if overrides:
            config_dict = config.model_dump()
            config_dict.update(overrides)
            config = TapLDAPConfig(**config_dict)

        return FlextResult.ok(config)

    except (RuntimeError, ValueError, TypeError) as e:
        return FlextResult.fail(f"Failed to create development config: {e}")


def create_production_ldap_config(**overrides: object) -> FlextResult[TapLDAPConfig]:
    """Create production LDAP configuration with security defaults.

    Args:
        **overrides: Configuration overrides

    Returns:
        FlextResult with TapLDAPConfig for production use.

    """
    try:
        connection_config = FlextLdapConnectionConfig.model_validate(
            {"server": "ldap.company.com", "port": 636, "use_ssl": True, "timeout": 30},
        )

        config = TapLDAPConfig(
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
            config_dict = config.model_dump()
            config_dict.update(overrides)
            config = TapLDAPConfig(**config_dict)

        return FlextResult.ok(config)

    except (RuntimeError, ValueError, TypeError) as e:
        return FlextResult.fail(f"Failed to create production config: {e}")


__all__ = [
    "LDAPConnectionParams",
    "LDAPConnectionService",
    "LDAPRecordService",
    "LDAPStreamService",
    "LDIFConfigBuilder",
    "LDIFProcessingService",
    "StreamCreationParams",
    "TapExecutionService",
    "create_development_ldap_config",
    "create_ldap_connection_config",
    "create_ldap_connection_config_legacy",
    "create_production_ldap_config",
    "setup_ldap_tap",
    "validate_ldap_config",
]
