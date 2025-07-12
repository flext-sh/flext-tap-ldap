from typing import Any

"""Domain entities for FLEXT-TAP-LDAP v0.7.0.

REFACTORED:
            Using flext-core mixins and types - NO duplication.  Clean architecture with domain entities using enhanced mixins for code reduction.  """

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import Field

from flext_core.domain.mixins import EntityMixin
from flext_core.domain.mixins import MetadataMixin
from flext_core.domain.mixins import StatusMixin
from flext_core.domain.pydantic_base import DomainEntity
from flext_core.domain.pydantic_base import DomainEvent
from flext_core.domain.pydantic_base import Field
from flext_core.domain.types import StrEnum

if TYPE_CHECKING:
            from uuid import UUID


class TapStatus(StrEnum):
    """Tap execution status using flext-core StrEnum."""

    IDLE = "idle"
    DISCOVERING = "discovering"
    EXTRACTING = "extracting"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StreamType(StrEnum):
    """LDAP stream types using flext-core StrEnum."""

    USERS = "users"
    GROUPS = "groups"
    ORGANIZATIONAL_UNITS = "organizational_units"
    CUSTOM = "custom"


class LDAPConnection(DomainEntity, EntityMixin):
    """LDAP connection domain entity using enhanced mixins for code reduction."""

    host: str = Field(..., min_length=1, max_length=255, description="LDAP server host")
    port: int = Field(default=389, ge=1, le=65535, description="LDAP server port")

    # Authentication
    bind_dn: str | None = Field(None, description="Distinguished name for binding")
    bind_password: str | None = Field(None, description="Password for LDAP authentication")
    use_ssl: bool = Field(default=False, description="Use SSL/LDAPS")
    use_tls: bool = Field(default=False, description="Use STARTTLS")

    # Search configuration
    base_dn: str = Field(..., min_length=1, description="Base DN for searches")
    search_scope: str = Field(
        default="subtree",
        description="Search scope: base, onelevel, subtree",
    )

    # Connection settings
    timeout: int = Field(
        default=30,
        ge=1,
        le=300,
        description="Connection timeout in seconds",
    )
    page_size: int = Field(
        default=1000,
        ge=1,
        le=10000,
        description="Page size for results",
    )
    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum retry attempts",
    )

    # Connection state
    last_tested: datetime | None = Field(None,
        description="Last connection test timestamp",
    )
    last_error: str | None = Field(None, description="Last error message")

    @property
    def connection_string(self) -> str:
        protocol = "ldaps" if self.use_ssl else "ldap"
        return f"{protocol}://{self.host}:{self.port}"

    def test_connection(self) -> None:
        self.last_tested = datetime.now()


class LDAPStream(DomainEntity, EntityMixin, MetadataMixin):
    """LDAP stream domain entity using enhanced mixins for code reduction."""

    connection_id: UUID = Field(..., description="Associated connection ID")
    stream_type: StreamType = Field(
        default=StreamType.CUSTOM,
        description="Type of LDAP stream",
    )

    # LDAP query
    search_filter: str = Field(..., min_length=1, description="LDAP search filter")
    attributes: list[str] = Field(
        default_factory=list,
        description="Attributes to retrieve",
    )

    # Stream configuration
    tap_stream_id: str = Field(..., min_length=1, description="Singer tap stream ID")
    key_properties: list[str] = Field(
        default_factory=list,
        description="Primary key properties",
    )
    replication_method: str = Field(
        default="FULL_TABLE",
        description="Replication method",
    )
    replication_key: str | None = Field(None, description="Replication key field")

    # Schema
    schema: dict[str, Any] = Field(
        default_factory=dict,
        description="JSON schema for stream",
    )

    # Metrics
    records_extracted: int = Field(
        default=0,
        ge=0,
        description="Total records extracted",
    )
    last_extraction: datetime | None = Field(None,
        description="Last extraction timestamp",
    )

    def update_schema(self, schema: dict[str, Any]) -> None:
        self.schema = schema

    def record_extraction(self, record_count: int) -> None:
        self.records_extracted += record_count
        self.last_extraction = datetime.now()


