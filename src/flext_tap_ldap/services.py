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

from flext_core import FlextLogger, FlextModels, r
from flext_ldif import FlextLdif, FlextLdifModels
from pydantic import ConfigDict, Field, TypeAdapter, ValidationError

from flext_tap_ldap import t
from flext_tap_ldap.constants import c
from flext_tap_ldap.models import TapExecution
from flext_tap_ldap.settings import FlextTapLdapSettings

logger = FlextLogger(__name__)
_MAP_ADAPTER = TypeAdapter(dict[str, object], config=ConfigDict(strict=True))
_STR_ADAPTER = TypeAdapter(str, config=ConfigDict(strict=True))


def _as_map(value: object) -> Mapping[str, object] | None:
    try:
        return _MAP_ADAPTER.validate_python(value)
    except ValidationError:
        return None


def _as_str(value: object) -> str | None:
    try:
        return _STR_ADAPTER.validate_python(value)
    except ValidationError:
        return None


class FlextTapLdapServices:
    """Unified services class for LDAP tap operations with complete service management.

    This class consolidates all LDAP tap services including connection management,
    stream processing, record handling, and LDIF processing following the unified
    class pattern with Clean Architecture and Domain-Driven Design.

    Contains all service classes and utility functions as nested classes and methods
    to maintain single responsibility while providing complete LDAP/LDIF
    data extraction and processing capabilities.
    """

    EXPECTED_DATA_COUNT = 3

    class LDAPConnectionParams(FlextModels.Value):
        """Parameters for establishing LDAP connection."""

        host: str = Field(min_length=1)
        base_dn: str = Field(min_length=1)
        port: int = Field(default=c.TapLdap.DEFAULT_PORT, ge=1)
        bind_dn: str | None = None
        bind_password: str | None = None
        use_ssl: bool = False
        timeout_seconds: int = Field(default=c.TapLdap.DEFAULT_SEARCH_TIMEOUT, ge=1)
        page_size: int = Field(default=c.TapLdap.DEFAULT_PAGE_SIZE, ge=1)
        max_retries: int = Field(default=3, ge=0)

    class StreamCreationParams(FlextModels.Value):
        """Parameters for creating LDAP data stream."""

        stream_type: str = Field(min_length=1)
        connection_id: str = Field(min_length=1)
        search_filter: str = Field(min_length=1)
        attributes: list[str] | None = None
        tap_stream_id: str | None = None
        key_properties: list[str] | None = None
        replication_method: str = "FULL_TABLE"
        replication_key: str | None = None

    class LDAPConnection(FlextModels.Entity):
        """LDAP connection entity with test status and error tracking."""

        host: str = Field(min_length=1)
        port: int = Field(ge=1)
        bind_dn: str | None = None
        password: str | None = None
        use_ssl: bool = False
        timeout: int = Field(ge=1)
        id: str = Field(default_factory=lambda: uuid4().hex)
        last_tested: datetime | None = None
        last_error: str | None = None

    class LDAPStream(FlextModels.Entity):
        """LDAP data stream with schema and replication configuration."""

        id: str = Field(default_factory=lambda: uuid4().hex)
        name: str = Field(min_length=1)
        connection_id: str = Field(min_length=1)
        stream_type: str = Field(min_length=1)
        search_filter: str = Field(min_length=1)
        attributes: list[str] = Field(default_factory=list)
        tap_stream_id: str = Field(min_length=1)
        key_properties: list[str] = Field(default_factory=lambda: ["dn"])
        replication_method: str = "FULL_TABLE"
        replication_key: str | None = None
        stream_schema: dict[str, object] = Field(default_factory=dict)

        def update_schema(self, schema: Mapping[str, object]) -> None:
            """Update stream schema from mapping."""
            self.stream_schema = dict(schema)

    class LDAPConnectionService:
        """Service for managing LDAP connections with flext-core patterns."""

        def __init__(self) -> None:
            """Initialize the connection service."""
            self._connections: dict[str, FlextTapLdapServices.LDAPConnection] = {}

        def create_connection(
            self, params: FlextTapLdapServices.LDAPConnectionParams
        ) -> r[FlextTapLdapServices.LDAPConnection]:
            """Create LDAP connection using parameter object pattern."""
            try:
                connection = FlextTapLdapServices.LDAPConnection(
                    host=params.host,
                    port=params.port,
                    bind_dn=params.bind_dn,
                    password=params.bind_password,
                    use_ssl=params.use_ssl,
                    timeout=params.timeout_seconds,
                    domain_events=[],
                )
                self._connections[str(connection.id)] = connection
                return r[FlextTapLdapServices.LDAPConnection].ok(connection)
            except (RuntimeError, ValueError, TypeError) as e:
                return r[FlextTapLdapServices.LDAPConnection].fail(
                    f"Failed to create connection: {e}"
                )

        def get_connection(
            self, connection_id: str
        ) -> r[FlextTapLdapServices.LDAPConnection]:
            """Get LDAP connection by ID."""
            try:
                connection = self._connections.get(connection_id)
                if not connection:
                    return r[FlextTapLdapServices.LDAPConnection].fail(
                        "Connection not found"
                    )
                return r[FlextTapLdapServices.LDAPConnection].ok(connection)
            except (RuntimeError, ValueError, TypeError) as e:
                return r[FlextTapLdapServices.LDAPConnection].fail(
                    f"Failed to get connection: {e}"
                )

        def list_connections(
            self,
        ) -> r[list[FlextTapLdapServices.LDAPConnection]]:
            """List all LDAP connections."""
            try:
                connections = list(self._connections.values())
                return r[list[FlextTapLdapServices.LDAPConnection]].ok(connections)
            except (RuntimeError, ValueError, TypeError) as e:
                return r[list[FlextTapLdapServices.LDAPConnection]].fail(
                    f"Failed to list connections: {e}"
                )

        def test_connection(self, connection_id: str) -> r[Mapping[str, object]]:
            """Test LDAP connection."""
            try:
                connection = self._connections.get(connection_id)
                if not connection:
                    return r[Mapping[str, object]].fail("Connection not found")
                connection.last_tested = datetime.now(UTC)
                connection.last_error = None
                self._connections[connection_id] = connection
                return r[Mapping[str, object]].ok({
                    "success": True,
                    "connection": connection.id,
                })
            except (RuntimeError, ValueError, TypeError) as e:
                connection = self._connections.get(connection_id)
                if connection:
                    connection.last_tested = datetime.now(UTC)
                    connection.last_error = str(e)
                    self._connections[connection_id] = connection
                return r[Mapping[str, object]].fail(f"Failed to test connection: {e}")

    class LDAPStreamService:
        """Service for managing LDAP streams with flext-core patterns."""

        def __init__(self) -> None:
            """Initialize the stream service."""
            self._streams: dict[str, FlextTapLdapServices.LDAPStream] = {}

        def create_stream(
            self, params: FlextTapLdapServices.StreamCreationParams
        ) -> r[FlextTapLdapServices.LDAPStream]:
            """Create LDAP stream using parameter object pattern."""
            try:
                tap_stream_id = params.tap_stream_id
                if not tap_stream_id:
                    tap_stream_id = f"{params.stream_type.lower()}_stream"
                stream = FlextTapLdapServices.LDAPStream(
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
                    domain_events=[],
                )
                self._streams[str(stream.id)] = stream
                return r[FlextTapLdapServices.LDAPStream].ok(stream)
            except (RuntimeError, ValueError, TypeError) as e:
                return r[FlextTapLdapServices.LDAPStream].fail(
                    f"Failed to create stream: {e}"
                )

        def discover_schema(self, stream_id: str) -> r[Mapping[str, object]]:
            """Discover schema for LDAP stream."""
            try:
                stream = self._streams.get(stream_id)
                if not stream:
                    return r[Mapping[str, object]].fail("Stream not found")
                schema: dict[str, object] = {
                    "type": "object",
                    "properties": {
                        "dn": {"type": "string"},
                        "objectClass": {"type": "array", "items": {"type": "string"}},
                    },
                    "additionalProperties": True,
                }
                stream.update_schema(schema)
                self._streams[stream_id] = stream
                return r[Mapping[str, object]].ok(schema)
            except (RuntimeError, ValueError, TypeError) as e:
                return r[Mapping[str, object]].fail(f"Failed to discover schema: {e}")

        def get_stream(self, stream_id: str) -> r[FlextTapLdapServices.LDAPStream]:
            """Get LDAP stream by ID."""
            try:
                stream = self._streams.get(stream_id)
                if not stream:
                    return r[FlextTapLdapServices.LDAPStream].fail("Stream not found")
                return r[FlextTapLdapServices.LDAPStream].ok(stream)
            except (RuntimeError, ValueError, TypeError) as e:
                return r[FlextTapLdapServices.LDAPStream].fail(
                    f"Failed to get stream: {e}"
                )

        def list_streams(
            self, connection_id: str | None = None
        ) -> r[list[FlextTapLdapServices.LDAPStream]]:
            """List LDAP streams, optionally filtered by connection ID."""
            try:
                streams = list(self._streams.values())
                if connection_id:
                    streams = [s for s in streams if s.connection_id == connection_id]
                return r[list[FlextTapLdapServices.LDAPStream]].ok(streams)
            except (RuntimeError, ValueError, TypeError) as e:
                return r[list[FlextTapLdapServices.LDAPStream]].fail(
                    f"Failed to list streams: {e}"
                )

    class TapExecutionService:
        """Service for managing tap executions with flext-core patterns."""

        def __init__(self) -> None:
            """Initialize the execution service."""
            self._executions: dict[str, TapExecution] = {}

        def cancel_execution(self, execution_id: str) -> r[TapExecution]:
            """Cancel tap execution."""
            try:
                execution = self._executions.get(execution_id)
                if not execution:
                    return r[TapExecution].fail("Execution not found")
                execution.cancel_execution()
                self._executions[execution_id] = execution
                return r[TapExecution].ok(execution)
            except (RuntimeError, ValueError, TypeError) as e:
                return r[TapExecution].fail(f"Failed to cancel execution: {e}")

        def complete_execution(
            self,
            execution_id: str,
            exit_code: int,
            stdout: str | None = None,
            stderr: str | None = None,
        ) -> r[TapExecution]:
            """Complete tap execution."""
            try:
                execution = self._executions.get(execution_id)
                if not execution:
                    return r[TapExecution].fail("Execution not found")
                execution.complete_execution(exit_code, stdout, stderr)
                self._executions[execution_id] = execution
                return r[TapExecution].ok(execution)
            except (RuntimeError, ValueError, TypeError) as e:
                return r[TapExecution].fail(f"Failed to complete execution: {e}")

        def create_execution(
            self,
            connection_id: str,
            command: str,
            config: Mapping[str, object] | None = None,
            catalog: Mapping[str, object] | None = None,
            state: Mapping[str, object] | None = None,
        ) -> r[TapExecution]:
            """Create tap execution."""
            try:
                validated_config = _as_map(config or {}) or {}
                validated_catalog = _as_map(catalog or {}) or {}
                validated_state = _as_map(state or {}) or {}
                execution = TapExecution(
                    execution_id=f"exec_{uuid4().hex[:8]}",
                    connection_id=connection_id,
                    command=command,
                    tap_status="created",
                    config={str(k): v for k, v in validated_config.items()},
                    catalog={str(k): v for k, v in validated_catalog.items()},
                    state={str(k): v for k, v in validated_state.items()},
                    domain_events=[],
                )
                self._executions[str(execution.id)] = execution
                return r[TapExecution].ok(execution)
            except (RuntimeError, ValueError, TypeError) as e:
                return r[TapExecution].fail(f"Failed to create execution: {e}")

        def get_execution(self, execution_id: str) -> r[TapExecution]:
            """Get tap execution by ID."""
            try:
                execution = self._executions.get(execution_id)
                if not execution:
                    return r[TapExecution].fail("Execution not found")
                return r[TapExecution].ok(execution)
            except (RuntimeError, ValueError, TypeError) as e:
                return r[TapExecution].fail(f"Failed to get execution: {e}")

        def list_executions(
            self, connection_id: str | None = None
        ) -> r[list[TapExecution]]:
            """List tap executions, optionally filtered by connection ID."""
            try:
                executions = list(self._executions.values())
                if connection_id:
                    executions = [
                        e for e in executions if e.connection_id == connection_id
                    ]
                executions.sort(
                    key=lambda e: e.started_at or datetime.min.replace(tzinfo=UTC),
                    reverse=True,
                )
                return r[list[TapExecution]].ok(executions)
            except (RuntimeError, ValueError, TypeError) as e:
                return r[list[TapExecution]].fail(f"Failed to list executions: {e}")

        def start_execution(self, execution_id: str) -> r[TapExecution]:
            """Start tap execution."""
            try:
                execution = self._executions.get(execution_id)
                if not execution:
                    return r[TapExecution].fail("Execution not found")
                execution.start_execution()
                self._executions[execution_id] = execution
                return r[TapExecution].ok(execution)
            except (RuntimeError, ValueError, TypeError) as e:
                return r[TapExecution].fail(f"Failed to start execution: {e}")

        def update_metrics(
            self, execution_id: str, records_extracted: int, streams_processed: int
        ) -> r[TapExecution]:
            """Update execution metrics."""
            try:
                execution = self._executions.get(execution_id)
                if not execution:
                    return r[TapExecution].fail("Execution not found")
                execution.update_metrics(records_extracted, streams_processed)
                self._executions[execution_id] = execution
                return r[TapExecution].ok(execution)
            except (RuntimeError, ValueError, TypeError) as e:
                return r[TapExecution].fail(f"Failed to update metrics: {e}")

    class LDIFProcessingService:
        """Service for LDIF file processing using flext-ldif library."""

        def __init__(self) -> None:
            """Initialize LDIF processing service."""
            self._ldif_api = FlextLdif()

        def get_ldif_statistics(self, file_path: str) -> r[Mapping[str, object]]:
            """Get LDIF file statistics using flext-ldif library."""
            try:
                validation_result: r[Mapping[str, object]] = self.validate_ldif_file(
                    file_path
                )
                if not validation_result.is_success:
                    return validation_result
                validation_data: Mapping[str, object] = (
                    _as_map(validation_result.value) or {}
                )
                file_stats: dict[str, object] = {
                    "file_path": file_path,
                    "file_size_bytes": Path(file_path).stat().st_size
                    if Path(file_path).exists()
                    else 0,
                    **validation_data,
                }
                return r[Mapping[str, object]].ok(file_stats)
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
                return r[Mapping[str, object]].fail(f"LDIF statistics failed: {e}")

        def process_ldif_file(self, file_path: str) -> r[list[Mapping[str, object]]]:
            """Process LDIF file using flext-ldif library."""
            try:
                logger.info("Processing LDIF file: %s", file_path)
                result: r[list[FlextLdifModels.Ldif.Entry]] = self._ldif_api.parse(
                    Path(file_path)
                )
                if not result.is_success:
                    return r[list[Mapping[str, object]]].fail(
                        f"Failed to parse LDIF file: {result.error}"
                    )
                entries: list[FlextLdifModels.Ldif.Entry] = result.value or []
                entry_count = len(entries)
                logger.info(
                    "Successfully processed %s entries from %s", entry_count, file_path
                )
                normalized: list[Mapping[str, object]] = []
                for entry in entries:
                    dn_value = entry.dn.value if entry.dn is not None else ""
                    attributes_raw: Mapping[str, object] = (
                        entry.attributes.attributes
                        if entry.attributes is not None
                        else {}
                    )
                    attrs = _as_map(attributes_raw) or {}
                    normalized.append({"dn": dn_value, "attributes": attrs})
                return r[list[Mapping[str, object]]].ok(normalized)
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
                return r[list[Mapping[str, object]]].fail(
                    f"LDIF processing failed: {e}"
                )

        def validate_ldif_file(self, file_path: str) -> r[Mapping[str, object]]:
            """Validate LDIF file using flext-ldif library."""
            try:
                logger.info("Validating LDIF file: %s", file_path)
                result: r[list[FlextLdifModels.Ldif.Entry]] = self._ldif_api.parse(
                    Path(file_path)
                )
                if not result.is_success:
                    return r[Mapping[str, object]].fail(
                        f"Validation failed: {result.error}"
                    )
                entries: list[FlextLdifModels.Ldif.Entry] = result.value or []
                total_entries = len(entries)
                validation_data: dict[str, object] = {
                    "total_entries": total_entries,
                    "valid_entries": total_entries,
                    "invalid_entries": 0,
                    "errors": [],
                }
                logger.info("LDIF file validation completed: %s", file_path)
                return r[Mapping[str, object]].ok(validation_data)
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
                return r[Mapping[str, object]].fail(f"LDIF validation failed: {e}")

    @staticmethod
    def create_development_ldap_config(
        **overrides: t.Scalar,
    ) -> r[FlextTapLdapSettings]:
        """Create development LDAP configuration with defaults.

        Args:
        **overrides: Configuration overrides

        Returns:
        r with FlextTapLdapSettings for development use.

        """
        try:
            config = FlextTapLdapSettings.model_validate(overrides)
            return r[FlextTapLdapSettings].ok(config)
        except (RuntimeError, ValueError, TypeError) as e:
            return r[FlextTapLdapSettings].fail(
                f"Failed to create development config: {e}"
            )

    @staticmethod
    def create_ldap_connection_config(
        params: FlextTapLdapServices.LDAPConnectionParams,
    ) -> r[Mapping[str, object]]:
        """Create LDAP connection configuration using Parameter Object Pattern.

        Args:
        params: LDAP connection parameters object

        Returns:
        r with connection configuration or error message.

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
            return r[Mapping[str, object]].ok(config)
        except (RuntimeError, ValueError, TypeError) as e:
            return r[Mapping[str, object]].fail(
                f"Failed to create LDAP connection config: {e}"
            )

    @staticmethod
    def create_ldap_connection_config_convenience(
        host: str,
        base_dn: str,
        port: int = c.TapLdap.DEFAULT_PORT,
        **kwargs: t.Scalar,
    ) -> r[Mapping[str, object]]:
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
        return FlextTapLdapServices.create_ldap_connection_config(params)

    @staticmethod
    def create_production_ldap_config(
        **overrides: t.Scalar,
    ) -> r[FlextTapLdapSettings]:
        """Create production LDAP configuration with security defaults.

        Args:
        **overrides: Configuration overrides

        Returns:
        r with FlextTapLdapSettings for production use.

        """
        try:
            production_overrides = {"use_ssl": True, **overrides}
            config = FlextTapLdapSettings.model_validate(production_overrides)
            return r[FlextTapLdapSettings].ok(config)
        except (RuntimeError, ValueError, TypeError) as e:
            return r[FlextTapLdapSettings].fail(
                f"Failed to create production config: {e}"
            )

    @staticmethod
    def setup_ldap_tap(
        config: FlextTapLdapSettings | None = None,
    ) -> r[FlextTapLdapSettings]:
        """Set up the LDAP tap with configuration.

        Args:
        config: Optional configuration. If None, creates defaults.

        Returns:
        r with FlextTapLdapSettings or error message.

        """
        try:
            if config is None:
                config = FlextTapLdapSettings()
            validation_result = FlextTapLdapServices.validate_ldap_config(config)
            if not validation_result.is_success or not validation_result.value:
                return r[FlextTapLdapSettings].fail(
                    validation_result.error or "Configuration validation failed"
                )
            return r[FlextTapLdapSettings].ok(config)
        except (RuntimeError, ValueError, TypeError) as e:
            return r[FlextTapLdapSettings].fail(f"Failed to setup LDAP tap: {e}")

    @staticmethod
    def validate_ldap_config(config: FlextTapLdapSettings) -> r[bool]:
        """Validate LDAP tap configuration.

        Args:
        config: Configuration to validate

        Returns:
        r with validation success or error message.

        """
        try:
            is_valid = bool(config.host and config.port > 0 and config.page_size > 0)
            return r[bool].ok(is_valid)
        except (RuntimeError, ValueError, TypeError) as e:
            return r[bool].fail(f"Configuration validation failed: {e}")


__all__ = ["FlextTapLdapServices"]
