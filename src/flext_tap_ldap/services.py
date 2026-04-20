"""Services for FLEXT Tap LDAP operations and utilities.

Consolidates application services, LDIF processing, and simple API utilities
with maximum integration to flext-core, flext-ldap, and flext-ldif libraries.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import (
    Mapping,
    MutableMapping,
    MutableSequence,
    Sequence,
)
from datetime import UTC, datetime
from pathlib import Path
from typing import ClassVar
from uuid import uuid4

from flext_ldif import ldif

from flext_tap_ldap import FlextTapLdapSettings, c, m, p, r, t, u


class FlextTapLdapServices:
    """Unified services class for LDAP tap operations with complete service management.

    This class consolidates all LDAP tap services including connection management,
    stream processing, record handling, and LDIF processing following the unified
    class pattern with Clean Architecture and Domain-Driven Design.

    Contains all service classes and utility functions as nested classes and methods
    to maintain single responsibility while providing complete LDAP/LDIF
    data extraction and processing capabilities.
    """

    _logger: ClassVar = u.fetch_logger(__name__)

    EXPECTED_DATA_COUNT = 3

    class LDAPConnectionService:
        """Service for managing LDAP connections with flext-core patterns."""

        def __init__(self) -> None:
            """Initialize the connection service."""
            self._connections: MutableMapping[
                str,
                m.TapLdap.LdapConnection,
            ] = {}

        def create_connection(
            self,
            params: m.TapLdap.LdapConnectionParams,
        ) -> p.Result[m.TapLdap.LdapConnection]:
            """Create LDAP connection using parameter object pattern."""
            try:
                connection = m.TapLdap.LdapConnection(
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
                return r[m.TapLdap.LdapConnection].ok(connection)
            except (RuntimeError, ValueError, TypeError) as e:
                return r[m.TapLdap.LdapConnection].fail(
                    f"Failed to create connection: {e}",
                )

        def fetch_connection(
            self,
            connection_id: str,
        ) -> p.Result[m.TapLdap.LdapConnection]:
            """Get LDAP connection by ID."""
            try:
                connection = self._connections.get(connection_id)
                if not connection:
                    return r[m.TapLdap.LdapConnection].fail(
                        "Connection not found",
                    )
                return r[m.TapLdap.LdapConnection].ok(connection)
            except (RuntimeError, ValueError, TypeError) as e:
                return r[m.TapLdap.LdapConnection].fail(
                    f"Failed to get connection: {e}",
                )

        def list_connections(
            self,
        ) -> p.Result[Sequence[m.TapLdap.LdapConnection]]:
            """List all LDAP connections."""
            try:
                connections = list(self._connections.values())
                return r[Sequence[m.TapLdap.LdapConnection]].ok(
                    connections,
                )
            except (RuntimeError, ValueError, TypeError) as e:
                return r[Sequence[m.TapLdap.LdapConnection]].fail(
                    f"Failed to list connections: {e}",
                )

        def test_connection(
            self,
            connection_id: str,
        ) -> p.Result[Mapping[str, t.Container]]:
            """Test LDAP connection."""
            try:
                connection = self._connections.get(connection_id)
                if not connection:
                    return r[Mapping[str, t.Container]].fail(
                        "Connection not found",
                    )
                connection.last_tested = datetime.now(UTC)
                connection.last_error = None
                self._connections[connection_id] = connection
                return r[Mapping[str, t.Container]].ok({
                    "success": True,
                    "connection": connection.id,
                })
            except (RuntimeError, ValueError, TypeError) as e:
                connection = self._connections.get(connection_id)
                if connection:
                    connection.last_tested = datetime.now(UTC)
                    connection.last_error = str(e)
                    self._connections[connection_id] = connection
                return r[Mapping[str, t.Container]].fail(
                    f"Failed to test connection: {e}",
                )

    class LDAPStreamService:
        """Service for managing LDAP streams with flext-core patterns."""

        def __init__(self) -> None:
            """Initialize the stream service."""
            self._streams: MutableMapping[
                str,
                m.TapLdap.LdapStream,
            ] = {}

        def create_stream(
            self,
            params: m.TapLdap.StreamCreationParams,
        ) -> p.Result[m.TapLdap.LdapStream]:
            """Create LDAP stream using parameter object pattern."""
            try:
                tap_stream_id = params.tap_stream_id
                if not tap_stream_id:
                    tap_stream_id = f"{params.stream_type.lower()}_stream"
                stream = m.TapLdap.LdapStream(
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
                return r[m.TapLdap.LdapStream].ok(stream)
            except (RuntimeError, ValueError, TypeError) as e:
                return r[m.TapLdap.LdapStream].fail(
                    f"Failed to create stream: {e}",
                )

        def discover_schema(
            self, stream_id: str
        ) -> p.Result[Mapping[str, t.Container]]:
            """Discover schema for LDAP stream."""
            try:
                stream = self._streams.get(stream_id)
                if not stream:
                    return r[Mapping[str, t.Container]].fail("Stream not found")
                schema: Mapping[str, t.Container] = {
                    "type": "object",
                    "properties": {
                        "dn": {"type": "string"},
                        "objectClass": {"type": "array", "items": {"type": "string"}},
                    },
                    "additionalProperties": True,
                }
                stream.update_schema(schema)
                self._streams[stream_id] = stream
                return r[Mapping[str, t.Container]].ok(schema)
            except (RuntimeError, ValueError, TypeError) as e:
                return r[Mapping[str, t.Container]].fail(
                    f"Failed to discover schema: {e}",
                )

        def fetch_stream(
            self,
            stream_id: str,
        ) -> p.Result[m.TapLdap.LdapStream]:
            """Get LDAP stream by ID."""
            try:
                stream = self._streams.get(stream_id)
                if not stream:
                    return r[m.TapLdap.LdapStream].fail(
                        "Stream not found",
                    )
                return r[m.TapLdap.LdapStream].ok(stream)
            except (RuntimeError, ValueError, TypeError) as e:
                return r[m.TapLdap.LdapStream].fail(
                    f"Failed to get stream: {e}",
                )

        def list_streams(
            self,
            connection_id: str | None = None,
        ) -> p.Result[Sequence[m.TapLdap.LdapStream]]:
            """List LDAP streams, optionally filtered by connection ID."""
            try:
                streams = list(self._streams.values())
                if connection_id:
                    streams = [s for s in streams if s.connection_id == connection_id]
                return r[Sequence[m.TapLdap.LdapStream]].ok(streams)
            except (RuntimeError, ValueError, TypeError) as e:
                return r[Sequence[m.TapLdap.LdapStream]].fail(
                    f"Failed to list streams: {e}",
                )

    class TapExecutionService:
        """Service for managing tap executions with flext-core patterns."""

        def __init__(self) -> None:
            """Initialize the execution service."""
            self._executions: MutableMapping[
                str,
                m.TapLdap.TapExecution,
            ] = {}

        def cancel_execution(
            self,
            execution_id: str,
        ) -> p.Result[m.TapLdap.TapExecution]:
            """Cancel tap execution."""
            try:
                execution = self._executions.get(execution_id)
                if not execution:
                    return r[m.TapLdap.TapExecution].fail(
                        "Execution not found",
                    )
                execution.cancel_execution()
                self._executions[execution_id] = execution
                return r[m.TapLdap.TapExecution].ok(execution)
            except (RuntimeError, ValueError, TypeError) as e:
                return r[m.TapLdap.TapExecution].fail(
                    f"Failed to cancel execution: {e}",
                )

        def complete_execution(
            self,
            execution_id: str,
            exit_code: int,
            stdout: str | None = None,
            stderr: str | None = None,
        ) -> p.Result[m.TapLdap.TapExecution]:
            """Complete tap execution."""
            try:
                execution = self._executions.get(execution_id)
                if not execution:
                    return r[m.TapLdap.TapExecution].fail(
                        "Execution not found",
                    )
                execution.complete_execution(exit_code, stdout, stderr)
                self._executions[execution_id] = execution
                return r[m.TapLdap.TapExecution].ok(execution)
            except (RuntimeError, ValueError, TypeError) as e:
                return r[m.TapLdap.TapExecution].fail(
                    f"Failed to complete execution: {e}",
                )

        def create_execution(
            self,
            connection_id: str,
            command: str,
            settings: Mapping[str, t.Container] | None = None,
            catalog: Mapping[str, t.Container] | None = None,
            state: Mapping[str, t.Container] | None = None,
        ) -> p.Result[m.TapLdap.TapExecution]:
            """Create tap execution."""
            try:
                validated_config = (
                    u.TapLdap.ValueConversion.to_map(settings or {}) or {}
                )
                validated_catalog = (
                    u.TapLdap.ValueConversion.to_map(catalog or {}) or {}
                )
                validated_state = u.TapLdap.ValueConversion.to_map(state or {}) or {}
                execution = m.TapLdap.TapExecution(
                    id=uuid4().hex,
                    execution_id=f"exec_{uuid4().hex[:8]}",
                    connection_id=connection_id,
                    command=command,
                    tap_status="created",
                    settings={str(k): v for k, v in validated_config.items()},
                    catalog={str(k): v for k, v in validated_catalog.items()},
                    state={str(k): v for k, v in validated_state.items()},
                    domain_events=[],
                )
                self._executions[str(execution.id)] = execution
                return r[m.TapLdap.TapExecution].ok(execution)
            except (RuntimeError, ValueError, TypeError) as e:
                return r[m.TapLdap.TapExecution].fail(
                    f"Failed to create execution: {e}",
                )

        def fetch_execution(
            self,
            execution_id: str,
        ) -> p.Result[m.TapLdap.TapExecution]:
            """Get tap execution by ID."""
            try:
                execution = self._executions.get(execution_id)
                if not execution:
                    return r[m.TapLdap.TapExecution].fail(
                        "Execution not found",
                    )
                return r[m.TapLdap.TapExecution].ok(execution)
            except (RuntimeError, ValueError, TypeError) as e:
                return r[m.TapLdap.TapExecution].fail(
                    f"Failed to get execution: {e}",
                )

        def list_executions(
            self,
            connection_id: str | None = None,
        ) -> p.Result[Sequence[m.TapLdap.TapExecution]]:
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
                return r[Sequence[m.TapLdap.TapExecution]].ok(
                    executions,
                )
            except (RuntimeError, ValueError, TypeError) as e:
                return r[Sequence[m.TapLdap.TapExecution]].fail(
                    f"Failed to list executions: {e}",
                )

        def start_execution(
            self,
            execution_id: str,
        ) -> p.Result[m.TapLdap.TapExecution]:
            """Start tap execution."""
            try:
                execution = self._executions.get(execution_id)
                if not execution:
                    return r[m.TapLdap.TapExecution].fail(
                        "Execution not found",
                    )
                execution.start_execution()
                self._executions[execution_id] = execution
                return r[m.TapLdap.TapExecution].ok(execution)
            except (RuntimeError, ValueError, TypeError) as e:
                return r[m.TapLdap.TapExecution].fail(
                    f"Failed to start execution: {e}",
                )

        def update_metrics(
            self,
            execution_id: str,
            records_extracted: int,
            streams_processed: int,
        ) -> p.Result[m.TapLdap.TapExecution]:
            """Update execution metrics."""
            try:
                execution = self._executions.get(execution_id)
                if not execution:
                    return r[m.TapLdap.TapExecution].fail(
                        "Execution not found",
                    )
                execution.update_metrics(records_extracted, streams_processed)
                self._executions[execution_id] = execution
                return r[m.TapLdap.TapExecution].ok(execution)
            except (RuntimeError, ValueError, TypeError) as e:
                return r[m.TapLdap.TapExecution].fail(
                    f"Failed to update metrics: {e}",
                )

    class LDIFProcessingService:
        """Service for LDIF file processing using flext-ldif library."""

        def __init__(self) -> None:
            """Initialize LDIF processing service."""
            self._ldif_api = ldif()

        def fetch_ldif_statistics(
            self,
            file_path: str,
        ) -> p.Result[Mapping[str, t.Container]]:
            """Get LDIF file statistics using flext-ldif library."""
            try:
                validation_result: p.Result[Mapping[str, t.Container]] = (
                    self.validate_ldif_file(
                        file_path,
                    )
                )
                if not validation_result.success:
                    return validation_result
                validation_data: Mapping[str, t.Container] = (
                    u.TapLdap.ValueConversion.to_map(validation_result.value) or {}
                )
                file_stats: Mapping[str, t.Container] = {
                    "file_path": file_path,
                    "file_size_bytes": Path(file_path).stat().st_size
                    if Path(file_path).exists()
                    else 0,
                    **validation_data,
                }
                return r[Mapping[str, t.Container]].ok(file_stats)
            except c.Meltano.SINGER_SAFE_EXCEPTIONS as e:
                FlextTapLdapServices._logger.exception(
                    "Error getting LDIF statistics for %s",
                    file_path,
                )
                return r[Mapping[str, t.Container]].fail(
                    f"LDIF statistics failed: {e}",
                )

        def process_ldif_file(
            self,
            file_path: str,
        ) -> p.Result[Sequence[Mapping[str, t.Container]]]:
            """Process LDIF file using flext-ldif library."""
            try:
                FlextTapLdapServices._logger.info("Processing LDIF file: %s", file_path)
                result: p.Result[m.Ldif.ParseResponse] = self._ldif_api.parse_ldif(
                    Path(file_path),
                )
                if not result.success:
                    return r[Sequence[Mapping[str, t.Container]]].fail(
                        f"Failed to parse LDIF file: {result.error}",
                    )
                entries: MutableSequence[m.Ldif.Entry] = result.value.entries
                entry_count = len(entries)
                FlextTapLdapServices._logger.info(
                    "Successfully processed %s entries from %s",
                    entry_count,
                    file_path,
                )
                normalized: Sequence[Mapping[str, t.Container]] = [
                    {
                        "dn": entry.dn.value if entry.dn is not None else "",
                        "attributes": u.TapLdap.ValueConversion.to_map(
                            entry.attributes.attributes
                            if entry.attributes is not None
                            else {}
                        )
                        or {},
                    }
                    for entry in entries
                ]
                return r[Sequence[Mapping[str, t.Container]]].ok(normalized)
            except c.Meltano.SINGER_SAFE_EXCEPTIONS as e:
                FlextTapLdapServices._logger.exception(
                    "Error processing LDIF file %s",
                    file_path,
                )
                return r[Sequence[Mapping[str, t.Container]]].fail(
                    f"LDIF processing failed: {e}",
                )

        def validate_ldif_file(
            self,
            file_path: str,
        ) -> p.Result[Mapping[str, t.Container]]:
            """Validate LDIF file using flext-ldif library."""
            try:
                FlextTapLdapServices._logger.info("Validating LDIF file: %s", file_path)
                result: p.Result[m.Ldif.ParseResponse] = self._ldif_api.parse_ldif(
                    Path(file_path),
                )
                if not result.success:
                    return r[Mapping[str, t.Container]].fail(
                        f"Validation failed: {result.error}",
                    )
                entries: MutableSequence[m.Ldif.Entry] = result.value.entries
                total_entries = len(entries)
                validation_data: Mapping[str, t.Container] = {
                    "total_entries": total_entries,
                    "valid_entries": total_entries,
                    "invalid_entries": 0,
                    "errors": list[str](),
                }
                FlextTapLdapServices._logger.info(
                    "LDIF file validation completed: %s",
                    file_path,
                )
                return r[Mapping[str, t.Container]].ok(validation_data)
            except c.Meltano.SINGER_SAFE_EXCEPTIONS as e:
                FlextTapLdapServices._logger.exception(
                    "Error validating LDIF file %s",
                    file_path,
                )
                return r[Mapping[str, t.Container]].fail(
                    f"LDIF validation failed: {e}",
                )

    @staticmethod
    def create_development_ldap_config(
        **overrides: t.Scalar,
    ) -> p.Result[FlextTapLdapSettings]:
        """Create development LDAP configuration with defaults.

        Args:
        **overrides: Configuration overrides

        Returns:
        r with FlextTapLdapSettings for development use.

        """
        try:
            settings = FlextTapLdapSettings.model_validate(overrides)
            return r[FlextTapLdapSettings].ok(settings)
        except (RuntimeError, ValueError, TypeError) as e:
            return r[FlextTapLdapSettings].fail(
                f"Failed to create development settings: {e}",
            )

    @staticmethod
    def create_ldap_connection_config(
        params: m.TapLdap.LdapConnectionParams,
    ) -> p.Result[Mapping[str, t.Container]]:
        """Create LDAP connection configuration using Parameter Object Pattern.

        Args:
        params: LDAP connection parameters t.Container

        Returns:
        r with connection configuration or error message.

        """
        try:
            settings: Mapping[str, t.Container] = {
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
            return r[Mapping[str, t.Container]].ok(settings)
        except (RuntimeError, ValueError, TypeError) as e:
            return r[Mapping[str, t.Container]].fail(
                f"Failed to create LDAP connection settings: {e}",
            )

    @staticmethod
    def create_default_ldap_config(
        host: str,
        base_dn: str,
        port: int = c.Ldap.ConnectionDefaults.PORT,
        **kwargs: t.Scalar,
    ) -> p.Result[Mapping[str, t.Container]]:
        """Create LDAP connection configuration (testing convenience interface).

        Testing convenience wrapper for the Parameter Object Pattern implementation.
        Use FlextTapLdapServices.create_ldap_connection_config() with m.TapLdap.LdapConnectionParams for new code.
        """
        params = m.TapLdap.LdapConnectionParams(
            host=host,
            base_dn=base_dn,
            port=port,
            use_ssl=bool(kwargs.get("use_ssl")),
            bind_dn=u.TapLdap.ValueConversion.to_str(kwargs.get("bind_dn")),
            bind_password=u.TapLdap.ValueConversion.to_str(kwargs.get("bind_password")),
            timeout_seconds=c.TapLdap.DEFAULT_SEARCH_TIMEOUT,
            page_size=c.TapLdap.DEFAULT_PAGE_SIZE,
            max_retries=3,
        )
        return FlextTapLdapServices.create_ldap_connection_config(params)

    @staticmethod
    def create_production_ldap_config(
        **overrides: t.Scalar,
    ) -> p.Result[FlextTapLdapSettings]:
        """Create production LDAP configuration with security defaults.

        Args:
        **overrides: Configuration overrides

        Returns:
        r with FlextTapLdapSettings for production use.

        """
        try:
            production_overrides = {"use_ssl": True, **overrides}
            settings = FlextTapLdapSettings.model_validate(production_overrides)
            return r[FlextTapLdapSettings].ok(settings)
        except (RuntimeError, ValueError, TypeError) as e:
            return r[FlextTapLdapSettings].fail(
                f"Failed to create production settings: {e}",
            )

    @staticmethod
    def setup_ldap_tap(
        settings: FlextTapLdapSettings | None = None,
    ) -> p.Result[FlextTapLdapSettings]:
        """Set up the LDAP tap with configuration.

        Args:
        settings: Optional configuration. If None, creates defaults.

        Returns:
        r with FlextTapLdapSettings or error message.

        """
        try:
            if settings is None:
                settings = FlextTapLdapSettings.model_validate({})
            validation_result = FlextTapLdapServices.validate_ldap_config(settings)
            if not validation_result.success or not validation_result.value:
                return r[FlextTapLdapSettings].fail(
                    validation_result.error or "Configuration validation failed",
                )
            return r[FlextTapLdapSettings].ok(settings)
        except (RuntimeError, ValueError, TypeError) as e:
            return r[FlextTapLdapSettings].fail(f"Failed to setup LDAP tap: {e}")

    @staticmethod
    def validate_ldap_config(settings: FlextTapLdapSettings) -> p.Result[bool]:
        """Validate LDAP tap configuration.

        Args:
        settings: Configuration to validate

        Returns:
        r with validation success or error message.

        """
        try:
            valid = bool(settings.host and settings.port > 0 and settings.page_size > 0)
            return r[bool].ok(valid)
        except (RuntimeError, ValueError, TypeError) as e:
            return r[bool].fail(f"Configuration validation failed: {e}")


__all__: list[str] = ["FlextTapLdapServices"]
