"""Domain Models for FLEXT Tap LDAP with flext-core integration.

Consolidates all data models for LDAP tap operations including entries,
streams, connections, and execution tracking.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from flext_core import FlextLogger, FlextModels, FlextResult, FlextTypes
from flext_core.typings import FlextTypes
from flext_ldap import FlextLDAPEntities
from pydantic import Field

logger = FlextLogger(__name__)


def _get_entry_value(
    entry: FlextTypes.Core.Dict | FlextLDAPEntities.Entry,
    key: str,
    default: object = None,
) -> object:
    """Get a value from either a dict or `FlextLDAPEntities.Entry`."""
    if isinstance(entry, dict):
        return entry.get(key, default)
    # FlextLDAPEntities.Entry - use getattr or similar access pattern
    return getattr(entry, key, default)


def _safe_list_value(
    value: object, default: FlextTypes.Core.StringList | None = None
) -> FlextTypes.Core.StringList:
    """Safely convert value to FlextTypes.Core.StringList."""
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, str):
        return [value]
    return default or []


def _safe_first_value(value: object) -> str | None:
    """Safely get first value from list or return string."""
    if isinstance(value, list) and len(value) > 0:
        return str(value[0])
    if isinstance(value, str):
        return value
    return None


class LDAPAttribute(FlextModels):
    """Represents an LDAP attribute with its values."""

    name: str = Field(..., description="Attribute name")
    values: FlextTypes.Core.StringList = Field(..., description="Attribute values")
    is_binary: bool = Field(
        default=False,
        description="Whether the attribute contains binary data",
    )

    def validate_domain_rules(self) -> FlextResult[None]:
        """Validate domain-specific rules for LDAP attributes."""
        # LDAP attributes can have any name and values
        return FlextResult[None].ok(None)

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate business rules for LDAP attributes."""
        # Business validation for LDAP attributes
        return FlextResult[None].ok(None)

    @property
    def single_value(self) -> str | None:
        """Get first value if exists, None otherwise.

        Returns:
            First value from values list or None if empty.

        """
        return self.values[0] if self.values else None

    @property
    def is_multi_valued(self) -> bool:
        """Check if attribute has multiple values.

        Returns:
            True if attribute has more than one value.

        """
        return len(self.values) > 1