class TapExecution(DomainEntity, EntityMixin, StatusMixin):
    """Tap execution domain entity using enhanced mixins for code reduction."""

    connection_id: UUID = Field(..., description="Associated connection ID")

    # Execution details
    command: str = Field(..., min_length=1, description="Command executed")
    tap_status: TapStatus = Field(
        default=TapStatus.IDLE,
        description="Execution status",
    )

    # Timing
    started_at: datetime | None = Field(None, description="Execution start time")
    completed_at: datetime | None = Field(None, description="Execution completion time")
    duration_seconds: float | None = Field(None,
        ge=0,
        description="Duration in seconds",
    )

    # Configuration
    config: dict[str, Any] = Field(
        default_factory=dict,
        description="Tap configuration",
    )
    catalog: dict[str, Any] = Field(default_factory=dict, description="Singer catalog")
    state: dict[str, Any] = Field(default_factory=dict, description="Singer state")

    # Results
    records_extracted: int = Field(
        default=0,
        ge=0,
        description="Total records extracted",
    )
    streams_processed: int = Field(
        default=0,
        ge=0,
        description="Number of streams processed",
    )

    # Output
    stdout: str | None = Field(None, description="Standard output")
    stderr: str | None = Field(None, description="Standard error")
    exit_code: int | None = Field(None, description="Process exit code")

    # Error handling
    error_message: str | None = Field(None, description="Error message if failed")

    @property
    def is_completed(self) -> bool:
        return self.tap_status in {
            TapStatus.COMPLETED,
            TapStatus.FAILED,
            TapStatus.CANCELLED,
        }

    @property
    def is_successful(self) -> bool:
        return self.tap_status == TapStatus.COMPLETED and self.exit_code == 0

    def start_execution(self) -> None:
        self.tap_status = TapStatus.DISCOVERING
        self.started_at = datetime.now()

    def start_extraction(self) -> None:
        self.tap_status = TapStatus.EXTRACTING

    def complete_execution(self, exit_code: int, stdout: str | None = None, stderr: str | None = None) -> None:
        self.tap_status = TapStatus.COMPLETED if exit_code == 0 else TapStatus.FAILED
        self.exit_code = exit_code
        self.completed_at = datetime.now()
        self.stdout = stdout
        self.stderr = stderr

        if self.started_at:
            duration = self.completed_at - self.started_at
            self.duration_seconds = duration.total_seconds()

    def cancel_execution(self) -> None:
        self.tap_status = TapStatus.CANCELLED
        self.completed_at = datetime.now()

        if self.started_at:
            duration = self.completed_at - self.started_at
            self.duration_seconds = duration.total_seconds()

    def update_metrics(self, records_extracted: int, streams_processed: int) -> None:
        self.records_extracted = records_extracted
        self.streams_processed = streams_processed


class LDAPRecord(DomainEntity, EntityMixin):
    """LDAP record domain entity using enhanced mixins for code reduction."""

    stream_id: UUID = Field(..., description="Associated stream ID")
    execution_id: UUID = Field(..., description="Associated execution ID")

    # LDAP attributes
    dn: str = Field(..., min_length=1, description="Distinguished Name")
    attributes: dict[str, Any] = Field(
        default_factory=dict,
        description="LDAP attributes",
    )

    # Record metadata
    object_class: list[str] = Field(
        default_factory=list,
        description="LDAP object classes",
    )

    # Extraction metadata
    extracted_at: datetime = Field(
        default_factory=datetime.now,
        description="Extraction timestamp",
    )

    # Singer protocol
    singer_record: dict[str, Any] = Field(
        default_factory=dict,
        description="Singer format record",
    )

    @property
    def rdn(self) -> str:
        return self.dn.split(",")[0] if self.dn else ""

    def to_singer_record(self) -> dict[str, Any]:
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
class TapExecutionStartedEvent(DomainEvent):
    """Event raised when tap execution starts."""

    execution_id: UUID
    connection_id: UUID
    command: str


class TapExecutionCompletedEvent(DomainEvent):
    """Event raised when tap execution completes."""

    execution_id: UUID
    connection_id: UUID | None = None


class StreamDiscoveredEvent(DomainEvent):
    """Event raised when stream is discovered."""

    stream_id: UUID
    connection_id: UUID
    stream_name: str
    stream_type: StreamType
    schema: dict[str, Any]


class RecordExtractedEvent(DomainEvent):
    """Event raised when record is extracted."""

    record_id: UUID
    stream_id: UUID
    execution_id: UUID
    dn: str
    attributes_count: int


class ConnectionTestedEvent(DomainEvent):
    """Event raised when connection is tested."""

    connection_id: UUID
    connection_name: str | None = None
