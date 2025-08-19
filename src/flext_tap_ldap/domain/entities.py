"""Domain entities for tap-ldap using flext-core patterns."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from flext_core import (
    FlextEntity,
    FlextEntityId,
    FlextModel,
    FlextResult,
    get_logger,
)
from pydantic import Field

# Constants
MAX_PORT = 65535

logger = get_logger(__name__)


class LDAPConnection(FlextEntity):
    """LDAP connection entity using FlextEntity pattern."""

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate LDAP connection business rules."""
        if not self.host:
            return FlextResult[None].fail("Host is required")
        if self.port <= 0 or self.port > MAX_PORT:
            return FlextResult[None].fail(f"Port must be between 1 and {MAX_PORT}")
        if self.timeout <= 0:
            return FlextResult[None].fail("Timeout must be positive")
        if self.pool_size <= 0:
            return FlextResult[None].fail("Pool size must be positive")
        return FlextResult[None].ok(None)

    id: FlextEntityId = Field(default_factory=lambda: FlextEntityId(str(uuid4())))
    host: str
    port: int
    bind_dn: str | None = None
    password: str | None = None
    use_ssl: bool = False
    timeout: int = 30
    pool_size: int = 5
    is_active: bool = True
    last_tested: datetime | None = None
    last_error: str | None = None


class LDAPStream(FlextEntity):
    """LDAP stream entity using FlextEntity pattern."""

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate LDAP stream business rules."""
        if not self.stream_type:
            return FlextResult[None].fail("Stream type is required")
        if not self.search_filter:
            return FlextResult[None].fail("Search filter is required")
        if not self.tap_stream_id:
            return FlextResult[None].fail("Tap stream ID is required")
        if self.replication_method not in {"FULL_TABLE", "INCREMENTAL"}:
            return FlextResult[None].fail(
                "Replication method must be FULL_TABLE or INCREMENTAL",
            )
        return FlextResult[None].ok(None)

    id: FlextEntityId = Field(default_factory=lambda: FlextEntityId(str(uuid4())))
    connection_id: UUID
    stream_type: str
    search_filter: str
    attributes: list[str]
    tap_stream_id: str
    key_properties: list[str]
    replication_method: str
    replication_key: str | None = None
    stream_schema: dict[str, object]
    records_extracted: int = 0
    last_extraction: datetime | None = None

    def update_schema(self, schema: dict[str, object]) -> FlextResult[None]:
        """Update stream schema with validation."""
        if not isinstance(schema, dict):
            return FlextResult[None].fail("Schema must be a dictionary")
        self.stream_schema = schema
        return FlextResult[None].ok(None)

    def record_extraction(self, record_count: int) -> FlextResult[None]:
        """Record extraction statistics with validation."""
        if record_count < 0:
            return FlextResult[None].fail("Record count cannot be negative")
        self.records_extracted += record_count
        self.last_extraction = datetime.now(UTC)
        return FlextResult[None].ok(None)


class TapExecution(FlextEntity):
    """Tap execution entity using FlextEntity pattern."""

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate tap execution business rules."""
        if not self.command:
            return FlextResult[None].fail("Command is required")
        valid_statuses = {
            "created",
            "discovering",
            "extracting",
            "completed",
            "failed",
            "cancelled",
        }
        if self.tap_status not in valid_statuses:
            return FlextResult[None].fail(f"Invalid tap status: {self.tap_status}")
        if self.records_extracted < 0:
            return FlextResult[None].fail("Records extracted cannot be negative")
        if self.streams_processed < 0:
            return FlextResult[None].fail("Streams processed cannot be negative")
        return FlextResult[None].ok(None)

    id: FlextEntityId = Field(default_factory=lambda: FlextEntityId(str(uuid4())))
    connection_id: UUID
    command: str
    tap_status: str
    started_at: datetime | None = None
    completed_at: datetime | None = None
    duration_seconds: float | None = None
    config: dict[str, object]
    catalog: dict[str, object]
    state: dict[str, object]
    records_extracted: int = 0
    streams_processed: int = 0
    stdout: str | None = None
    stderr: str | None = None
    exit_code: int | None = None
    error_message: str | None = None

    @property
    def is_completed(self) -> bool:
        """Check if execution is completed."""
        return self.tap_status in {
            "completed",
            "failed",
            "cancelled",
        }

    @property
    def successful(self) -> bool:
        """Check if execution was successful."""
        return self.tap_status == "completed" and self.exit_code == 0

    def start_execution(self) -> FlextResult[None]:
        """Start tap execution with validation."""
        if self.tap_status != "created":
            return FlextResult[None].fail(
                f"Cannot start execution from status: {self.tap_status}",
            )
        self.tap_status = "discovering"
        self.started_at = datetime.now(UTC)
        return FlextResult[None].ok(None)

    def start_extraction(self) -> FlextResult[None]:
        """Start extraction phase with validation."""
        if self.tap_status != "discovering":
            return FlextResult[None].fail(
                f"Cannot start extraction from status: {self.tap_status}",
            )
        self.tap_status = "extracting"
        return FlextResult[None].ok(None)

    def complete_execution(
        self,
        exit_code: int,
        stdout: str | None = None,
        stderr: str | None = None,
    ) -> FlextResult[None]:
        """Complete tap execution with validation."""
        if self.tap_status not in {"discovering", "extracting"}:
            return FlextResult[None].fail(
                f"Cannot complete execution from status: {self.tap_status}",
            )

        self.tap_status = "completed" if exit_code == 0 else "failed"
        self.exit_code = exit_code
        self.completed_at = datetime.now(UTC)
        self.stdout = stdout
        self.stderr = stderr

        if self.started_at:
            duration = self.completed_at - self.started_at
            self.duration_seconds = duration.total_seconds()

        return FlextResult[None].ok(None)

    def cancel_execution(self) -> FlextResult[None]:
        """Cancel tap execution with validation."""
        if self.tap_status in {"completed", "failed", "cancelled"}:
            return FlextResult[None].fail(
                f"Cannot cancel execution with status: {self.tap_status}",
            )

        self.tap_status = "cancelled"
        self.completed_at = datetime.now(UTC)

        if self.started_at:
            duration = self.completed_at - self.started_at
            self.duration_seconds = duration.total_seconds()

        return FlextResult[None].ok(None)

    def update_metrics(
        self,
        records_extracted: int,
        streams_processed: int,
    ) -> FlextResult[None]:
        """Update execution metrics with validation."""
        if records_extracted < 0:
            return FlextResult[None].fail("Records extracted cannot be negative")
        if streams_processed < 0:
            return FlextResult[None].fail("Streams processed cannot be negative")

        self.records_extracted = records_extracted
        self.streams_processed = streams_processed
        return FlextResult[None].ok(None)