class LDAPEntry(FlextModels):
    """Represents an LDAP entry with comprehensive metadata."""

    dn: str = Field(..., description="Distinguished Name")
    object_classes: FlextTypes.Core.StringList = Field(
        ..., description="Object classes"
    )
    attributes: FlextTypes.Core.Dict = Field(
        default_factory=dict,
        description="Entry attributes",
    )

    # Metadata
    created_at: datetime | None = Field(None, description="Entry creation time")
    modified_at: datetime | None = Field(None, description="Entry modification time")
    created_by: str | None = Field(None, description="Entry creator")
    modified_by: str | None = Field(None, description="Entry modifier")

    # Change tracking
    change_type: str | None = Field(
        None,
        description="LDIF change type (add, modify, delete)",
    )
    controls: FlextTypes.Core.StringList = Field(
        default_factory=list, description="LDAP controls"
    )

    def validate_domain_rules(self) -> FlextResult[None]:
        """Validate domain-specific rules for LDAP entries."""
        if not self.dn:
            return FlextResult[None].fail("DN cannot be empty")
        # Additional LDAP entry validation can be added here
        return FlextResult[None].ok(None)

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate business rules for LDAP entries."""
        return FlextResult[None].ok(None)

    @property
    def rdn(self) -> str:
        """Get relative distinguished name."""
        return self.dn.split(",")[0] if self.dn else ""

    def get_attribute(self, name: str) -> object | None:
        """Get attribute value by name (case-insensitive).

        Args:
            name: Attribute name to retrieve.

        Returns:
            Attribute value if found, None otherwise.

        """
        # LDAP attributes are case-insensitive
        for key, value in self.attributes.items():
            if key.lower() == name.lower():
                return value
        return None

    def has_object_class(self, object_class: str) -> bool:
        """Check if entry has specific object class.

        Args:
            object_class: Object class name to check.

        Returns:
            True if entry has the specified object class (case-insensitive).

        """
        return any(oc.lower() == object_class.lower() for oc in self.object_classes)


class LDAPUser(LDAPEntry):
    """Represents an LDAP user entry with user-specific attributes."""

    uid: str | None = Field(None, description="User ID")
    cn: str | None = Field(None, description="Common name")
    sn: str | None = Field(None, description="Surname")
    given_name: str | None = Field(None, description="Given name")
    display_name: str | None = Field(None, description="Display name")
    mail: str | None = Field(None, description="Email address")
    telephone_number: str | None = Field(None, description="Telephone number")
    mobile: str | None = Field(None, description="Mobile number")
    employee_number: str | None = Field(None, description="Employee number")
    employee_type: str | None = Field(None, description="Employee type")
    department: str | None = Field(None, description="Department")
    title: str | None = Field(None, description="Job title")
    manager: str | None = Field(None, description="Manager DN")
    home_directory: str | None = Field(None, description="Home directory")
    login_shell: str | None = Field(None, description="Login shell")

    @classmethod
    def from_entry(
        cls, entry: FlextTypes.Core.Dict | FlextLDAPEntities.Entry
    ) -> LDAPUser:
        """Create LDAPUser from LDAP entry."""
        return cls(
            # Required fields from LDAPEntry
            dn=str(_get_entry_value(entry, "dn", "")),
            object_classes=_safe_list_value(_get_entry_value(entry, "objectClass", [])),
            # Optional metadata fields from LDAPEntry with defaults
            created_at=None,
            modified_at=None,
            created_by=None,
            modified_by=None,
            change_type=None,
            # LDAPUser specific fields with defaults
            uid=_safe_first_value(_get_entry_value(entry, "uid", [])),
            cn=_safe_first_value(_get_entry_value(entry, "cn", [])),
            sn=_safe_first_value(_get_entry_value(entry, "sn", [])),
            given_name=_safe_first_value(_get_entry_value(entry, "givenName", [])),
            display_name=_safe_first_value(_get_entry_value(entry, "displayName", [])),
            mail=_safe_first_value(_get_entry_value(entry, "mail", [])),
            telephone_number=_safe_first_value(
                _get_entry_value(entry, "telephoneNumber", []),
            ),
            mobile=_safe_first_value(_get_entry_value(entry, "mobile", [])),
            employee_number=_safe_first_value(
                _get_entry_value(entry, "employeeNumber", []),
            ),
            employee_type=_safe_first_value(
                _get_entry_value(entry, "employeeType", []),
            ),
            department=_safe_first_value(_get_entry_value(entry, "department", [])),
            title=_safe_first_value(_get_entry_value(entry, "title", [])),
            manager=_safe_first_value(_get_entry_value(entry, "manager", [])),
            home_directory=_safe_first_value(
                _get_entry_value(entry, "homeDirectory", []),
            ),
            login_shell=_safe_first_value(_get_entry_value(entry, "loginShell", [])),
        )


class LDAPGroup(LDAPEntry):
    """Represents an LDAP group entry with group-specific attributes."""

    cn: str | None = Field(None, description="Group name")
    description: str | None = Field(None, description="Group description")
    members: FlextTypes.Core.StringList = Field(
        default_factory=list, description="Member DNs"
    )
    unique_members: FlextTypes.Core.StringList = Field(
        default_factory=list,
        description="Unique member DNs",
    )
    gid_number: str | None = Field(None, description="Group ID number")
    owner: str | None = Field(None, description="Group owner DN")
    create_timestamp: str | None = Field(None, description="Creation timestamp")
    modify_timestamp: str | None = Field(None, description="Modification timestamp")

    @classmethod
    def from_entry(
        cls, entry: FlextTypes.Core.Dict | FlextLDAPEntities.Entry
    ) -> LDAPGroup:
        """Create LDAPGroup from LDAP entry."""
        return cls(
            # Required fields from LDAPEntry
            dn=str(_get_entry_value(entry, "dn", "")),
            object_classes=_safe_list_value(_get_entry_value(entry, "objectClass", [])),
            # Optional metadata fields from LDAPEntry with defaults
            created_at=None,
            modified_at=None,
            created_by=None,
            modified_by=None,
            change_type=None,
            # LDAPGroup specific fields with defaults
            cn=_safe_first_value(_get_entry_value(entry, "cn", [])),
            description=_safe_first_value(_get_entry_value(entry, "description", [])),
            members=_safe_list_value(_get_entry_value(entry, "member", [])),
            unique_members=_safe_list_value(
                _get_entry_value(entry, "uniqueMember", []),
            ),
            gid_number=_safe_first_value(_get_entry_value(entry, "gidNumber", [])),
            owner=None,
            create_timestamp=_safe_first_value(
                _get_entry_value(entry, "createTimestamp", []),
            ),
            modify_timestamp=_safe_first_value(
                _get_entry_value(entry, "modifyTimestamp", []),
            ),
        )


class LDAPSchema(FlextModels):
    """Represents LDAP schema information."""

    object_classes: FlextTypes.Core.StringList = Field(
        default_factory=list,
        description="Available object classes",
    )
    attribute_types: FlextTypes.Core.StringList = Field(
        default_factory=list,
        description="Available attribute types",
    )
    ldap_syntaxes: FlextTypes.Core.StringList = Field(
        default_factory=list, description="LDAP syntaxes"
    )
    naming_contexts: FlextTypes.Core.StringList = Field(
        default_factory=list,
        description="Naming contexts",
    )

    def validate_domain_rules(self) -> FlextResult[None]:
        """Validate domain-specific rules for LDAP schema."""
        # Schema validation rules can be added here
        return FlextResult[None].ok(None)

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate business rules for LDAP schema."""
        return FlextResult[None].ok(None)

    @property
    def has_oracle_extensions(self) -> bool:
        """Check if schema contains Oracle-specific extensions.

        Returns:
            True if schema contains Oracle LDAP extensions.

        """
        oracle_prefixes = ["orcl", "oracl", "oid"]
        return any(
            any(oc.lower().startswith(prefix) for prefix in oracle_prefixes)
            for oc in self.object_classes
        )


