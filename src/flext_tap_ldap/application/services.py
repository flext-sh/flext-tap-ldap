from typing import Any

"""Application services for FLEXT-TAP-LDAP v0.7.0.

REFACTORED:
            Using flext-core service patterns - NO duplication.  Clean architecture with dependency injection and ServiceResult pattern.  """

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.config import injectable
from flext_core.domain.types import ServiceResult

if TYPE_CHECKING:
    from uuid import UUID

    from flext_tap_ldap.domain.entities import LDAPConnection
    from flext_tap_ldap.domain.entities import LDAPRecord
    from flext_tap_ldap.domain.entities import LDAPStream
    from flext_tap_ldap.domain.entities import TapExecution


@injectable()
class LDAPConnectionService:
    """Service for managing LDAP connections."""

    def __init__(self) -> None:
        self._connections: dict[UUID, LDAPConnection] = {}  # TODO: Initialize in __post_init__

    async def create_connection(self, host: str, port: int = 389, bind_dn: str | None = None, bind_password: str | None = None, base_dn: str = "", use_ssl: bool = False, use_tls: bool = False, timeout: int = 30, page_size: int = 1000, max_retries: int = 3) -> ServiceResult[LDAPConnection]:
        try:
            from flext_tap_ldap.domain.entities import LDAPConnection

            connection = LDAPConnection(
                name=f"LDAP connection to {host}:{port}",
                description=f"Connection to {host}:{port} with base DN {base_dn}",
                host=host,
                port=port,
                bind_dn=bind_dn,
                bind_password=bind_password,
                base_dn=base_dn,
                use_ssl=use_ssl,
                use_tls=use_tls,
                timeout=timeout,
                page_size=page_size,
                max_retries=max_retries,
            )

            self._connections[connection.id] = connection
            return ServiceResult.ok(connection)
        except Exception as e:
            return ServiceResult.fail(f"Failed to create connection: {e}")

    async def test_connection(self, connection_id: UUID) -> ServiceResult[bool]:
        try:
            connection = self._connections.get(connection_id)
            if not connection:
                return ServiceResult.fail("Connection not found")

            # Here you would actually test the LDAP connection
            # For now, we just mark it as tested
            connection.test_connection()
            return ServiceResult.ok(True)
        except Exception as e:
            connection = self._connections.get(connection_id)
            if connection:
                connection.last_error = str(e)
            return ServiceResult.fail(f"Failed to test connection: {e}")

    async def get_connection(self, connection_id: UUID) -> ServiceResult[LDAPConnection | None]:
        try:
            connection = self._connections.get(connection_id)
            return ServiceResult.ok(connection)
        except Exception as e:
            return ServiceResult.fail(f"Failed to get connection: {e}")

    async def list_connections(self) -> ServiceResult[list[LDAPConnection]]:
        try:
            connections = list(self._connections.values())
            return ServiceResult.ok(connections)
        except Exception as e:
            return ServiceResult.fail(f"Failed to list connections: {e}")


@injectable()
class LDAPStreamService:
    """Service for managing LDAP streams."""

    def __init__(self) -> None:
        self._streams: dict[UUID, LDAPStream] = {}  # TODO: Initialize in __post_init__

    async def create_stream(self, connection_id: UUID, stream_type: str, search_filter: str, attributes: list[str] | None = None, tap_stream_id: str | None = None, key_properties: list[str] | None = None, replication_method: str = "FULL_TABLE", replication_key: str | None = None) -> ServiceResult[LDAPStream]:
        try:
            from flext_tap_ldap.domain.entities import LDAPStream
            from flext_tap_ldap.domain.entities import StreamType

            # Generate tap_stream_id if not provided
            if not tap_stream_id:
                tap_stream_id = f"{stream_type.lower()}_stream"

            stream = LDAPStream(
                name=f"LDAP {stream_type} stream",
                description=f"Extracts {stream_type} from LDAP",
                connection_id=connection_id,
                stream_type=StreamType(stream_type.lower()),
                search_filter=search_filter,
                attributes=attributes or [],
                tap_stream_id=tap_stream_id,
                key_properties=key_properties or ["dn"],
                replication_method=replication_method,
                replication_key=replication_key,
            )

            self._streams[stream.id] = stream
            return ServiceResult.ok(stream)
        except Exception as e:
            return ServiceResult.fail(f"Failed to create stream: {e}")

    async def discover_schema(self, stream_id: UUID) -> ServiceResult[dict[str, Any]]:
        try:
            stream = self._streams.get(stream_id)
            if not stream:
                return ServiceResult.fail("Stream not found")

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
            return ServiceResult.ok(schema)
        except Exception as e:
            return ServiceResult.fail(f"Failed to discover schema: {e}")

    async def get_stream(self, stream_id: UUID) -> ServiceResult[LDAPStream | None]:
        try:
            stream = self._streams.get(stream_id)
            return ServiceResult.ok(stream)
        except Exception as e:
            return ServiceResult.fail(f"Failed to get stream: {e}")

    async def list_streams(self, connection_id: UUID | None = None) -> ServiceResult[list[LDAPStream]]:
        try:
            streams = list(self._streams.values())

            if connection_id:
                streams = [s for s in streams if s.connection_id == connection_id]

            return ServiceResult.ok(streams)
        except Exception as e:
            return ServiceResult.fail(f"Failed to list streams: {e}")


