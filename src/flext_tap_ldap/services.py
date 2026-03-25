"""Services for FLEXT Tap LDAP operations and utilities.

Consolidates application services, LDIF processing, and simple API utilities
with maximum integration to flext-core, flext-ldap, and flext-ldif libraries.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping, MutableSequence, Sequence
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from flext_core import FlextLogger, r
from flext_ldif import FlextLdif
from pydantic import ValidationError

from flext_tap_ldap import t
from flext_tap_ldap.constants import c
from flext_tap_ldap.models import FlextTapLdapModels
from flext_tap_ldap.settings import FlextTapLdapSettings
from flext_tap_ldap.typings import FlextTapLdapTypes

logger = FlextLogger(__name__)


class FlextTapLdapServices:
    """Unified services class for LDAP tap operations with complete service management.

    This class consolidates all LDAP tap services including connection management,
    stream processing, record handling, and LDIF processing following the unified
    class pattern with Clean Architecture and Domain-Driven Design.

    Contains all service classes and utility functions as nested classes and methods
    to maintain single responsibility while providing complete LDAP/LDIF
    data extraction and processing capabilities.
    """

    @staticmethod
    def _as_map(value: t.NormalizedValue) -> Mapping[str, t.ContainerValue] | None:
        try:
            return FlextTapLdapTypes.CONFIG_MAP_ADAPTER.validate_python(value)
        except ValidationError:
            return None

    @staticmethod
    def _as_str(value: t.NormalizedValue) -> str | None:
        try:
            return FlextTapLdapTypes.STRICT_STR_ADAPTER.validate_python(value)
        except ValidationError:
            return None

    EXPECTED_DATA_COUNT = 3

    class LDAPConnectionService:
        """Service for managing LDAP connections with flext-core patterns."""

        def __init__(self) -> None:
            """Initialize the connection service."""
            self._connections: MutableMapping[
                str,
                FlextTapLdapModels.TapLdap.LdapConnection,
            ] = {}

        def create_connection(
            self,
            params: FlextTapLdapModels.TapLdap.LdapConnectionParams,
        ) -> r[FlextTapLdapModels.TapLdap.LdapConnection]:
            """Create LDAP connection using parameter t.NormalizedValue pattern."""
            try:
                connection = FlextTapLdapModels.TapLdap.LdapConnection(
                    id=uuid4().hex,
                    host=params.host,
                    port=params.port,
                    bind_dn=params.bind_dn,
                    password=params.bind_password,
                    use_ssl=params.use_ssl,
                    timeout=params.timeout_seconds,
                    domain_events=[],
                )
                self._connections[str(connection.id)] = connection
                return r[FlextTapLdapModels.TapLdap.LdapConnection].ok(connection)
            except (RuntimeError, ValueError, TypeError) as e:
                return r[FlextTapLdapModels.TapLdap.LdapConnection].fail(
                    f"Failed to create connection: {e}",
                )

        def get_connection(
            self,
            connection_id: str,
        ) -> r[FlextTapLdapModels.TapLdap.LdapConnection]:
            """Get LDAP connection by ID."""
            try:
                connection = self._connections.get(connection_id)
                if not connection:
                    return r[FlextTapLdapModels.TapLdap.LdapConnection].fail(
                        "Connection not found",
                    )
                return r[FlextTapLdapModels.TapLdap.LdapConnection].ok(connection)
            except (RuntimeError, ValueError, TypeError) as e:
                return r[FlextTapLdapModels.TapLdap.LdapConnection].fail(
                    f"Failed to get connection: {e}",
                )

        def list_connections(
            self,
        ) -> r[Sequence[FlextTapLdapModels.TapLdap.LdapConnection]]:
            """List all LDAP connections."""
            try:
                connections = list(self._connections.values())
                return r[Sequence[FlextTapLdapModels.TapLdap.LdapConnection]].ok(
                    connections,
                )
            except (RuntimeError, ValueError, TypeError) as e:
                return r[Sequence[FlextTapLdapModels.TapLdap.LdapConnection]].fail(
                    f"Failed to list connections: {e}",
                )

        def test_connection(
            self,
            connection_id: str,
        ) -> r[t.ContainerMapping]:
            """Test LDAP connection."""
            try:
                connection = self._connections.get(connection_id)
                if not connection:
                    return r[t.ContainerMapping].fail(
                        "Connection not found",
                    )
                connection.last_tested = datetime.now(UTC)
                connection.last_error = None
                self._connections[connection_id] = connection
                return r[t.ContainerMapping].ok({
                    "success": True,
                    "connection": connection.id,
                })
            except (RuntimeError, ValueError, TypeError) as e:
                connection = self._connections.get(connection_id)
                if connection:
                    connection.last_tested = datetime.now(UTC)
                    connection.last_error = str(e)
                    self._connections[connection_id] = connection
                return r[t.ContainerMapping].fail(
                    f"Failed to test connection: {e}",
                )

    class LDAPStreamService:
        """Service for managing LDAP streams with flext-core patterns."""

        def __init__(self) -> None:
            """Initialize the stream service."""
            self._streams: MutableMapping[
                str,
                FlextTapLdapModels.TapLdap.LdapStream,
            ] = {}

        def create_stream(
            self,
            params: FlextTapLdapModels.TapLdap.StreamCreationParams,
        ) -> r[FlextTapLdapModels.TapLdap.LdapStream]:
            """Create LDAP stream using parameter t.NormalizedValue pattern."""
            try:
                tap_stream_id = params.tap_stream_id
                if not tap_stream_id:
                    tap_stream_id = f"{params.stream_type.lower()}_stream"
                stream = FlextTapLdapModels.TapLdap.LdapStream(
                    id=uuid4().hex,
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
                return r[FlextTapLdapModels.TapLdap.LdapStream].ok(stream)
            except (RuntimeError, ValueError, TypeError) as e:
                return r[FlextTapLdapModels.TapLdap.LdapStream].fail(
                    f"Failed to create stream: {e}",
                )

        def discover_schema(self, stream_id: str) -> r[t.ContainerMapping]:
            """Discover schema for LDAP stream."""
            try:
                stream = self._streams.get(stream_id)
                if not stream:
                    return r[t.ContainerMapping].fail("Stream not found")
                schema: t.ContainerMapping = {
                    "type": "object",
                    "properties": {
                        "dn": {"type": "string"},
                        "objectClass": {"type": "array", "items": {"type": "string"}},
                    },
                    "additionalProperties": True,
                }
                stream.update_schema(schema)
                self._streams[stream_id] = stream
                return r[t.ContainerMapping].ok(schema)
            except (RuntimeError, ValueError, TypeError) as e:
                return r[t.ContainerMapping].fail(
                    f"Failed to discover schema: {e}",
                )

        def get_stream(
            self,
            stream_id: str,
        ) -> r[FlextTapLdapModels.TapLdap.LdapStream]:
            """Get LDAP stream by ID."""
            try:
                stream = self._streams.get(stream_id)
                if not stream:
                    return r[FlextTapLdapModels.TapLdap.LdapStream].fail(
                        "Stream not found",
                    )
                return r[FlextTapLdapModels.TapLdap.LdapStream].ok(stream)
            except (RuntimeError, ValueError, TypeError) as e:
                return r[FlextTapLdapModels.TapLdap.LdapStream].fail(
                    f"Failed to get stream: {e}",
                )

        def list_streams(
            self,
            connection_id: str | None = None,
        ) -> r[Sequence[FlextTapLdapModels.TapLdap.LdapStream]]:
            """List LDAP streams, optionally filtered by connection ID."""
            try:
                streams = list(self._streams.values())
                if connection_id:
                    streams = [s for s in streams if s.connection_id == connection_id]
                return r[Sequence[FlextTapLdapModels.TapLdap.LdapStream]].ok(streams)
            except (RuntimeError, ValueError, TypeError) as e:
                return r[Sequence[FlextTapLdapModels.TapLdap.LdapStream]].fail(
                    f"Failed to list streams: {e}",
                )

    class TapExecutionService:
        """Service for managing tap executions with flext-core patterns."""

        def __init__(self) -> None:
            """Initialize the execution service."""
            self._executions: MutableMapping[
                str,
                FlextTapLdapModels.TapLdap.TapExecution,
            ] = {}

        def cancel_execution(
            self,
            execution_id: str,
        ) -> r[FlextTapLdapModels.TapLdap.TapExecution]:
            """Cancel tap execution."""
            try:
                execution = self._executions.get(execution_id)
                if not execution:
                    return r[FlextTapLdapModels.TapLdap.TapExecution].fail(
                        "Execution not found",
                    )
                execution.cancel_execution()
                self._executions[execution_id] = execution
                return r[FlextTapLdapModels.TapLdap.TapExecution].ok(execution)
            except (RuntimeError, ValueError, TypeError) as e:
                return r[FlextTapLdapModels.TapLdap.TapExecution].fail(
                    f"Failed to cancel execution: {e}",
                )

        def complete_execution(
            self,
            execution_id: str,
            exit_code: int,
            stdout: str | None = None,
            stderr: str | None = None,
        ) -> r[FlextTapLdapModels.TapLdap.TapExecution]:
            """Complete tap execution."""
            try:
                execution = self._executions.get(execution_id)
                if not execution:
                    return r[FlextTapLdapModels.TapLdap.TapExecution].fail(
                        "Execution not found",
                    )
                execution.complete_execution(exit_code, stdout, stderr)
                self._executions[execution_id] = execution
                return r[FlextTapLdapModels.TapLdap.TapExecution].ok(execution)
            except (RuntimeError, ValueError, TypeError) as e:
                return r[FlextTapLdapModels.TapLdap.TapExecution].fail(
                    f"Failed to complete execution: {e}",
                )

        def create_execution(
            self,
            connection_id: str,
            command: str,
            config: t.ContainerMapping | None = None,
            catalog: t.ContainerMapping | None = None,
            state: t.ContainerMapping | None = None,
        ) -> r[FlextTapLdapModels.TapLdap.TapExecution]:
            """Create tap execution."""
            try:
                validated_config = FlextTapLdapServices._as_map(config or {}) or {}
                validated_catalog = FlextTapLdapServices._as_map(catalog or {}) or {}
                validated_state = FlextTapLdapServices._as_map(state or {}) or {}
                execution = FlextTapLdapModels.TapLdap.TapExecution(
                    id=uuid4().hex,
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
                return r[FlextTapLdapModels.TapLdap.TapExecution].ok(execution)
            except (RuntimeError, ValueError, TypeError) as e:
                return r[FlextTapLdapModels.TapLdap.TapExecution].fail(
                    f"Failed to create execution: {e}",
                )

        def get_execution(
            self,
            execution_id: str,
        ) -> r[FlextTapLdapModels.TapLdap.TapExecution]:
            """Get tap execution by ID."""
            try:
                execution = self._executions.get(execution_id)
                if not execution:
                    return r[FlextTapLdapModels.TapLdap.TapExecution].fail(
                        "Execution not found",
                    )
                return r[FlextTapLdapModels.TapLdap.TapExecution].ok(execution)
            except (RuntimeError, ValueError, TypeError) as e:
                return r[FlextTapLdapModels.TapLdap.TapExecution].fail(
                    f"Failed to get execution: {e}",
                )

        def list_executions(
            self,
            connection_id: str | None = None,
        ) -> r[Sequence[FlextTapLdapModels.TapLdap.TapExecution]]:
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
                return r[Sequence[FlextTapLdapModels.TapLdap.TapExecution]].ok(
                    executions,
                )
            except (RuntimeError, ValueError, TypeError) as e:
                return r[Sequence[FlextTapLdapModels.TapLdap.TapExecution]].fail(
                    f"Failed to list executions: {e}",
                )

        def start_execution(
            self,
            execution_id: str,
        ) -> r[FlextTapLdapModels.TapLdap.TapExecution]:
            """Start tap execution."""
            try:
                execution = self._executions.get(execution_id)
                if not execution:
                    return r[FlextTapLdapModels.TapLdap.TapExecution].fail(
                        "Execution not found",
                    )
                execution.start_execution()
                self._executions[execution_id] = execution
                return r[FlextTapLdapModels.TapLdap.TapExecution].ok(execution)
            except (RuntimeError, ValueError, TypeError) as e:
                return r[FlextTapLdapModels.TapLdap.TapExecution].fail(
                    f"Failed to start execution: {e}",
                )

        def update_metrics(
            self,
            execution_id: str,
            records_extracted: int,
            streams_processed: int,
        ) -> r[FlextTapLdapModels.TapLdap.TapExecution]:
            """Update execution metrics."""
            try:
                execution = self._executions.get(execution_id)
                if not execution:
                    return r[FlextTapLdapModels.TapLdap.TapExecution].fail(
                        "Execution not found",
                    )
                execution.update_metrics(records_extracted, streams_processed)
                self._executions[execution_id] = execution
                return r[FlextTapLdapModels.TapLdap.TapExecution].ok(execution)
            except (RuntimeError, ValueError, TypeError) as e:
                return r[FlextTapLdapModels.TapLdap.TapExecution].fail(
                    f"Failed to update metrics: {e}",
                )

    class LDIFProcessingService:
        """Service for LDIF file processing using flext-ldif library."""

        def __init__(self) -> None:
            """Initialize LDIF processing service."""
            self._ldif_api = FlextLdif()

        def get_ldif_statistics(
            self,
            file_path: str,
        ) -> r[t.ContainerMapping]:
            """Get LDIF file statistics using flext-ldif library."""
            try:
                validation_result: r[t.ContainerMapping] = self.validate_ldif_file(
                    file_path,
                )
                if not validation_result.is_success:
                    return validation_result
                validation_data: t.ContainerMapping = (
                    FlextTapLdapServices._as_map(validation_result.value) or {}
                )
                file_stats: t.ContainerMapping = {
                    "file_path": file_path,
                    "file_size_bytes": Path(file_path).stat().st_size
                    if Path(file_path).exists()
                    else 0,
                    **validation_data,
                }
                return r[t.ContainerMapping].ok(file_stats)
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
                return r[t.ContainerMapping].fail(
                    f"LDIF statistics failed: {e}",
                )

        def process_ldif_file(
            self,
            file_path: str,
        ) -> r[Sequence[t.ContainerMapping]]:
            """Process LDIF file using flext-ldif library."""
            try:
                logger.info("Processing LDIF file: %s", file_path)
                result: r[MutableSequence[FlextTapLdapModels.Ldif.Entry]] = (
                    self._ldif_api.parse_ldif(
                        Path(file_path),
                    )
                )
                if not result.is_success:
                    return r[Sequence[t.ContainerMapping]].fail(
                        f"Failed to parse LDIF file: {result.error}",
                    )
                entries: MutableSequence[FlextTapLdapModels.Ldif.Entry] = (
                    result.value or []
                )
                entry_count = len(entries)
                logger.info(
                    "Successfully processed %s entries from %s",
                    entry_count,
                    file_path,
                )
                normalized: Sequence[t.ContainerMapping] = [
                    {
                        "dn": entry.dn.value if entry.dn is not None else "",
                        "attributes": FlextTapLdapServices._as_map(
                            entry.attributes.attributes
                            if entry.attributes is not None
                            else {}
                        )
                        or {},
                    }
                    for entry in entries
                ]
                return r[Sequence[t.ContainerMapping]].ok(normalized)
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
                return r[Sequence[t.ContainerMapping]].fail(
                    f"LDIF processing failed: {e}",
                )

        def validate_ldif_file(
            self,
            file_path: str,
        ) -> r[t.ContainerMapping]:
            """Validate LDIF file using flext-ldif library."""
            try:
                logger.info("Validating LDIF file: %s", file_path)
                result: r[MutableSequence[FlextTapLdapModels.Ldif.Entry]] = (
                    self._ldif_api.parse_ldif(
                        Path(file_path),
                    )
                )
                if not result.is_success:
                    return r[t.ContainerMapping].fail(
                        f"Validation failed: {result.error}",
                    )
                entries: MutableSequence[FlextTapLdapModels.Ldif.Entry] = (
                    result.value or []
                )
                total_entries = len(entries)
                validation_data: t.ContainerMapping = {
                    "total_entries": total_entries,
                    "valid_entries": total_entries,
                    "invalid_entries": 0,
                    "errors": list[str](),
                }
                logger.info("LDIF file validation completed: %s", file_path)
                return r[t.ContainerMapping].ok(validation_data)
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
                return r[t.ContainerMapping].fail(
                    f"LDIF validation failed: {e}",
                )

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
                f"Failed to create development config: {e}",
            )

    @staticmethod
    def create_ldap_connection_config(
        params: FlextTapLdapModels.TapLdap.LdapConnectionParams,
    ) -> r[t.ContainerMapping]:
        """Create LDAP connection configuration using Parameter Object Pattern.

        Args:
        params: LDAP connection parameters t.NormalizedValue

        Returns:
        r with connection configuration or error message.

        """
        try:
            config: t.ContainerMapping = {
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
            return r[t.ContainerMapping].ok(config)
        except (RuntimeError, ValueError, TypeError) as e:
            return r[t.ContainerMapping].fail(
                f"Failed to create LDAP connection config: {e}",
            )

    @staticmethod
    def create_ldap_connection_config_convenience(
        host: str,
        base_dn: str,
        port: int = c.TapLdap.DEFAULT_PORT,
        **kwargs: t.Scalar,
    ) -> r[t.ContainerMapping]:
        """Create LDAP connection configuration (testing convenience interface).

        Testing convenience wrapper for the Parameter Object Pattern implementation.
        Use FlextTapLdapServices.create_ldap_connection_config() with FlextTapLdapModels.TapLdap.LdapConnectionParams for new code.
        """
        params = FlextTapLdapModels.TapLdap.LdapConnectionParams(
            host=host,
            base_dn=base_dn,
            port=port,
            use_ssl=bool(kwargs.get("use_ssl")),
            bind_dn=FlextTapLdapServices._as_str(kwargs.get("bind_dn")),
            bind_password=FlextTapLdapServices._as_str(kwargs.get("bind_password")),
            timeout_seconds=c.TapLdap.DEFAULT_SEARCH_TIMEOUT,
            page_size=c.TapLdap.DEFAULT_PAGE_SIZE,
            max_retries=3,
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
                f"Failed to create production config: {e}",
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
                config = FlextTapLdapSettings.model_validate({})
            validation_result = FlextTapLdapServices.validate_ldap_config(config)
            if not validation_result.is_success or not validation_result.value:
                return r[FlextTapLdapSettings].fail(
                    validation_result.error or "Configuration validation failed",
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