# CONNECTION AND EXECUTION MODELS


class LDAPConnection(FlextModels):
    """LDAP connection entity with comprehensive tracking."""

    id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Connection unique identifier",
    )
    host: str = Field(..., description="LDAP server host")
    port: int = Field(389, description="LDAP server port")
    bind_dn: str | None = Field(None, description="Bind DN for authentication")
    password: str | None = Field(None, description="Bind password", repr=False)
    use_ssl: bool = Field(default=False, description="Use SSL/TLS connection")
    timeout: int = Field(default=30, description="Connection timeout in seconds")
    pool_size: int = Field(default=5, description="Connection pool size")
    is_active: bool = Field(default=True, description="Connection is active")
    last_tested: datetime | None = Field(None, description="Last connection test time")
    last_error: str | None = Field(None, description="Last connection error")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    def validate_domain_rules(self) -> FlextResult[None]:
        """Validate domain-specific rules for LDAP connections."""
        if not self.host:
            return FlextResult[None].fail("Host is required")
        max_port_number = 65535
        if self.port < 1 or self.port > max_port_number:
            return FlextResult[None].fail(
                f"Port must be between 1 and {max_port_number}"
            )
        return FlextResult[None].ok(None)

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate business rules for LDAP connections."""
        return FlextResult[None].ok(None)

    @property
    def connection_string(self) -> str:
        """Get connection string for display purposes."""
        protocol = "ldaps" if self.use_ssl else "ldap"
        return f"{protocol}://{self.host}:{self.port}"

    def test_connection_success(self) -> LDAPConnection:
        """Mark connection test as successful."""
        return self.model_copy(
            update={
                "last_tested": datetime.now(UTC),
                "last_error": None,
                "is_active": True,
            },
        )

    def test_connection_failure(self, error: str) -> LDAPConnection:
        """Mark connection test as failed."""
        return self.model_copy(
            update={
                "last_tested": datetime.now(UTC),
                "last_error": error,
                "is_active": False,
            },
        )


class LDAPStream(FlextModels):
    """LDAP stream entity with comprehensive metadata."""

    id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Stream unique identifier",
    )
    connection_id: str = Field(..., description="Associated connection ID")
    stream_type: str = Field(..., description="Type of LDAP stream")
    search_filter: str = Field(..., description="LDAP search filter")
    attributes: FlextTypes.Core.StringList = Field(
        default_factory=list,
        description="Attributes to extract",
    )
    tap_stream_id: str = Field(..., description="Singer tap stream ID")
    key_properties: FlextTypes.Core.StringList = Field(
        default_factory=list,
        description="Primary key properties",
    )
    replication_method: str = Field("FULL_TABLE", description="Replication method")
    replication_key: str | None = Field(None, description="Replication key field")
    stream_schema: FlextTypes.Core.Dict = Field(
        default_factory=dict,
        description="Stream JSON schema",
    )
    records_extracted: int = Field(0, description="Total records extracted")
    last_extraction: datetime | None = Field(None, description="Last extraction time")
    is_selected: bool = Field(
        default=True,
        description="Stream is selected for extraction",
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    def validate_domain_rules(self) -> FlextResult[None]:
        """Validate domain-specific rules for LDAP streams."""
        if not self.tap_stream_id:
            return FlextResult[None].fail("Tap stream ID is required")
        if not self.search_filter:
            return FlextResult[None].fail("Search filter is required")
        return FlextResult[None].ok(None)

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate business rules for LDAP streams."""
        return FlextResult[None].ok(None)

    def update_schema(self, schema: FlextTypes.Core.Dict) -> LDAPStream:
        """Update stream schema."""
        return self.model_copy(
            update={
                "stream_schema": schema,
                "updated_at": datetime.now(UTC),
            },
        )

    def record_extraction(self, record_count: int) -> LDAPStream:
        """Record extraction statistics."""
        return self.model_copy(
            update={
                "records_extracted": self.records_extracted + record_count,
                "last_extraction": datetime.now(UTC),
                "updated_at": datetime.now(UTC),
            },
        )