@injectable()
class TapExecutionService:
    """Service for managing tap executions."""

    def __init__(self) -> None:
        self._executions: dict[UUID, TapExecution] = {}  # TODO: Initialize in __post_init__

    async def create_execution(self, connection_id: UUID, command: str, config: dict[str, Any] | None = None, catalog: dict[str, Any] | None = None, state: dict[str, Any] | None = None) -> ServiceResult[TapExecution]:
        try:
            from flext_tap_ldap.domain.entities import TapExecution

            execution = TapExecution(
                name=f"Tap execution for connection {connection_id}",
                description="LDAP data extraction execution",
                connection_id=connection_id,
                command=command,
                config=config or {},
                catalog=catalog or {},
                state=state or {},
            )

            self._executions[execution.id] = execution
            return ServiceResult.ok(execution)
        except Exception as e:
            return ServiceResult.fail(f"Failed to create execution: {e}")

    async def start_execution(self, execution_id: UUID) -> ServiceResult[TapExecution]:
        try:
            execution = self._executions.get(execution_id)
            if not execution:
                return ServiceResult.fail("Execution not found")

            execution.start_execution()
            return ServiceResult.ok(execution)
        except Exception as e:
            return ServiceResult.fail(f"Failed to start execution: {e}")

    async def complete_execution(self, execution_id: UUID, exit_code: int, stdout: str | None = None, stderr: str | None = None) -> ServiceResult[TapExecution]:
        try:
            execution = self._executions.get(execution_id)
            if not execution:
                return ServiceResult.fail("Execution not found")

            execution.complete_execution(exit_code, stdout, stderr)
            return ServiceResult.ok(execution)
        except Exception as e:
            return ServiceResult.fail(f"Failed to complete execution: {e}")

    async def cancel_execution(self, execution_id: UUID) -> ServiceResult[TapExecution]:
        try:
            execution = self._executions.get(execution_id)
            if not execution:
                return ServiceResult.fail("Execution not found")

            execution.cancel_execution()
            return ServiceResult.ok(execution)
        except Exception as e:
            return ServiceResult.fail(f"Failed to cancel execution: {e}")

    async def update_metrics(self, execution_id: UUID, records_extracted: int, streams_processed: int) -> ServiceResult[TapExecution]:
        try:
            execution = self._executions.get(execution_id)
            if not execution:
                return ServiceResult.fail("Execution not found")

            execution.update_metrics(records_extracted, streams_processed)
            return ServiceResult.ok(execution)
        except Exception as e:
            return ServiceResult.fail(f"Failed to update metrics: {e}")

    async def get_execution(self, execution_id: UUID) -> ServiceResult[TapExecution | None]:
        try:
            execution = self._executions.get(execution_id)
            return ServiceResult.ok(execution)
        except Exception as e:
            return ServiceResult.fail(f"Failed to get execution: {e}")

    async def list_executions(self, connection_id: UUID | None = None) -> ServiceResult[list[TapExecution]]:
        try:
            executions = list(self._executions.values())

            if connection_id:
                executions = [e for e in executions if e.connection_id == connection_id]

            # Sort by started_at descending
            executions.sort(
                key=lambda e: e.started_at or e.created_at,
                reverse=True,
            )

            return ServiceResult.ok(executions)
        except Exception as e:
            return ServiceResult.fail(f"Failed to list executions: {e}")


@injectable()
class LDAPRecordService:
    """Service for managing LDAP records."""

    def __init__(self) -> None:
        self._records: dict[UUID, LDAPRecord] = {}  # TODO: Initialize in __post_init__

    async def create_record(self, stream_id: UUID, execution_id: UUID, dn: str, attributes: dict[str, Any], object_class: list[str] | None = None) -> ServiceResult[LDAPRecord]:
        try:
            from flext_tap_ldap.domain.entities import LDAPRecord

            record = LDAPRecord(
                name=f"LDAP record {dn}",
                description=f"Record from LDAP with DN {dn}",
                stream_id=stream_id,
                execution_id=execution_id,
                dn=dn,
                attributes=attributes,
                object_class=object_class or [],
            )

            # Generate Singer record
            record.singer_record = record.to_singer_record()

            self._records[record.id] = record
            return ServiceResult.ok(record)
        except Exception as e:
            return ServiceResult.fail(f"Failed to create record: {e}")

    async def get_record(self, record_id: UUID) -> ServiceResult[LDAPRecord | None]:
        try:
            record = self._records.get(record_id)
            return ServiceResult.ok(record)
        except Exception as e:
            return ServiceResult.fail(f"Failed to get record: {e}")

    async def list_records(self, stream_id: UUID | None = None, execution_id: UUID | None = None, limit: int = 100) -> ServiceResult[list[LDAPRecord]]:
        try:
            records = list(self._records.values())

            if stream_id:
                records = [r for r in records if r.stream_id == stream_id]

            if execution_id:
                records = [r for r in records if r.execution_id == execution_id]

            # Sort by extracted_at descending
            records.sort(key=lambda r: r.extracted_at, reverse=True)

            return ServiceResult.ok(records[:limit])
        except Exception as e:
            return ServiceResult.fail(f"Failed to list records: {e}")

    async def count_records(self, stream_id: UUID | None = None, execution_id: UUID | None = None) -> ServiceResult[int]:
        try:
            records = list(self._records.values())

            if stream_id:
                records = [r for r in records if r.stream_id == stream_id]

            if execution_id:
                records = [r for r in records if r.execution_id == execution_id]

            return ServiceResult.ok(len(records))
        except Exception as e:
            return ServiceResult.fail(f"Failed to count records: {e}")
