"""Domain models for tap-ldap using flext-core.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import Field

from flext_core import FlextModels, FlextResult, FlextTypes


class FlextTapLdapModels(FlextModels):
    """Comprehensive models for LDAP tap operations extending FlextModels.

    Provides standardized models for all LDAP tap domain entities including:
    - Singer stream metadata and configuration
    - LDAP connection and authentication management
    - LDIF file processing operations
    - Performance monitoring and metrics collection
    - LDAP schema and directory operations
    - All utility functions for data processing

    All nested classes inherit FlextModels validation and patterns.
    Consolidates ALL models from tap_models.py and other scattered classes.
    """

    # Legacy type aliases for backward compatibility
    LDAPRecord = dict["str", "object"]
    LDAPRecords = list[LDAPRecord]

    class UtilityFunctions:
        """Utility functions for model data processing."""

        @staticmethod
        def get_entry_value(
            entry: FlextTypes.Core.Dict | Any,
            key: str,
            default: object = None,
        ) -> object:
            """Get a value from either a dict or FlextLdapModels.Entry.

            Returns the attribute value by name from a plain dict or an attribute of
            a FlextLdapModels.Entry, falling back to default when not present.
            """
            if isinstance(entry, dict):
                return entry.get(key, default)
            # FlextLdapModels.Entry - use getattr or similar access pattern
            return getattr(entry, key, default)

        @staticmethod
        def safe_list_str(value: object) -> list[str]:
            """Safely convert value to list of strings."""
            if value is None:
                return []
            if isinstance(value, str):
                return [value]
            if isinstance(value, list):
                return [str(item) for item in value]
            return [str(value)]

        @staticmethod
        def safe_first_str(value: object) -> str:
            """Safely get first string value from potentially list value."""
            if value is None:
                return ""
            if isinstance(value, str):
                return value
            if isinstance(value, list) and value:
                return str(value[0])
            return str(value)

        @staticmethod
        def safe_list_value(value: object) -> list[object]:
            """Safely convert value to list."""
            if value is None:
                return []
            if isinstance(value, list):
                return value
            return [value]

        @staticmethod
        def safe_first_value(value: object) -> object | None:
            """Safely get first value from potentially list value."""
            if value is None:
                return None
            if isinstance(value, list):
                return value[0] if value else None
            return value

    class LdapAttribute(FlextModels.Value):
        """Represents an LDAP attribute with its values."""

        name: str = Field(..., description="Attribute name")
        values: FlextTypes.Core.StringList = Field(..., description="Attribute values")
        is_binary: bool = Field(
            default=False,
            description="Whether the attribute contains binary data",
        )

        def validate_domain_rules(self: object) -> FlextResult[None]:
            """Validate domain-specific rules for LDAP attributes."""
            # LDAP attributes can have any name and values
            return FlextResult[None].ok(None)

        def validate_business_rules(self: object) -> FlextResult[None]:
            """Validate business rules for LDAP attributes."""
            # Business validation for LDAP attributes
            return FlextResult[None].ok(None)

        @property
        def single_value(self: object) -> str | None:
            """Get first value if exists, None otherwise.

            Returns:
                First value from values list or None if empty.

            """
            return self.values[0] if self.values else None

        @property
        def is_multi_valued(self: object) -> bool:
            """Check if attribute has multiple values.

            Returns:
                True if attribute has more than one value.

            """
            return len(self.values) > 1

    class LdapConnectionConfig(FlextModels.BaseConfig):
        """LDAP connection configuration with comprehensive settings."""

        # LDAP Connection (required)
        host: str = Field(..., description="LDAP server hostname")
        port: int = Field(default=389, ge=1, le=65535, description="LDAP server port")
        bind_dn: str = Field(..., description="Bind DN for authentication")
        password: str = Field(..., description="Password for bind DN")
        base_dn: str = Field(..., description="Base DN for searches")

        # SSL/TLS Configuration
        use_ssl: bool = Field(default=False, description="Enable SSL connection")
        use_tls: bool = Field(default=False, description="Enable StartTLS")
        ca_cert_file: str | None = Field(
            default=None, description="CA certificate file path"
        )
        cert_file: str | None = Field(
            default=None, description="Client certificate file"
        )
        key_file: str | None = Field(
            default=None, description="Client private key file"
        )

        # Performance Settings
        timeout: int = Field(
            default=30, ge=1, le=300, description="Connection timeout in seconds"
        )
        page_size: int = Field(
            default=1000, ge=1, le=10000, description="LDAP paging size"
        )
        connection_pool_size: int = Field(
            default=5, ge=1, le=20, description="Connection pool size"
        )

        # LDIF Processing
        enable_ldif_streams: bool = Field(
            default=False, description="Enable LDIF file processing"
        )
        ldif_files: list[str] = Field(
            default_factory=list, description="List of LDIF files to process"
        )
        ldif_directory: str | None = Field(
            default=None, description="Directory containing LDIF files"
        )
        ldif_ignore_errors: bool = Field(
            default=True, description="Continue processing on LDIF errors"
        )
        ldif_max_errors: int = Field(
            default=100, ge=0, le=10000, description="Maximum LDIF errors allowed"
        )

    class LdapStreamMetadata(FlextModels.Entity):
        """LDAP stream metadata with Singer protocol compliance."""

        # Singer stream configuration
        stream_name: str = Field(..., description="Singer stream name")
        ldap_filter: str = Field(..., description="LDAP search filter for this stream")
        base_dn: str | None = Field(
            default=None, description="Specific base DN for this stream"
        )
        attributes: list[str] = Field(
            default_factory=list, description="LDAP attributes to retrieve"
        )

        # Replication settings
        replication_method: str = Field(
            default="FULL_TABLE", description="Singer replication method"
        )
        replication_key: str | None = Field(
            default=None, description="Attribute for incremental replication"
        )

        # LDAP-specific settings
        search_scope: str = Field(default="SUBTREE", description="LDAP search scope")
        page_size: int = Field(default=1000, description="Results page size")
        follow_referrals: bool = Field(
            default=True, description="Follow LDAP referrals"
        )

    class LdapEntry(FlextModels.Entity):
        """Represents an LDAP directory entry with comprehensive attributes."""

        dn: str = Field(..., description="Distinguished Name")
        object_classes: FlextTypes.Core.StringList = Field(
            ...,
            description="Object classes",
        )

        def validate_business_rules(self: object) -> FlextResult[None]:
            """Validate business rules for LDAP entries."""
            if not self.dn:
                return FlextResult[None].fail("DN cannot be empty")
            # Additional LDAP entry validation can be added here
            return FlextResult[None].ok(None)

        attributes: FlextTypes.Core.Dict = Field(
            default_factory=dict,
            description="Entry attributes",
        )

        # Metadata
        extracted_at: str = Field(description="Extraction timestamp")
        source_server: str | None = Field(
            default=None, description="Source LDAP server"
        )
        entry_uuid: str | None = Field(
            default=None, description="LDAP entry UUID if available"
        )
        created_at: datetime | None = Field(None, description="Entry creation time")
        modified_at: datetime | None = Field(
            None, description="Entry modification time"
        )
        created_by: str | None = Field(None, description="Entry creator")
        modified_by: str | None = Field(None, description="Entry modifier")

        # Change tracking
        change_type: str | None = Field(
            None,
            description="LDIF change type (add, modify, delete)",
        )
        controls: FlextTypes.Core.StringList = Field(
            default_factory=list,
            description="LDAP controls",
        )

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

        def to_dict(self: object) -> FlextTypes.Core.Dict:
            """Convert entry to dictionary format.

            Returns:
                Dictionary representation of the LDAP entry.

            """
            result = {
                "dn": self.dn,
                "objectClass": self.object_classes,
            }

            # Add attributes
            for name, value in self.attributes.items():
                if isinstance(value, FlextTapLdapModels.LdapAttribute):
                    result[name] = value.values
                else:
                    result[name] = value

            return result

        @classmethod
        def from_dict(cls, data: FlextTypes.Core.Dict) -> FlextTapLdapModels.LdapEntry:
            """Create LdapEntry from dictionary.

            Args:
                data: Dictionary with entry data.

            Returns:
                LdapEntry instance.

            """
            return cls(
                dn=str(data.get("dn", "")),
                object_classes=FlextTapLdapModels.UtilityFunctions.safe_list_str(
                    data.get("objectClass", [])
                ),
                attributes=data.get("attributes", {}),
                extracted_at=data.get("extracted_at", datetime.now(UTC).isoformat()),
            )

    class LdapUser(FlextModels.BaseModel):
        """LDAP user entry with standard inetOrgPerson attributes."""

        # Core identification
        dn: str = Field(..., description="User Distinguished Name")
        uid: str | None = Field(default=None, description="User ID")
        cn: str | None = Field(default=None, description="Common Name")

        # Personal information
        given_name: str | None = Field(
            default=None, description="Given name (first name)"
        )
        sn: str | None = Field(default=None, description="Surname (last name)")
        display_name: str | None = Field(default=None, description="Display name")
        mail: str | None = Field(default=None, description="Email address")

        # Organizational information
        employee_number: str | None = Field(default=None, description="Employee number")
        department: str | None = Field(default=None, description="Department")
        title: str | None = Field(default=None, description="Job title")
        manager: str | None = Field(default=None, description="Manager DN")

        # Account information
        user_account_control: int | None = Field(
            default=None, description="Account control flags"
        )
        last_logon: str | None = Field(default=None, description="Last logon timestamp")
        password_last_set: str | None = Field(
            default=None, description="Password last set timestamp"
        )

        # Group memberships
        member_of: list[str] = Field(
            default_factory=list, description="Group memberships"
        )

    class LdapGroup(FlextModels.BaseModel):
        """LDAP group entry with membership management."""

        # Core identification
        dn: str = Field(..., description="Group Distinguished Name")
        cn: str | None = Field(default=None, description="Group common name")

        # Group information
        description: str | None = Field(default=None, description="Group description")
        group_type: str | None = Field(default=None, description="Group type")
        sam_account_name: str | None = Field(
            default=None, description="SAM account name"
        )

        # Membership
        members: list[str] = Field(default_factory=list, description="Group member DNs")
        member_of: list[str] = Field(
            default_factory=list, description="Parent group memberships"
        )

        # Metadata
        when_created: str | None = Field(
            default=None, description="Group creation timestamp"
        )
        when_changed: str | None = Field(
            default=None, description="Last modification timestamp"
        )

    class LdapSchema(FlextModels.BaseModel):
        """LDAP schema information with object classes and attributes."""

        object_classes: list[str] = Field(
            default_factory=list, description="Available object classes"
        )
        attributes: list[str] = Field(
            default_factory=list, description="Available attributes"
        )
        syntax_definitions: dict[str, str] = Field(
            default_factory=dict, description="Attribute syntax definitions"
        )

    class LdapConnection(FlextModels.Entity):
        """LDAP connection state and configuration."""

        host: str = Field(..., description="LDAP server host")
        port: int = Field(..., description="LDAP server port")
        bind_dn: str = Field(..., description="Bind DN")
        is_connected: bool = Field(default=False, description="Connection status")
        connection_time: float = Field(
            default=0.0, description="Connection establishment time"
        )
        last_operation: str | None = Field(
            default=None, description="Last LDAP operation"
        )

    class LdapStream(FlextModels.Entity):
        """Singer stream configuration for LDAP data."""

        name: str = Field(..., description="Stream name")
        tap_stream_id: str = Field(..., description="Singer tap stream ID")
        schema: dict[str, Any] = Field(default_factory=dict, description="JSON schema")
        metadata: list[dict[str, Any]] = Field(
            default_factory=list, description="Stream metadata"
        )
        replication_method: str = Field(
            default="FULL_TABLE", description="Replication method"
        )

    class TapExecution(FlextModels.Entity):
        """Tap execution tracking and state management."""

        execution_id: str = Field(..., description="Unique execution identifier")
        started_at: datetime = Field(
            default_factory=lambda: datetime.now(UTC),
            description="Execution start time",
        )
        completed_at: datetime | None = Field(
            default=None, description="Execution completion time"
        )
        status: str = Field(default="running", description="Execution status")
        streams_processed: int = Field(
            default=0, description="Number of streams processed"
        )
        records_extracted: int = Field(default=0, description="Total records extracted")

    class LdapRecord(FlextModels.BaseModel):
        """Individual LDAP record for Singer output."""

        stream: str = Field(..., description="Source stream name")
        record: dict[str, Any] = Field(..., description="Record data")
        time_extracted: datetime = Field(
            default_factory=lambda: datetime.now(UTC),
            description="Extraction timestamp",
        )

    class TapExecutionStartedEvent(FlextModels.DomainEvent):
        """Domain event for tap execution start."""

        execution_id: str = Field(..., description="Execution identifier")
        config: dict[str, Any] = Field(..., description="Tap configuration")

    class TapExecutionCompletedEvent(FlextModels.DomainEvent):
        """Domain event for tap execution completion."""

        execution_id: str = Field(..., description="Execution identifier")
        records_extracted: int = Field(..., description="Total records extracted")
        duration: float = Field(..., description="Execution duration in seconds")

    class StreamDiscoveredEvent(FlextModels.DomainEvent):
        """Domain event for stream discovery."""

        stream_name: str = Field(..., description="Discovered stream name")
        schema: dict[str, Any] = Field(..., description="Stream schema")

    class RecordExtractedEvent(FlextModels.DomainEvent):
        """Domain event for record extraction."""

        stream_name: str = Field(..., description="Source stream")
        record: dict[str, Any] = Field(..., description="Extracted record")

    class ConnectionTestedEvent(FlextModels.DomainEvent):
        """Domain event for connection testing."""

        host: str = Field(..., description="LDAP server host")
        success: bool = Field(..., description="Connection test result")
        error_message: str | None = Field(
            default=None, description="Error message if failed"
        )

    class LdifProcessingState(FlextModels.BaseModel):
        """LDIF file processing state and statistics."""

        # File information
        file_path: str = Field(..., description="LDIF file path")
        file_size: int = Field(default=0, description="File size in bytes")

        # Processing statistics
        entries_processed: int = Field(
            default=0, description="Number of entries processed"
        )
        entries_failed: int = Field(
            default=0, description="Number of entries that failed"
        )
        change_records: int = Field(
            default=0, description="Number of change records processed"
        )

        # Timing information
        start_time: str = Field(description="Processing start timestamp")
        end_time: str | None = Field(
            default=None, description="Processing end timestamp"
        )
        processing_duration: float = Field(
            default=0.0, description="Processing duration in seconds"
        )

        # Error tracking
        errors: list[str] = Field(default_factory=list, description="Processing errors")
        warnings: list[str] = Field(
            default_factory=list, description="Processing warnings"
        )

    class LdapTapPerformanceMetrics(FlextModels.BaseModel):
        """Performance metrics for LDAP tap operations."""

        # Connection metrics
        connection_time: float = Field(
            default=0.0, description="LDAP connection time in seconds"
        )
        search_time: float = Field(
            default=0.0, description="Total search time in seconds"
        )

        # Volume metrics
        total_entries: int = Field(default=0, description="Total entries extracted")
        total_bytes: int = Field(default=0, description="Total bytes processed")
        streams_processed: int = Field(
            default=0, description="Number of streams processed"
        )

        # Performance rates
        entries_per_second: float = Field(
            default=0.0, description="Entries processed per second"
        )
        bytes_per_second: float = Field(
            default=0.0, description="Bytes processed per second"
        )

        # LDAP-specific metrics
        ldap_operations: int = Field(
            default=0, description="Total LDAP operations performed"
        )
        paged_searches: int = Field(
            default=0, description="Number of paged searches executed"
        )
        referrals_followed: int = Field(
            default=0, description="Number of referrals followed"
        )

        # Error metrics
        connection_errors: int = Field(default=0, description="LDAP connection errors")
        search_errors: int = Field(default=0, description="LDAP search errors")
        timeout_errors: int = Field(default=0, description="Operation timeout errors")

    # Legacy type aliases maintained for backward compatibility
    TapConfiguration = dict[str, object]
    StreamConfiguration = dict[str, object]

    # Convenience accessors for backward compatibility
    @classmethod
    def get_entry_value(cls, entry: Any, key: str, default: object = None) -> object:
        """Convenience method for getting entry values."""
        return cls.UtilityFunctions.get_entry_value(entry, key, default)

    @classmethod
    def safe_list_str(cls, value: object) -> list[str]:
        """Convenience method for safe list conversion."""
        return cls.UtilityFunctions.safe_list_str(value)

    @classmethod
    def safe_first_str(cls, value: object) -> str:
        """Convenience method for safe first string extraction."""
        return cls.UtilityFunctions.safe_first_str(value)


# Legacy aliases for backward compatibility
LDAPAttribute = FlextTapLdapModels.LdapAttribute
LDAPEntry = FlextTapLdapModels.LdapEntry
LDAPUser = FlextTapLdapModels.LdapUser
LDAPGroup = FlextTapLdapModels.LdapGroup
LDAPSchema = FlextTapLdapModels.LdapSchema
LDAPConnection = FlextTapLdapModels.LdapConnection
LDAPStream = FlextTapLdapModels.LdapStream
LDAPRecord = FlextTapLdapModels.LdapRecord
TapExecution = FlextTapLdapModels.TapExecution
TapExecutionStartedEvent = FlextTapLdapModels.TapExecutionStartedEvent
TapExecutionCompletedEvent = FlextTapLdapModels.TapExecutionCompletedEvent
StreamDiscoveredEvent = FlextTapLdapModels.StreamDiscoveredEvent
RecordExtractedEvent = FlextTapLdapModels.RecordExtractedEvent
ConnectionTestedEvent = FlextTapLdapModels.ConnectionTestedEvent


# Public API: expose unified models class and backward compatibility aliases
__all__ = [
    "ConnectionTestedEvent",
    "FlextTapLdapModels",
    # Legacy aliases for backward compatibility
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
]