class TapExecution(FlextModels):
    """Tap execution entity with comprehensive tracking."""

    id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Execution unique identifier",
    )
    connection_id: str = Field(..., description="Associated connection ID")
    command: str = Field(..., description="Executed command")
    tap_status: str = Field("pending", description="Execution status")
    started_at: datetime | None = Field(None, description="Execution start time")
    completed_at: datetime | None = Field(None, description="Execution completion time")
    duration_seconds: float | None = Field(None, description="Execution duration")
    config: FlextTypes.Core.Dict = Field(
        default_factory=dict,
        description="Tap configuration",
    )
    catalog: FlextTypes.Core.Dict = Field(
        default_factory=dict,
        description="Stream catalog",
    )
    state: FlextTypes.Core.Dict = Field(default_factory=dict, description="Tap state")
    records_extracted: int = Field(0, description="Total records extracted")
    streams_processed: int = Field(0, description="Total streams processed")
    stdout: str | None = Field(None, description="Standard output")
    stderr: str | None = Field(None, description="Standard error")
    exit_code: int | None = Field(None, description="Exit code")
    error_message: str | None = Field(None, description="Error message")

    def validate_domain_rules(self) -> FlextResult[None]:
        """Validate domain-specific rules for tap executions."""
        if not self.command:
            return FlextResult[None].fail("Command is required")
        return FlextResult[None].ok(None)

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate business rules for tap executions."""
        return FlextResult[None].ok(None)

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

    def start_execution(self) -> TapExecution:
        """Start tap execution."""
        return self.model_copy(
            update={
                "tap_status": "discovering",
                "started_at": datetime.now(UTC),
            },
        )

    def start_extraction(self) -> TapExecution:
        """Start extraction phase."""
        return self.model_copy(update={"tap_status": "extracting"})

    def complete_execution(
        self,
        exit_code: int,
        stdout: str | None = None,
        stderr: str | None = None,
    ) -> TapExecution:
        """Complete tap execution."""
        completed_at = datetime.now(UTC)
        duration_seconds = None

        if self.started_at:
            duration = completed_at - self.started_at
            duration_seconds = duration.total_seconds()

        return self.model_copy(
            update={
                "tap_status": "completed" if exit_code == 0 else "failed",
                "exit_code": exit_code,
                "completed_at": completed_at,
                "duration_seconds": duration_seconds,
                "stdout": stdout,
                "stderr": stderr,
            },
        )

    def cancel_execution(self) -> TapExecution:
        """Cancel tap execution."""
        completed_at = datetime.now(UTC)
        duration_seconds = None

        if self.started_at:
            duration = completed_at - self.started_at
            duration_seconds = duration.total_seconds()

        return self.model_copy(
            update={
                "tap_status": "cancelled",
                "completed_at": completed_at,
                "duration_seconds": duration_seconds,
            },
        )

    def update_metrics(
        self,
        records_extracted: int,
        streams_processed: int,
    ) -> TapExecution:
        """Update execution metrics."""
        return self.model_copy(
            update={
                "records_extracted": records_extracted,
                "streams_processed": streams_processed,
            },
        )


class LDAPRecord(FlextModels):
    """LDAP record entity with Singer protocol support."""

    id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Record unique identifier",
    )
    stream_id: str = Field(..., description="Associated stream ID")
    execution_id: str = Field(..., description="Associated execution ID")
    dn: str = Field(..., description="Distinguished Name")
    attributes: FlextTypes.Core.Dict = Field(
        default_factory=dict,
        description="LDAP attributes",
    )
    object_class: FlextTypes.Core.StringList = Field(
        default_factory=list, description="Object classes"
    )
    extracted_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    singer_record: FlextTypes.Core.Dict = Field(
        default_factory=dict,
        description="Singer record data",
    )

    def validate_domain_rules(self) -> FlextResult[None]:
        """Validate domain-specific rules for LDAP records."""
        if not self.dn:
            return FlextResult[None].fail("DN is required")
        return FlextResult[None].ok(None)

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate business rules for LDAP records."""
        return FlextResult[None].ok(None)

    @property
    def rdn(self) -> str:
        """Get relative distinguished name."""
        return self.dn.split(",")[0] if self.dn else ""

    def to_singer_record(self) -> FlextTypes.Core.Dict:
        """Convert to Singer record format."""
        return {
            "type": "RECORD",
            "record": {
                "dn": self.dn,
                "objectClass": self.object_class,
                **self.attributes,
            },
            "time_extracted": self.extracted_at.isoformat(),
        }