class LDAPRecord(FlextEntity):
    """LDAP record entity using FlextEntity pattern."""

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate LDAP record business rules."""
        if not self.dn:
            return FlextResult[None].fail("Distinguished Name (DN) is required")
        if not self.object_class:
            return FlextResult[None].fail("Object class is required")
        if not isinstance(self.attributes, dict):
            return FlextResult[None].fail("Attributes must be a dictionary")
        return FlextResult[None].ok(None)

    id: FlextEntityId = Field(default_factory=lambda: FlextEntityId(str(uuid4())))
    stream_id: UUID
    execution_id: UUID
    dn: str
    attributes: dict[str, object]
    object_class: list[str]
    extracted_at: datetime = Field(default_factory=datetime.now)
    singer_record: dict[str, object]

    @property
    def rdn(self) -> str:
        """Get relative distinguished name."""
        return self.dn.split(",")[0] if self.dn else ""

    def to_singer_record(self) -> FlextResult[dict[str, object]]:
        """Convert to Singer record format with validation."""
        validation_result = self.validate_business_rules()
        if not validation_result.success:
            return FlextResult[None].fail(f"Invalid LDAP record: {validation_result.error}")

        record = {
            "type": "RECORD",
            "record": {
                "dn": self.dn,
                "object_class": self.object_class,
                **self.attributes,
            },
            "time_extracted": self.extracted_at.isoformat(),
        }
        return FlextResult[None].ok(record)


# Domain Events using flext-core FlextModel pattern
class TapExecutionStartedEvent(FlextModel):
    """Event raised when tap execution starts."""

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate event data."""
        if not self.command:
            return FlextResult[None].fail("Command is required for execution started event")
        return FlextResult[None].ok(None)

    execution_id: UUID
    connection_id: UUID
    command: str


class TapExecutionCompletedEvent(FlextModel):
    """Event raised when tap execution completes."""

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate event data."""
        return FlextResult[None].ok(None)

    execution_id: UUID
    connection_id: UUID | None = None


class StreamDiscoveredEvent(FlextModel):
    """Event raised when stream is discovered."""

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate event data."""
        if not self.stream_name:
            return FlextResult[None].fail("Stream name is required")
        if not self.stream_type:
            return FlextResult[None].fail("Stream type is required")
        return FlextResult[None].ok(None)

    stream_id: UUID
    connection_id: UUID
    stream_name: str
    stream_type: str
    stream_schema: dict[str, object]


class RecordExtractedEvent(FlextModel):
    """Event raised when record is extracted."""

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate event data."""
        if not self.dn:
            return FlextResult[None].fail("DN is required for record extracted event")
        if self.attributes_count < 0:
            return FlextResult[None].fail("Attributes count cannot be negative")
        return FlextResult[None].ok(None)

    record_id: UUID
    stream_id: UUID
    execution_id: UUID
    dn: str
    attributes_count: int


class ConnectionTestedEvent(FlextModel):
    """Event raised when connection is tested."""

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate event data."""
        return FlextResult[None].ok(None)

    connection_id: UUID
    connection_name: str | None = None
