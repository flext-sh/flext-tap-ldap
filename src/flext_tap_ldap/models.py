"""Domain models for tap-ldap using flext-core.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from flext_core import FlextModels, FlextResult, FlextTypes, FlextUtilities
from flext_ldap import FlextLdapModels
from flext_tap_ldap.tap_models import (
    ConnectionTestedEvent,
    LDAPConnection,
    LDAPRecord,
    LDAPStream,
    RecordExtractedEvent,
    StreamDiscoveredEvent,
    TapExecution,
    TapExecutionCompletedEvent,
    TapExecutionStartedEvent,
)


def _get_entry_value(
    entry: FlextTypes.Core.Dict | FlextLdapModels.Entry,
    key: str,
    default: object = None,
) -> object:
    """Get a value from either a dict or `FlextLdapModels.Entry`.

    Returns the attribute value by name from a plain dict or an attribute of
    a `FlextLdapModels.Entry`, falling back to `default` when not present.
    """
    if isinstance(entry, dict):
        return entry.get(key, default)
    # FlextLdapModels.Entry - use getattr or similar access pattern
    return getattr(entry, key, default)


def _safe_list_str(value: object) -> FlextTypes.Core.StringList:
    """Safely coerce a value to FlextTypes.Core.StringList."""
    if isinstance(value, list):
        return [str(v) for v in value]
    if isinstance(value, tuple):
        return [str(v) for v in value]
    if isinstance(value, str):
        # Single string treated as single-element list
        return [value]
    return []


def _safe_first_str(value: object) -> str | None:
    """Safely get the first string from a possibly list-like value."""
    if isinstance(value, (list, tuple)):
        return str(value[0]) if value else None
    if isinstance(value, str):
        return value
    return None


class FlextTapLdapModels(FlextModels):
    """Comprehensive models for LDAP tap operations extending FlextModels.

    Provides standardized models for all LDAP tap domain entities including:
    - Singer stream metadata and configuration
    - LDAP connection and authentication management
    - LDIF file processing operations
    - Performance monitoring and metrics collection
    - LDAP schema and directory operations

    All nested classes inherit FlextModels validation and patterns.
    """

    # Legacy type aliases for backward compatibility
    LDAPRecord = dict["str", "object"]
    LDAPRecords = list[LDAPRecord]

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

    class LdapEntry(FlextModels.BaseModel):
        """LDAP directory entry with comprehensive attribute handling."""

        # Entry identification
        dn: str = Field(..., description="Distinguished Name")
        object_classes: list[str] = Field(
            default_factory=list, description="LDAP object classes"
        )

        # Attributes (flexible structure for LDAP data)
        attributes: dict[str, list[str]] = Field(
            default_factory=dict, description="LDAP attributes with multi-value support"
        )

        # Metadata
        extracted_at: str = Field(description="Extraction timestamp")
        source_server: str | None = Field(
            default=None, description="Source LDAP server"
        )
        entry_uuid: str | None = Field(
            default=None, description="LDAP entry UUID if available"
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

    # Legacy compatibility - individual classes that map to nested classes
    class LDAPAttribute(BaseModel):
        """Legacy LDAP attribute model for backward compatibility."""

        name: str
        values: list[str]

        @classmethod
        def from_ldap_entry(
            cls, entry: FlextTapLdapModels.LdapEntry, attr_name: str
        ) -> FlextTapLdapModels.LDAPAttribute:
            """Create from LdapEntry for backward compatibility."""
            values = entry.attributes.get(attr_name, [])
            return cls(name=attr_name, values=values)

    class LDAPEntry(BaseModel):
        """Legacy LDAP entry model for backward compatibility."""

        dn: str
        attributes: dict[str, list[str]]

        @classmethod
        def from_ldap_entry(cls, entry: FlextTapLdapModels.LdapEntry) -> LDAPEntry:
            """Create from LdapEntry for backward compatibility."""
            return cls(dn=entry.dn, attributes=entry.attributes)

    class LDAPUser(BaseModel):
        """Legacy LDAP user model for backward compatibility."""

        dn: str
        cn: str | None = None
        mail: str | None = None

        @classmethod
        def from_ldap_user(cls, user: FlextTapLdapModels.LdapUser) -> LDAPUser:
            """Create from LdapUser for backward compatibility."""
            return cls(dn=user.dn, cn=user.cn, mail=user.mail)

    class LDAPGroup(BaseModel):
        """Legacy LDAP group model for backward compatibility."""

        dn: str
        cn: str | None = None
        members: list[str] = Field(default_factory=list)

        @classmethod
        def from_ldap_group(cls, group: FlextTapLdapModels.LdapGroup) -> LDAPGroup:
            """Create from LdapGroup for backward compatibility."""
            return cls(dn=group.dn, cn=group.cn, members=group.members)

    class LDAPSchema(BaseModel):
        """Legacy LDAP schema model for backward compatibility."""

        object_classes: list[str] = Field(default_factory=list)
        attributes: list[str] = Field(default_factory=list)

    # Legacy type aliases maintained for backward compatibility
    TapConfiguration = dict[str, object]
    StreamConfiguration = dict[str, object]


class FlextTapLdapUtilities(FlextUtilities):
    """Unified LDAP tap utilities extending FlextUtilities.

    Provides comprehensive utilities for LDAP Singer tap operations including:
    - LDAP connection validation and management
    - Singer tap configuration generation and validation
    - LDAP-to-Singer schema mapping and transformation
    - LDIF file processing and validation
    - Performance optimization for LDAP extraction operations
    - LDAP search filter generation and optimization
    """

    class _LdapConnectionHelper:
        """Helper for LDAP connection validation and management."""

        @staticmethod
        def validate_ldap_connection_config(config: dict) -> FlextResult[dict]:
            """Validate LDAP connection configuration completeness and security."""
            if not isinstance(config, dict):
                return FlextResult[dict].fail(
                    "LDAP connection config must be a dictionary"
                )

            required_fields = ["host", "bind_dn", "password", "base_dn"]
            missing_fields = [
                field for field in required_fields if not config.get(field)
            ]
            if missing_fields:
                return FlextResult[dict].fail(
                    f"Missing required LDAP connection fields: {missing_fields}"
                )

            # Validate port range
            port = config.get("port", 389)
            if not isinstance(port, int) or port < 1 or port > 65535:
                return FlextResult[dict].fail(
                    f"Invalid LDAP port: {port}. Must be between 1-65535"
                )

            # Validate SSL/TLS configuration consistency
            use_ssl = config.get("use_ssl", False)
            use_tls = config.get("use_tls", False)
            if use_ssl and use_tls:
                return FlextResult[dict].fail(
                    "Cannot enable both SSL and TLS simultaneously"
                )

            # Validate timeout settings
            timeout = config.get("timeout", 30)
            if not isinstance(timeout, int) or timeout < 1 or timeout > 300:
                return FlextResult[dict].fail(
                    f"Invalid timeout: {timeout}. Must be between 1-300 seconds"
                )

            # Validate page size for performance
            page_size = config.get("page_size", 1000)
            if not isinstance(page_size, int) or page_size < 1 or page_size > 10000:
                return FlextResult[dict].fail(
                    f"Invalid page_size: {page_size}. Must be between 1-10000"
                )

            # Validate base DN format
            base_dn = config["base_dn"]
            if not isinstance(base_dn, str) or "=" not in base_dn:
                return FlextResult[dict].fail(
                    f"Invalid base_dn format: {base_dn}. Must be valid LDAP DN"
                )

            return FlextResult[dict].ok(config)

        @staticmethod
        def generate_ldap_connection_string(config: dict) -> FlextResult[str]:
            """Generate LDAP connection string from configuration."""
            validation_result = FlextTapLdapUtilities._LdapConnectionHelper.validate_ldap_connection_config(
                config
            )
            if validation_result.is_failure:
                return FlextResult[str].fail(
                    f"LDAP config validation failed: {validation_result.error}"
                )

            protocol = "ldaps" if config.get("use_ssl") else "ldap"
            host = config["host"]
            port = config.get("port", 636 if config.get("use_ssl") else 389)

            connection_string = f"{protocol}://{host}:{port}"
            return FlextResult[str].ok(connection_string)

    class _SingerTapConfigHelper:
        """Helper for Singer tap configuration generation and validation."""

        @staticmethod
        def generate_ldap_singer_catalog(
            ldap_config: dict, streams: list[dict]
        ) -> FlextResult[dict]:
            """Generate Singer catalog for LDAP tap with proper schema definitions."""
            if not isinstance(ldap_config, dict):
                return FlextResult[dict].fail("LDAP configuration must be a dictionary")

            if not isinstance(streams, list) or not streams:
                return FlextResult[dict].fail(
                    "Streams configuration must be a non-empty list"
                )

            catalog_streams = []
            for stream_config in streams:
                if not isinstance(stream_config, dict):
                    return FlextResult[dict].fail(
                        "Each stream configuration must be a dictionary"
                    )

                stream_name = stream_config.get("stream_name")
                if not stream_name:
                    return FlextResult[dict].fail("Stream must have a stream_name")

                # Generate JSON schema for LDAP attributes
                schema_properties = {
                    "dn": {"type": "string", "description": "Distinguished Name"},
                    "objectClass": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "LDAP object classes",
                    },
                }

                # Add configured attributes to schema
                attributes = stream_config.get("attributes", [])
                for attr in attributes:
                    schema_properties[attr] = {
                        "type": ["string", "array", "null"],
                        "description": f"LDAP attribute: {attr}",
                    }

                # Add extracted timestamp
                schema_properties["_sdc_extracted_at"] = {
                    "type": "string",
                    "format": "date-time",
                    "description": "Singer extraction timestamp",
                }

                catalog_stream = {
                    "tap_stream_id": stream_name,
                    "stream": stream_name,
                    "schema": {
                        "type": "object",
                        "properties": schema_properties,
                        "required": ["dn"],
                        "additionalProperties": True,
                    },
                    "metadata": [
                        {
                            "breadcrumb": [],
                            "metadata": {
                                "replication-method": stream_config.get(
                                    "replication_method", "FULL_TABLE"
                                ),
                                "replication-key": stream_config.get("replication_key"),
                                "inclusion": "available",
                                "selected": True,
                            },
                        }
                    ],
                }

                catalog_streams.append(catalog_stream)

            catalog = {"version": 1, "streams": catalog_streams}

            return FlextResult[dict].ok(catalog)

        @staticmethod
        def validate_singer_tap_config(tap_config: dict) -> FlextResult[dict]:
            """Validate Singer tap configuration for LDAP extraction."""
            if not isinstance(tap_config, dict):
                return FlextResult[dict].fail("Singer tap config must be a dictionary")

            # Validate LDAP connection section
            ldap_section = tap_config.get("ldap_connection")
            if not ldap_section:
                return FlextResult[dict].fail(
                    "Missing ldap_connection section in tap config"
                )

            connection_validation = FlextTapLdapUtilities._LdapConnectionHelper.validate_ldap_connection_config(
                ldap_section
            )
            if connection_validation.is_failure:
                return FlextResult[dict].fail(
                    f"LDAP connection validation failed: {connection_validation.error}"
                )

            # Validate streams configuration
            streams = tap_config.get("streams", [])
            if not isinstance(streams, list):
                return FlextResult[dict].fail("Streams must be a list")

            for stream in streams:
                if not isinstance(stream, dict):
                    return FlextResult[dict].fail("Each stream must be a dictionary")

                stream_name = stream.get("stream_name")
                if not stream_name or not isinstance(stream_name, str):
                    return FlextResult[dict].fail(
                        "Each stream must have a valid stream_name"
                    )

                ldap_filter = stream.get("ldap_filter")
                if not ldap_filter or not isinstance(ldap_filter, str):
                    return FlextResult[dict].fail(
                        f"Stream {stream_name} must have a valid ldap_filter"
                    )

            return FlextResult[dict].ok(tap_config)

    class _LdapSchemaHelper:
        """Helper for LDAP-to-Singer schema mapping and transformations."""

        @staticmethod
        def map_ldap_attribute_to_json_type(
            ldap_attribute: str, ldap_syntax: str | None = None
        ) -> FlextResult[dict]:
            """Map LDAP attribute to JSON Schema type for Singer catalog."""
            if not isinstance(ldap_attribute, str) or not ldap_attribute.strip():
                return FlextResult[dict].fail(
                    "LDAP attribute name must be a non-empty string"
                )

            # Define common LDAP attribute type mappings
            attribute_type_mappings = {
                # String attributes
                "cn": {"type": "string"},
                "sn": {"type": "string"},
                "givenName": {"type": "string"},
                "displayName": {"type": "string"},
                "description": {"type": "string"},
                "mail": {"type": "string"},
                "userPrincipalName": {"type": "string"},
                "sAMAccountName": {"type": "string"},
                "distinguishedName": {"type": "string"},
                "name": {"type": "string"},
                # Multi-value string attributes
                "memberOf": {"type": "array", "items": {"type": "string"}},
                "member": {"type": "array", "items": {"type": "string"}},
                "objectClass": {"type": "array", "items": {"type": "string"}},
                "otherMailbox": {"type": "array", "items": {"type": "string"}},
                # Numeric attributes
                "employeeNumber": {"type": ["string", "integer"]},
                "userAccountControl": {"type": "integer"},
                "primaryGroupID": {"type": "integer"},
                "logonCount": {"type": "integer"},
                "badPwdCount": {"type": "integer"},
                # Date/time attributes
                "whenCreated": {"type": "string", "format": "date-time"},
                "whenChanged": {"type": "string", "format": "date-time"},
                "lastLogon": {"type": "string", "format": "date-time"},
                "lastLogonTimestamp": {"type": "string", "format": "date-time"},
                "pwdLastSet": {"type": "string", "format": "date-time"},
                "accountExpires": {"type": "string", "format": "date-time"},
                # Binary attributes
                "objectSid": {
                    "type": "string",
                    "description": "Base64 encoded binary data",
                },
                "objectGUID": {"type": "string", "description": "Base64 encoded GUID"},
                "thumbnailPhoto": {
                    "type": "string",
                    "description": "Base64 encoded image",
                },
                # Boolean-like attributes
                "isCriticalSystemObject": {"type": "boolean"},
                "showInAdvancedViewOnly": {"type": "boolean"},
            }

            # Check for exact match first
            if ldap_attribute in attribute_type_mappings:
                json_type = attribute_type_mappings[ldap_attribute]
                return FlextResult[dict].ok(json_type)

            # Use LDAP syntax to determine type if provided
            if ldap_syntax:
                syntax_mappings = {
                    "1.3.6.1.4.1.1466.115.121.1.15": {
                        "type": "string"
                    },  # Directory String
                    "1.3.6.1.4.1.1466.115.121.1.27": {"type": "integer"},  # Integer
                    "1.3.6.1.4.1.1466.115.121.1.7": {"type": "boolean"},  # Boolean
                    "1.3.6.1.4.1.1466.115.121.1.24": {
                        "type": "string",
                        "format": "date-time",
                    },  # Generalized Time
                    "1.3.6.1.4.1.1466.115.121.1.40": {"type": "string"},  # Octet String
                    "1.3.6.1.4.1.1466.115.121.1.12": {
                        "type": "string"
                    },  # Distinguished Name
                }

                if ldap_syntax in syntax_mappings:
                    json_type = syntax_mappings[ldap_syntax]
                    return FlextResult[dict].ok(json_type)

            # Default to flexible string/array type for unknown attributes
            default_type = {
                "type": ["string", "array", "null"],
                "description": f"LDAP attribute: {ldap_attribute}",
            }

            return FlextResult[dict].ok(default_type)

        @staticmethod
        def generate_ldap_search_filter_from_config(
            stream_config: dict,
        ) -> FlextResult[str]:
            """Generate optimized LDAP search filter from stream configuration."""
            if not isinstance(stream_config, dict):
                return FlextResult[str].fail(
                    "Stream configuration must be a dictionary"
                )

            # Start with explicit filter if provided
            base_filter = stream_config.get("ldap_filter")
            if not base_filter:
                return FlextResult[str].fail(
                    "Stream configuration must include ldap_filter"
                )

            # Validate filter syntax
            if not isinstance(base_filter, str) or not base_filter.strip():
                return FlextResult[str].fail("LDAP filter must be a non-empty string")

            # Basic filter validation - should start and end with parentheses
            filter_str = base_filter.strip()
            if not (filter_str.startswith("(") and filter_str.endswith(")")):
                return FlextResult[str].fail(
                    f"Invalid LDAP filter format: {filter_str}"
                )

            # Add replication key filter for incremental streams
            replication_method = stream_config.get("replication_method", "FULL_TABLE")
            if replication_method == "INCREMENTAL":
                replication_key = stream_config.get("replication_key")
                bookmark_value = stream_config.get("bookmark_value")

                if replication_key and bookmark_value:
                    # Combine base filter with incremental condition
                    incremental_filter = f"({replication_key}>={bookmark_value})"
                    combined_filter = f"(&{filter_str}{incremental_filter})"
                    return FlextResult[str].ok(combined_filter)

            return FlextResult[str].ok(filter_str)

    class _LdifProcessingHelper:
        """Helper for LDIF file processing and validation."""

        @staticmethod
        def validate_ldif_file_structure(ldif_file_path: str) -> FlextResult[dict]:
            """Validate LDIF file structure and readability."""
            if not isinstance(ldif_file_path, str) or not ldif_file_path.strip():
                return FlextResult[dict].fail(
                    "LDIF file path must be a non-empty string"
                )

            from pathlib import Path

            file_path = Path(ldif_file_path)

            # Check file existence
            if not file_path.exists():
                return FlextResult[dict].fail(
                    f"LDIF file does not exist: {ldif_file_path}"
                )

            # Check file readability
            if not file_path.is_file():
                return FlextResult[dict].fail(f"Path is not a file: {ldif_file_path}")

            # Check file size
            try:
                file_size = file_path.stat().st_size
                if file_size == 0:
                    return FlextResult[dict].fail(
                        f"LDIF file is empty: {ldif_file_path}"
                    )

                # Warn for very large files (>100MB)
                if file_size > 100 * 1024 * 1024:
                    validation_info = {
                        "file_path": str(file_path),
                        "file_size": file_size,
                        "warning": f"Large LDIF file detected ({file_size // (1024 * 1024)}MB). Consider processing in chunks.",
                    }
                else:
                    validation_info = {
                        "file_path": str(file_path),
                        "file_size": file_size,
                        "status": "valid",
                    }

                return FlextResult[dict].ok(validation_info)

            except OSError as e:
                return FlextResult[dict].fail(
                    f"Error accessing LDIF file {ldif_file_path}: {e}"
                )

        @staticmethod
        def estimate_ldif_processing_time(
            ldif_file_path: str, entries_per_second: int = 1000
        ) -> FlextResult[dict]:
            """Estimate LDIF file processing time based on file size and processing rate."""
            validation_result = FlextTapLdapUtilities._LdifProcessingHelper.validate_ldif_file_structure(
                ldif_file_path
            )
            if validation_result.is_failure:
                return FlextResult[dict].fail(
                    f"LDIF validation failed: {validation_result.error}"
                )

            file_info = validation_result.unwrap()
            file_size = file_info["file_size"]

            # Estimate number of entries (rough approximation: 1KB per entry average)
            estimated_entries = max(1, file_size // 1024)

            # Calculate estimated processing time
            estimated_seconds = estimated_entries / max(1, entries_per_second)
            estimated_minutes = estimated_seconds / 60
            estimated_hours = estimated_minutes / 60

            processing_estimate = {
                "file_path": ldif_file_path,
                "file_size_bytes": file_size,
                "estimated_entries": estimated_entries,
                "processing_rate_eps": entries_per_second,
                "estimated_duration_seconds": estimated_seconds,
                "estimated_duration_minutes": estimated_minutes,
                "estimated_duration_hours": estimated_hours,
                "human_readable": f"{estimated_minutes:.1f} minutes"
                if estimated_minutes < 60
                else f"{estimated_hours:.1f} hours",
            }

            return FlextResult[dict].ok(processing_estimate)

    class _PerformanceOptimizationHelper:
        """Helper for LDAP extraction performance optimization."""

        @staticmethod
        def optimize_ldap_search_parameters(
            config: dict, expected_results: int | None = None
        ) -> FlextResult[dict]:
            """Optimize LDAP search parameters based on expected results and server capabilities."""
            if not isinstance(config, dict):
                return FlextResult[dict].fail("Configuration must be a dictionary")

            optimized_config = config.copy()

            # Optimize page size based on expected results
            current_page_size = optimized_config.get("page_size", 1000)

            if expected_results:
                if expected_results < 100:
                    # Small result set - use smaller page size to reduce memory
                    optimized_page_size = min(100, expected_results)
                elif expected_results < 10000:
                    # Medium result set - use moderate page size
                    optimized_page_size = min(1000, expected_results // 10)
                else:
                    # Large result set - use larger page size for efficiency
                    optimized_page_size = min(5000, current_page_size)
            else:
                # No estimate - use conservative default
                optimized_page_size = 1000

            optimized_config["page_size"] = optimized_page_size

            # Optimize timeout based on page size
            base_timeout = optimized_config.get("timeout", 30)
            if optimized_page_size > 2000:
                # Larger page sizes may need more time
                optimized_config["timeout"] = min(120, base_timeout * 2)

            # Optimize connection pool for concurrent operations
            current_pool_size = optimized_config.get("connection_pool_size", 5)
            if expected_results and expected_results > 50000:
                # Large datasets benefit from more connections
                optimized_config["connection_pool_size"] = min(
                    10, current_pool_size + 2
                )

            # Add performance optimizations
            performance_settings = {
                "follow_referrals": optimized_config.get("follow_referrals", True),
                "auto_bind": True,
                "read_only": True,
                "receive_timeout": optimized_config.get("timeout", 30),
                "fast_decoder": True,
            }

            optimized_config["performance_settings"] = performance_settings

            optimization_summary = {
                "original_page_size": current_page_size,
                "optimized_page_size": optimized_page_size,
                "expected_results": expected_results,
                "optimization_applied": True,
                "performance_settings": performance_settings,
            }

            result = {
                "optimized_config": optimized_config,
                "optimization_summary": optimization_summary,
            }

            return FlextResult[dict].ok(result)

        @staticmethod
        def calculate_optimal_extraction_batch_size(
            stream_configs: list[dict],
        ) -> FlextResult[dict]:
            """Calculate optimal batch sizes for multiple LDAP stream extractions."""
            if not isinstance(stream_configs, list) or not stream_configs:
                return FlextResult[dict].fail(
                    "Stream configurations must be a non-empty list"
                )

            batch_recommendations = []
            total_memory_estimate = 0

            for i, stream_config in enumerate(stream_configs):
                if not isinstance(stream_config, dict):
                    return FlextResult[dict].fail(
                        f"Stream configuration {i} must be a dictionary"
                    )

                stream_name = stream_config.get("stream_name", f"stream_{i}")
                attributes = stream_config.get("attributes", [])
                expected_entries = stream_config.get("expected_entries", 1000)

                # Estimate memory per entry (rough approximation)
                avg_attr_size = 100  # bytes per attribute
                entry_size_estimate = (
                    len(attributes) * avg_attr_size + 200
                )  # base overhead

                # Calculate total memory for stream
                stream_memory_estimate = expected_entries * entry_size_estimate

                # Determine optimal batch size (target: ~10MB per batch)
                target_batch_memory = 10 * 1024 * 1024  # 10MB
                optimal_batch_size = max(
                    100, min(5000, target_batch_memory // entry_size_estimate)
                )

                batch_recommendation = {
                    "stream_name": stream_name,
                    "expected_entries": expected_entries,
                    "estimated_entry_size_bytes": entry_size_estimate,
                    "estimated_total_memory_mb": stream_memory_estimate / (1024 * 1024),
                    "recommended_batch_size": optimal_batch_size,
                    "estimated_batches": max(1, expected_entries // optimal_batch_size),
                }

                batch_recommendations.append(batch_recommendation)
                total_memory_estimate += stream_memory_estimate

            # Global recommendations
            global_recommendations = {
                "total_estimated_memory_mb": total_memory_estimate / (1024 * 1024),
                "recommended_parallel_streams": min(5, len(stream_configs)),
                "memory_warning": total_memory_estimate > 500 * 1024 * 1024,  # > 500MB
                "batch_recommendations": batch_recommendations,
            }

            return FlextResult[dict].ok(global_recommendations)


class LDAPEntry(FlextModels.Entity):
    """Represents an LDAP entry."""

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
            "dn": "self.dn",
            "objectClass": self.object_classes,
        }

        # Add attributes
        for name, value in self.attributes.items():
            if isinstance(value, FlextTapLdapModels.LDAPAttribute):
                result[name] = value.values
            else:
                result[name] = value

        return result

    @classmethod
    def from_dict(cls, data: FlextTypes.Core.Dict) -> LDAPEntry:
        """Create LDAPEntry from dictionary.

        Args:
            data: Dictionary with entry data.

        Returns:
            LDAPEntry instance.

        """
        return cls(
            dn=str(data.get("dn", "")),
            object_classes=_safe_list_str(data.get("objectClass", [])),
            attributes=data.get("attributes", {}),
        )


class LDAPUser(LDAPEntry):
    """Represents an LDAP user entry."""

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
        cls,
        entry: FlextTypes.Core.Dict | FlextLdapModels.Entry,
    ) -> LDAPUser:
        """Create LDAPUser from LDAP entry."""
        return cls(
            # Required fields from LDAPEntry
            dn=str(_get_entry_value(entry, "dn", "")),
            object_classes=_safe_list_str(_get_entry_value(entry, "objectClass", [])),
            # Optional metadata fields from LDAPEntry with defaults
            created_at=None,
            modified_at=None,
            created_by=None,
            modified_by=None,
            change_type=None,
            # LDAPUser specific fields with safe extraction
            uid=_safe_first_str(_get_entry_value(entry, "uid", [])),
            cn=_safe_first_str(_get_entry_value(entry, "cn", [])),
            sn=_safe_first_str(_get_entry_value(entry, "sn", [])),
            given_name=_safe_first_str(_get_entry_value(entry, "givenName", [])),
            display_name=_safe_first_str(_get_entry_value(entry, "displayName", [])),
            mail=_safe_first_str(_get_entry_value(entry, "mail", [])),
            telephone_number=_safe_first_str(
                _get_entry_value(entry, "telephoneNumber", []),
            ),
            mobile=_safe_first_str(_get_entry_value(entry, "mobile", [])),
            employee_number=_safe_first_str(
                _get_entry_value(entry, "employeeNumber", []),
            ),
            employee_type=_safe_first_str(
                _get_entry_value(entry, "employeeType", []),
            ),
            department=_safe_first_str(_get_entry_value(entry, "department", [])),
            title=_safe_first_str(_get_entry_value(entry, "title", [])),
            manager=_safe_first_str(_get_entry_value(entry, "manager", [])),
            home_directory=_safe_first_str(
                _get_entry_value(entry, "homeDirectory", []),
            ),
            login_shell=_safe_first_str(_get_entry_value(entry, "loginShell", [])),
        )


class LDAPGroup(LDAPEntry):
    """Represents an LDAP group entry."""

    cn: str | None = Field(None, description="Group name")
    description: str | None = Field(None, description="Group description")
    members: FlextTypes.Core.StringList = Field(
        default_factory=list,
        description="Member DNs",
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
        cls,
        entry: FlextTypes.Core.Dict | FlextLdapModels.Entry,
    ) -> LDAPGroup:
        """Create LDAPGroup from LDAP entry."""
        return cls(
            # Required fields from LDAPEntry
            dn=str(_get_entry_value(entry, "dn", "")),
            object_classes=_safe_list_str(_get_entry_value(entry, "objectClass", [])),
            # Optional metadata fields from LDAPEntry with defaults
            created_at=None,
            modified_at=None,
            created_by=None,
            modified_by=None,
            change_type=None,
            # LDAPGroup specific fields with safe extraction
            cn=_safe_first_str(_get_entry_value(entry, "cn", [])),
            description=_safe_first_str(_get_entry_value(entry, "description", [])),
            members=_safe_list_str(_get_entry_value(entry, "member", [])),
            unique_members=_safe_list_str(_get_entry_value(entry, "uniqueMember", [])),
            gid_number=_safe_first_str(_get_entry_value(entry, "gidNumber", [])),
            owner=None,
            create_timestamp=_safe_first_str(
                _get_entry_value(entry, "createTimestamp", []),
            ),
            modify_timestamp=_safe_first_str(
                _get_entry_value(entry, "modifyTimestamp", []),
            ),
        )


class LDAPSchema(FlextModels.Value):
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
        default_factory=list,
        description="LDAP syntaxes",
    )
    naming_contexts: FlextTypes.Core.StringList = Field(
        default_factory=list,
        description="Naming contexts",
    )

    def validate_business_rules(self: object) -> FlextResult[None]:
        """Validate business rules for LDAP schema."""
        # Schema validation rules can be added here
        return FlextResult[None].ok(None)

    @property
    def has_oracle_extensions(self: object) -> bool:
        """Check if schema contains Oracle-specific extensions.

        Returns:
            True if schema contains Oracle LDAP extensions.

        """
        oracle_prefixes = ["orcl", "oracl", "oid"]
        return any(
            any(oc.lower().startswith(prefix) for prefix in oracle_prefixes)
            for oc in self.object_classes
        )


# Public API: expose local value objects and re-exported domain entities/events
__all__ = [
    "ConnectionTestedEvent",
    "FlextTapLdapModels",
    "FlextTapLdapUtilities",
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