# DOMAIN EVENTS


class TapExecutionStartedEvent(FlextModels):
    """Event raised when tap execution starts."""

    execution_id: UUID
    connection_id: UUID
    command: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class TapExecutionCompletedEvent(FlextModels):
    """Event raised when tap execution completes."""

    execution_id: UUID
    connection_id: UUID
    success: bool
    records_extracted: int
    streams_processed: int
    duration_seconds: float | None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class StreamDiscoveredEvent(FlextModels):
    """Event raised when stream is discovered."""

    stream_id: UUID
    connection_id: UUID
    stream_name: str
    stream_type: str
    stream_schema: FlextTypes.Core.Dict
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class RecordExtractedEvent(FlextModels):
    """Event raised when record is extracted."""

    record_id: UUID
    stream_id: UUID
    execution_id: UUID
    dn: str
    attributes_count: int
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ConnectionTestedEvent(FlextModels):
    """Event raised when connection is tested."""

    connection_id: UUID
    connection_host: str
    success: bool
    error_message: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


__all__ = [
    "ConnectionTestedEvent",
    "LDAPAttribute",
    "LDAPConnection",
    "LDAPEntry",
    "LDAPGroup",
    "LDAPRecord",
    "LDAPSchema",
    "LDAPStream",
    "LDAPUser",
    "RecordExtractedEvent",
    "StreamDiscoveredEvent",
    "TapExecution",
    "TapExecutionCompletedEvent",
    "TapExecutionStartedEvent",
    "_get_entry_value",
]
