"""Domain entities for tap-ldap using flext-core patterns."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from flext_core import get_logger
from pydantic import BaseModel, Field

logger = get_logger(__name__)


class LDAPConnection(BaseModel):
    """LDAP connection entity."""

    id: UUID = Field(default_factory=uuid4)
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
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class LDAPStream(BaseModel):
    """LDAP stream entity."""

    id: UUID = Field(default_factory=uuid4)
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

    def update_schema(self, schema: dict[str, object]) -> None:
        """Update stream schema."""
        self.stream_schema = schema

    def record_extraction(self, record_count: int) -> None:
        """Record extraction statistics."""
        self.records_extracted += record_count
        self.last_extraction = datetime.now(UTC)


class TapExecution(BaseModel):
    """Tap execution entity."""

    id: UUID = Field(default_factory=uuid4)
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

    def start_execution(self) -> None:
        """Start tap execution."""
        self.tap_status = "discovering"
        self.started_at = datetime.now(UTC)

    def start_extraction(self) -> None:
        """Start extraction phase."""
        self.tap_status = "extracting"

    def complete_execution(
        self,
        exit_code: int,
        stdout: str | None = None,
        stderr: str | None = None,
    ) -> None:
        """Complete tap execution."""
        self.tap_status = "completed" if exit_code == 0 else "failed"
        self.exit_code = exit_code
        self.completed_at = datetime.now(UTC)
        self.stdout = stdout
        self.stderr = stderr

        if self.started_at:
            duration = self.completed_at - self.started_at
            self.duration_seconds = duration.total_seconds()

    def cancel_execution(self) -> None:
        """Cancel tap execution."""
        self.tap_status = "cancelled"
        self.completed_at = datetime.now(UTC)

        if self.started_at:
            duration = self.completed_at - self.started_at
            self.duration_seconds = duration.total_seconds()

    def update_metrics(self, records_extracted: int, streams_processed: int) -> None:
        """Update execution metrics."""
        self.records_extracted = records_extracted
        self.streams_processed = streams_processed


class LDAPRecord(BaseModel):
    """LDAP record entity."""

    id: UUID = Field(default_factory=uuid4)
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

    def to_singer_record(self) -> dict[str, object]:
        """Convert to Singer record format."""
        return {
            "type": "RECORD",
            "record": {
                "dn": self.dn,
                "object_class": self.object_class,
                **self.attributes,
            },
            "time_extracted": self.extracted_at.isoformat(),
        }


# Domain Events using flext-core DomainEvent
class TapExecutionStartedEvent(BaseModel):
    """Event raised when tap execution starts."""

    execution_id: UUID
    connection_id: UUID
    command: str


class TapExecutionCompletedEvent(BaseModel):
    """Event raised when tap execution completes."""

    execution_id: UUID
    connection_id: UUID | None = None


class StreamDiscoveredEvent(BaseModel):
    """Event raised when stream is discovered."""

    stream_id: UUID
    connection_id: UUID
    stream_name: str
    stream_type: str
    stream_schema: dict[str, object]


class RecordExtractedEvent(BaseModel):
    """Event raised when record is extracted."""

    record_id: UUID
    stream_id: UUID
    execution_id: UUID
    dn: str
    attributes_count: int


class ConnectionTestedEvent(BaseModel):
    """Event raised when connection is tested."""

    connection_id: UUID
    connection_name: str | None = None
