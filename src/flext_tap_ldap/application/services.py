"""Application services for FLEXT-TAP-LDAP v0.7.0.

REFACTORED:
Uses flext-core service patterns - NO duplication. Clean architecture.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

# Import from flext-core for foundational patterns (standardized)
from flext_core import (
    FlextResult,
)

if TYPE_CHECKING:
    from uuid import UUID

    from flext_tap_ldap.domain.entities import (
        LDAPConnection,
        LDAPRecord,
        LDAPStream,
        TapExecution,
    )


class LDAPConnectionService:
    """Service for managing LDAP connections."""

    def __init__(self) -> None:
        self._connections: dict[
            UUID,
            LDAPConnection,
        ] = {}  # Initialized inline for immediate availability

    async def create_connection(
        self,
        host: str,
        port: int = 389,
        bind_dn: str | None = None,
        bind_password: str | None = None,
        *,
        base_dn: str = "",
        use_ssl: bool = False,
        use_tls: bool = False,
        timeout_seconds: int = 30,
        page_size: int = 1000,
        max_retries: int = 3,
    ) -> FlextResult[Any]:
        try:
            from flext_tap_ldap.domain.entities import LDAPConnection

            connection = LDAPConnection(
                host=host,
                port=port,
                bind_dn=bind_dn,
                password=bind_password,
                use_ssl=use_ssl,
                timeout=timeout_seconds,
            )

            self._connections[connection.id] = connection
            return FlextResult.ok(connection)
        except (RuntimeError, ValueError, TypeError) as e:
            return FlextResult.fail(f"Failed to create connection: {e}")

    async def test_connection(self, connection_id: UUID) -> FlextResult[Any]:
        try:
            connection = self._connections.get(connection_id)
            if not connection:
                return FlextResult.fail("Connection not found")

            # Here you would actually test the LDAP connection
            # For now, we just mark it as tested
            connection.last_tested = datetime.now()
            return FlextResult.ok(True)
        except (RuntimeError, ValueError, TypeError) as e:
            connection = self._connections.get(connection_id)
            if connection:
                connection.last_error = str(e)
            return FlextResult.fail(f"Failed to test connection: {e}")

    async def get_connection(
        self,
        connection_id: UUID,
    ) -> FlextResult[Any]:
        try:
            connection = self._connections.get(connection_id)
            return FlextResult.ok(connection)
        except (RuntimeError, ValueError, TypeError) as e:
            return FlextResult.fail(f"Failed to get connection: {e}")

    async def list_connections(self) -> FlextResult[Any]:
        try:
            connections = list(self._connections.values())
            return FlextResult.ok(connections)
        except (RuntimeError, ValueError, TypeError) as e:
            return FlextResult.fail(f"Failed to list connections: {e}")


class LDAPStreamService:
    """Service for managing LDAP streams."""

    def __init__(self) -> None:
        self._streams: dict[
            UUID,
            LDAPStream,
        ] = {}  # Initialized inline for immediate availability

    async def create_stream(
        self,
        connection_id: UUID,
        stream_type: str,
        search_filter: str,
        attributes: list[str] | None = None,
        tap_stream_id: str | None = None,
        key_properties: list[str] | None = None,
        replication_method: str = "FULL_TABLE",
        replication_key: str | None = None,
    ) -> FlextResult[Any]:
        try:
            from flext_tap_ldap.domain.entities import LDAPStream

            # Generate tap_stream_id if not provided
            if not tap_stream_id:
                tap_stream_id = f"{stream_type.lower()}_stream"

            stream = LDAPStream(
                connection_id=connection_id,
                stream_type=stream_type.lower(),
                search_filter=search_filter,
                attributes=attributes or [],
                tap_stream_id=tap_stream_id,
                key_properties=key_properties or ["dn"],
                replication_method=replication_method,
                replication_key=replication_key,
                stream_schema={},
            )

            self._streams[stream.id] = stream
            return FlextResult.ok(stream)
        except (RuntimeError, ValueError, TypeError) as e:
            return FlextResult.fail(f"Failed to create stream: {e}")

    async def discover_schema(self, stream_id: UUID) -> FlextResult[Any]:
        try:
            stream = self._streams.get(stream_id)
            if not stream:
                return FlextResult.fail("Stream not found")

            # Here you would actually discover the schema from LDAP
            # For now, return a basic schema
            schema = {
                "type": "object",
                "properties": {
                    "dn": {"type": "string"},
                    "objectClass": {"type": "array", "items": {"type": "string"}},
                },
                "additionalProperties": True,
            }

            stream.update_schema(schema)
            return FlextResult.ok(schema)
        except (RuntimeError, ValueError, TypeError) as e:
            return FlextResult.fail(f"Failed to discover schema: {e}")

    async def get_stream(self, stream_id: UUID) -> FlextResult[Any]:
        try:
            stream = self._streams.get(stream_id)
            return FlextResult.ok(stream)
        except (RuntimeError, ValueError, TypeError) as e:
            return FlextResult.fail(f"Failed to get stream: {e}")

    async def list_streams(
        self,
        connection_id: UUID | None = None,
    ) -> FlextResult[Any]:
        try:
            streams = list(self._streams.values())

            if connection_id:
                streams = [s for s in streams if s.connection_id == connection_id]

            return FlextResult.ok(streams)
        except (RuntimeError, ValueError, TypeError) as e:
            return FlextResult.fail(f"Failed to list streams: {e}")


class TapExecutionService:
    """Service for managing tap executions."""

    def __init__(self) -> None:
        self._executions: dict[
            UUID,
            TapExecution,
        ] = {}  # Initialized inline for immediate availability

    async def create_execution(
        self,
        connection_id: UUID,
        command: str,
        config: dict[str, Any] | None = None,
        catalog: dict[str, Any] | None = None,
        state: dict[str, Any] | None = None,
    ) -> FlextResult[Any]:
        try:
            from flext_tap_ldap.domain.entities import TapExecution

            execution = TapExecution(
                connection_id=connection_id,
                command=command,
                tap_status="created",
                config=config or {},
                catalog=catalog or {},
                state=state or {},
            )

            self._executions[execution.id] = execution
            return FlextResult.ok(execution)
        except (RuntimeError, ValueError, TypeError) as e:
            return FlextResult.fail(f"Failed to create execution: {e}")

    async def start_execution(self, execution_id: UUID) -> FlextResult[Any]:
        try:
            execution = self._executions.get(execution_id)
            if not execution:
                return FlextResult.fail("Execution not found")

            execution.start_execution()
            return FlextResult.ok(execution)
        except (RuntimeError, ValueError, TypeError) as e:
            return FlextResult.fail(f"Failed to start execution: {e}")

    async def complete_execution(
        self,
        execution_id: UUID,
        exit_code: int,
        stdout: str | None = None,
        stderr: str | None = None,
    ) -> FlextResult[Any]:
        try:
            execution = self._executions.get(execution_id)
            if not execution:
                return FlextResult.fail("Execution not found")

            execution.complete_execution(exit_code, stdout, stderr)
            return FlextResult.ok(execution)
        except (RuntimeError, ValueError, TypeError) as e:
            return FlextResult.fail(f"Failed to complete execution: {e}")

    async def cancel_execution(self, execution_id: UUID) -> FlextResult[Any]:
        try:
            execution = self._executions.get(execution_id)
            if not execution:
                return FlextResult.fail("Execution not found")

            execution.cancel_execution()
            return FlextResult.ok(execution)
        except (RuntimeError, ValueError, TypeError) as e:
            return FlextResult.fail(f"Failed to cancel execution: {e}")

    async def update_metrics(
        self,
        execution_id: UUID,
        records_extracted: int,
        streams_processed: int,
    ) -> FlextResult[Any]:
        try:
            execution = self._executions.get(execution_id)
            if not execution:
                return FlextResult.fail("Execution not found")

            execution.update_metrics(records_extracted, streams_processed)
            return FlextResult.ok(execution)
        except (RuntimeError, ValueError, TypeError) as e:
            return FlextResult.fail(f"Failed to update metrics: {e}")

    async def get_execution(
        self,
        execution_id: UUID,
    ) -> FlextResult[Any]:
        try:
            execution = self._executions.get(execution_id)
            return FlextResult.ok(execution)
        except (RuntimeError, ValueError, TypeError) as e:
            return FlextResult.fail(f"Failed to get execution: {e}")

    async def list_executions(
        self,
        connection_id: UUID | None = None,
    ) -> FlextResult[Any]:
        try:
            executions = list(self._executions.values())

            if connection_id:
                executions = [e for e in executions if e.connection_id == connection_id]

            # Sort by started_at descending
            executions.sort(
                key=lambda e: e.started_at or e.id.time_mid,
                reverse=True,
            )

            return FlextResult.ok(executions)
        except (RuntimeError, ValueError, TypeError) as e:
            return FlextResult.fail(f"Failed to list executions: {e}")


class LDAPRecordService:
    """Service for managing LDAP records."""

    def __init__(self) -> None:
        self._records: dict[
            UUID,
            LDAPRecord,
        ] = {}  # Initialized inline for immediate availability

    async def create_record(
        self,
        stream_id: UUID,
        execution_id: UUID,
        dn: str,
        attributes: dict[str, Any],
        object_class: list[str] | None = None,
    ) -> FlextResult[Any]:
        try:
            from flext_tap_ldap.domain.entities import LDAPRecord

            record = LDAPRecord(
                stream_id=stream_id,
                execution_id=execution_id,
                dn=dn,
                attributes=attributes,
                object_class=object_class or [],
                singer_record={},  # Will be set later
            )

            # Generate Singer record
            record.singer_record = record.to_singer_record()

            self._records[record.id] = record
            return FlextResult.ok(record)
        except (RuntimeError, ValueError, TypeError) as e:
            return FlextResult.fail(f"Failed to create record: {e}")

    async def get_record(self, record_id: UUID) -> FlextResult[Any]:
        try:
            record = self._records.get(record_id)
            return FlextResult.ok(record)
        except (RuntimeError, ValueError, TypeError) as e:
            return FlextResult.fail(f"Failed to get record: {e}")

    async def list_records(
        self,
        stream_id: UUID | None = None,
        execution_id: UUID | None = None,
        limit: int = 100,
    ) -> FlextResult[Any]:
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
        stream_id: UUID | None = None,
        execution_id: UUID | None = None,
    ) -> FlextResult[Any]:
        try:
            records = list(self._records.values())

            if stream_id:
                records = [r for r in records if r.stream_id == stream_id]

            if execution_id:
                records = [r for r in records if r.execution_id == execution_id]

            return FlextResult.ok(len(records))
        except (RuntimeError, ValueError, TypeError) as e:
            return FlextResult.fail(f"Failed to count records: {e}")
