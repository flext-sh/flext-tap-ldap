"""Application services for FLEXT-TAP-LDAP v0.7.0.

REFACTORED:
Uses flext-core service patterns - NO duplication. Clean architecture.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from flext_core import (
    FlextEntityId,
    FlextResult,
)

from flext_tap_ldap.domain.entities import (
    LDAPConnection,
    LDAPRecord,
    LDAPStream,
    TapExecution,
)


@dataclass
class LDAPConnectionParams:
    """Parameter object for LDAP connection creation.

    Implements Parameter Object Pattern to reduce parameter count
    and improve maintainability following SOLID principles.
    """

    host: str
    port: int = 389
    bind_dn: str | None = None
    bind_password: str | None = None
    base_dn: str = ""
    use_ssl: bool = False
    use_tls: bool = False
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

    connection_id: UUID
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


class LDAPConnectionService:
    """Service for managing LDAP connections."""

    def __init__(self) -> None:
      """Initialize the connection service."""
      self._connections: dict[
          FlextEntityId,
          LDAPConnection,
      ] = {}  # Initialized inline for immediate availability

    async def create_connection(
      self,
      params: LDAPConnectionParams,
    ) -> FlextResult[LDAPConnection]:
      """Create LDAP connection using parameter object pattern.

      Refactored to use Parameter Object Pattern, reducing complexity
      and improving maintainability following SOLID principles.
      """
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

          self._connections[connection.id] = connection
          return FlextResult.ok(connection)
      except (RuntimeError, ValueError, TypeError) as e:
          return FlextResult.fail(f"Failed to create connection: {e}")

    async def test_connection(
      self,
      connection_id: UUID,
    ) -> FlextResult[dict[str, object]]:
      """Test LDAP connection."""
      try:
          connection = self._connections.get(connection_id)
          if not connection:
              return FlextResult.fail("Connection not found")

          # Here you would actually test the LDAP connection
          # For now, we just mark it as tested
          connection.last_tested = datetime.now(UTC)
          return FlextResult.ok({"success": True})
      except (RuntimeError, ValueError, TypeError) as e:
          connection = self._connections.get(connection_id)
          if connection:
              connection.last_error = str(e)
          return FlextResult.fail(f"Failed to test connection: {e}")

    async def get_connection(
      self,
      connection_id: UUID,
    ) -> FlextResult[LDAPConnection | None]:
      """Get LDAP connection by ID."""
      try:
          connection = self._connections.get(connection_id)
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
    """Service for managing LDAP streams."""

    def __init__(self) -> None:
      """Initialize the stream service."""
      self._streams: dict[
          FlextEntityId,
          LDAPStream,
      ] = {}  # Initialized inline for immediate availability

    async def create_stream(
      self,
      params: StreamCreationParams,
    ) -> FlextResult[LDAPStream]:
      """Create LDAP stream using parameter object pattern.

      Refactored to use Parameter Object Pattern to reduce parameter count
      and improve maintainability following SOLID principles.
      """
      try:
          # Generate tap_stream_id if not provided
          tap_stream_id = params.tap_stream_id
          if not tap_stream_id:
              tap_stream_id = f"{params.stream_type.lower()}_stream"

          stream = LDAPStream(
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

          self._streams[stream.id] = stream
          return FlextResult.ok(stream)
      except (RuntimeError, ValueError, TypeError) as e:
          return FlextResult.fail(f"Failed to create stream: {e}")

    async def discover_schema(self, stream_id: UUID) -> FlextResult[dict[str, object]]:
      """Discover schema for LDAP stream."""
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

    async def get_stream(self, stream_id: UUID) -> FlextResult[LDAPStream | None]:
      """Get LDAP stream by ID."""
      try:
          stream = self._streams.get(stream_id)
          return FlextResult.ok(stream)
      except (RuntimeError, ValueError, TypeError) as e:
          return FlextResult.fail(f"Failed to get stream: {e}")

    async def list_streams(
      self,
      connection_id: UUID | None = None,
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
    """Service for managing tap executions."""

    def __init__(self) -> None:
      """Initialize the execution service."""
      self._executions: dict[
          UUID,
          TapExecution,
      ] = {}  # Initialized inline for immediate availability

    async def create_execution(
      self,
      connection_id: UUID,
      command: str,
      config: dict[str, object] | None = None,
      catalog: dict[str, object] | None = None,
      state: dict[str, object] | None = None,
    ) -> FlextResult[TapExecution]:
      """Create tap execution."""
      try:
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

    async def start_execution(
      self,
      execution_id: UUID,
    ) -> FlextResult[TapExecution]:
      """Start tap execution."""
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
    ) -> FlextResult[TapExecution]:
      """Complete tap execution."""
      try:
          execution = self._executions.get(execution_id)
          if not execution:
              return FlextResult.fail("Execution not found")

          execution.complete_execution(exit_code, stdout, stderr)
          return FlextResult.ok(execution)
      except (RuntimeError, ValueError, TypeError) as e:
          return FlextResult.fail(f"Failed to complete execution: {e}")

    async def cancel_execution(
      self,
      execution_id: UUID,
    ) -> FlextResult[TapExecution]:
      """Cancel tap execution."""
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
    ) -> FlextResult[TapExecution]:
      """Update execution metrics."""
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
    ) -> FlextResult[TapExecution | None]:
      """Get tap execution by ID."""
      try:
          execution = self._executions.get(execution_id)
          return FlextResult.ok(execution)
      except (RuntimeError, ValueError, TypeError) as e:
          return FlextResult.fail(f"Failed to get execution: {e}")

    async def list_executions(
      self,
      connection_id: UUID | None = None,
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
    """Service for managing LDAP records."""

    def __init__(self) -> None:
      """Initialize the record service."""
      self._records: dict[
          UUID,
          LDAPRecord,
      ] = {}  # Initialized inline for immediate availability

    async def create_record(
      self,
      stream_id: UUID,
      execution_id: UUID,
      dn: str,
      attributes: dict[str, object],
      object_class: list[str] | None = None,
    ) -> FlextResult[LDAPRecord]:
      """Create LDAP record."""
      try:
          record = LDAPRecord(
              stream_id=stream_id,
              execution_id=execution_id,
              dn=dn,
              attributes=attributes,
              object_class=object_class or [],
              singer_record={},  # Will be set later
          )

          # Generate Singer record
          singer_res = record.to_singer_record()
          if singer_res.is_failure or singer_res.data is None:
              return FlextResult.fail(
                  singer_res.error or "Failed to build singer record",
              )
          record.singer_record = singer_res.data

          self._records[record.id] = record
          return FlextResult.ok(record)
      except (RuntimeError, ValueError, TypeError) as e:
          return FlextResult.fail(f"Failed to create record: {e}")

    async def get_record(self, record_id: UUID) -> FlextResult[LDAPRecord | None]:
      """Get LDAP record by ID."""
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
      stream_id: UUID | None = None,
      execution_id: UUID | None = None,
    ) -> FlextResult[dict[str, object]]:
      """Count LDAP records, optionally filtered by stream or execution ID."""
      try:
          records = list(self._records.values())

          if stream_id:
              records = [r for r in records if r.stream_id == stream_id]

          if execution_id:
              records = [r for r in records if r.execution_id == execution_id]

          return FlextResult.ok({"count": len(records)})
      except (RuntimeError, ValueError, TypeError) as e:
          return FlextResult.fail(f"Failed to count records: {e}")
