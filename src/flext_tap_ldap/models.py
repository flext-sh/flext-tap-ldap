"""Domain models for tap-ldap using flext-core.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Self, cast

from flext_core import FlextConstants, FlextModels, FlextResult, FlextTypes
from pydantic import (
    ConfigDict,
    Field,
    computed_field,
    field_serializer,
    model_validator,
)

from flext_tap_ldap.typings import FlextTapLdapTypes


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

    # Pydantic 2.11 Configuration - Enterprise Singer Tap Features
    model_config = ConfigDict(
        validate_assignment=True,
        use_enum_values=True,
        arbitrary_types_allowed=True,
        extra="forbid",
        frozen=False,
        validate_return=True,
        ser_json_timedelta="iso8601",
        ser_json_bytes="base64",
        hide_input_in_errors=True,
        json_schema_extra={
            "title": "FLEXT Singer LDAP Tap Models",
            "description": "Enterprise LDAP data extraction models with Singer protocol compliance",
            "examples": [
                {
                    "tap_name": "tap-ldap",
                    "extraction_mode": "full_table",
                    "ldap_server": "ldap://directory.corp.com:389",
                }
            ],
            "tags": ["singer", "ldap", "tap", "extraction", "directory"],
            "version": "2.11.0",
        },
    )

    # Advanced Pydantic 2.11 Features - Singer Tap Domain

    @computed_field
    @property
    def active_tap_models_count(self) -> int:
        """Count of active LDAP tap models with extraction capabilities."""
        count = 0
        # Count core Singer tap models
        if hasattr(self, "LdapEntry"):
            count += 1
        if hasattr(self, "LdapUser"):
            count += 1
        if hasattr(self, "LdapGroup"):
            count += 1
        if hasattr(self, "LdapStream"):
            count += 1
        if hasattr(self, "TapExecution"):
            count += 1
        if hasattr(self, "LdapConnection"):
            count += 1
        if hasattr(self, "LdapConnectionConfig"):
            count += 1
        if hasattr(self, "LdapStreamMetadata"):
            count += 1
        if hasattr(self, "LdapRecord"):
            count += 1
        if hasattr(self, "LdapTapPerformanceMetrics"):
            count += 1
        return count

    @computed_field
    @property
    def tap_system_summary(self) -> FlextTypes.Dict:
        """Comprehensive Singer LDAP tap system summary with extraction capabilities."""
        return {
            "total_models": self.active_tap_models_count,
            "tap_type": "singer_ldap_extractor",
            "extraction_features": [
                "ldap_directory_scanning",
                "user_attribute_extraction",
                "group_membership_tracking",
                "schema_discovery",
                "incremental_replication",
                "performance_monitoring",
            ],
            "singer_compliance": {
                "protocol_version": "singer_v1",
                "stream_discovery": True,
                "catalog_generation": True,
                "state_management": True,
                "bookmarking": True,
            },
            "ldap_capabilities": {
                "connection_pooling": True,
                "ssl_tls_support": True,
                "paged_results": True,
                "referral_following": True,
                "schema_introspection": True,
            },
        }

    @model_validator(mode="after")
    def validate_tap_system_consistency(self) -> Self:
        """Validate Singer LDAP tap system consistency and configuration."""
        # Singer tap extraction validation
        extraction_streams = getattr(self, "_extraction_streams", None)
        if extraction_streams and not hasattr(self, "LdapStreamMetadata"):
            msg = "LdapStreamMetadata required when extraction streams configured"
            raise ValueError(msg)

        # LDAP connection validation
        ldap_config = getattr(self, "_ldap_config", None)
        if ldap_config and not hasattr(self, "LdapConnectionConfig"):
            msg = "LdapConnectionConfig required for LDAP tap operations"
            raise ValueError(msg)

        # Singer protocol compliance validation
        singer_mode = getattr(self, "_singer_mode", False)
        if singer_mode:
            required_models = ["LdapStream", "TapExecution", "LdapRecord"]
            for model in required_models:
                if not hasattr(self, model):
                    msg = f"{model} required for Singer protocol compliance"
                    raise ValueError(msg)

        return self

    @field_serializer("*", when_used="json")
    def serialize_with_tap_metadata(self, value: object, _info: object) -> object:
        """Add Singer LDAP tap metadata to all serialized fields."""
        if isinstance(value, dict):
            return {
                **value,
                "_tap_metadata": {
                    "extraction_timestamp": datetime.now(UTC).isoformat(),
                    "tap_type": "ldap_directory_extractor",
                    "singer_protocol": "v1.0",
                    "data_source": "ldap_directory",
                },
            }
        if isinstance(value, (str, int, float, bool)) and hasattr(
            self, "_include_tap_metadata"
        ):
            return {
                "value": value,
                "_tap_context": {
                    "extracted_at": datetime.now(UTC).isoformat(),
                    "tap_name": "flext-tap-ldap",
                },
            }
        return value

    # Legacy type aliases for backward compatibility
    LDAPRecord = FlextTypes.Dict
    LDAPRecords = list[LDAPRecord]

    class UtilityFunctions:
        """Utility functions for model data processing."""

        @staticmethod
        def get_entry_value(
            entry: FlextTapLdapTypes.Core.Dict | FlextTypes.Dict,
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
        def safe_list_str(value: object) -> FlextTypes.StringList:
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
        def safe_list_value(value: object) -> FlextTypes.List:
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

        # Pydantic 2.11 Configuration - LDAP Attribute Features
        model_config = ConfigDict(
            validate_assignment=True,
            extra="forbid",
            frozen=False,
            json_schema_extra={
                "description": "LDAP directory attribute with validation",
                "examples": [
                    {"name": "mail", "values": ["user@domain.com"], "is_binary": False}
                ],
            },
        )

        name: str = Field(..., description="Attribute name")
        values: FlextTapLdapTypes.Core.StringList = Field(
            ..., description="Attribute values"
        )
        is_binary: bool = Field(
            default=False,
            description="Whether the attribute contains binary data",
        )

        @computed_field
        @property
        def attribute_summary(self) -> FlextTypes.Dict:
            """LDAP attribute analysis summary."""
            return {
                "name": self.name,
                "value_count": len(self.values),
                "is_single_valued": len(self.values) == 1,
                "is_multi_valued": len(self.values) > 1,
                "is_binary": self.is_binary,
                "data_type": "binary" if self.is_binary else "string",
            }

        @model_validator(mode="after")
        def validate_ldap_attribute(self) -> Self:
            """Validate LDAP attribute constraints."""
            if not self.name:
                msg = "LDAP attribute name cannot be empty"
                raise ValueError(msg)
            if not self.values:
                msg = "LDAP attribute must have at least one value"
                raise ValueError(msg)
            return self

        def validate_domain_rules(self: object) -> FlextResult[None]:
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
            values = getattr(self, "values", None)
            return values[0] if values else None

        @property
        def is_multi_valued(self) -> bool:
            """Check if attribute has multiple values.

            Returns:
                True if attribute has more than one value.

            """
            values = getattr(self, "values", None)
            return len(values) > 1 if values else False

    class LdapConnectionConfig(FlextModels.ArbitraryTypesModel):
        """LDAP connection configuration with comprehensive settings."""

        # Pydantic 2.11 Configuration - Connection Features
        model_config = ConfigDict(
            validate_assignment=True,
            extra="forbid",
            frozen=False,
            json_schema_extra={
                "description": "LDAP server connection configuration",
                "examples": [
                    {
                        "host": "ldap.example.com",
                        "port": 389,
                        "bind_dn": "cn=admin,dc=example,dc=com",
                        "base_dn": "dc=example,dc=com",
                    }
                ],
            },
        )

        # LDAP Connection (required)
        host: str = Field(..., description="LDAP server hostname")
        port: int = Field(
            default=FlextConstants.Platform.LDAP_DEFAULT_PORT,
            ge=1,
            le=65535,
            description="LDAP server port",
        )
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
            default=FlextConstants.Network.DEFAULT_TIMEOUT,
            ge=1,
            le=300,
            description="Connection timeout in seconds",
        )
        page_size: int = Field(
            default=FlextConstants.Performance.BatchProcessing.DEFAULT_SIZE,
            ge=1,
            le=10000,
            description="LDAP paging size",
        )
        connection_pool_size: int = Field(
            default=FlextConstants.Container.DEFAULT_WORKERS,
            ge=1,
            le=20,
            description="Connection pool size",
        )

        # LDIF Processing
        enable_ldif_streams: bool = Field(
            default=False, description="Enable LDIF file processing"
        )
        ldif_files: FlextTypes.StringList = Field(
            default_factory=list, description="List of LDIF files to process"
        )
        ldif_directory: str | None = Field(
            default=None, description="Directory containing LDIF files"
        )
        ldif_ignore_errors: bool = Field(
            default=True, description="Continue processing on LDIF errors"
        )
        ldif_max_errors: int = Field(
            default=FlextConstants.Performance.BatchProcessing.DEFAULT_SIZE // 10,
            ge=0,
            le=10000,
            description="Maximum LDIF errors allowed",
        )

        @computed_field
        @property
        def connection_summary(self) -> FlextTypes.Dict:
            """LDAP connection configuration summary."""
            return {
                "server": f"{self.host}:{self.port}",
                "security": {
                    "ssl": self.use_ssl,
                    "tls": self.use_tls,
                    "has_client_cert": bool(self.cert_file),
                },
                "performance": {
                    "timeout": self.timeout,
                    "page_size": self.page_size,
                    "pool_size": self.connection_pool_size,
                },
                "ldif_enabled": self.enable_ldif_streams,
            }

        @model_validator(mode="after")
        def validate_connection_config(self) -> Self:
            """Validate LDAP connection configuration."""
            if self.use_ssl and self.use_tls:
                msg = "Cannot use both SSL and StartTLS simultaneously"
                raise ValueError(msg)
            if self.cert_file and not self.key_file:
                msg = "Client certificate requires private key file"
                raise ValueError(msg)
            return self

    class LdapStreamMetadata(FlextModels.Entity):
        """LDAP stream metadata with Singer protocol compliance."""

        # Pydantic 2.11 Configuration - Stream Features
        model_config = ConfigDict(
            validate_assignment=True,
            extra="forbid",
            frozen=False,
            json_schema_extra={
                "description": "Singer stream configuration for LDAP extraction",
                "examples": [
                    {
                        "stream_name": "users",
                        "ldap_filter": "(objectClass=inetOrgPerson)",
                        "replication_method": "FULL_TABLE",
                    }
                ],
            },
        )

        # Singer stream configuration
        stream_name: str = Field(..., description="Singer stream name")
        ldap_filter: str = Field(..., description="LDAP search filter for this stream")
        base_dn: str | None = Field(
            default=None, description="Specific base DN for this stream"
        )
        attributes: FlextTypes.StringList = Field(
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
        page_size: int = Field(
            default=FlextConstants.Performance.BatchProcessing.DEFAULT_SIZE,
            description="Results page size",
        )
        follow_referrals: bool = Field(
            default=True, description="Follow LDAP referrals"
        )

        @computed_field
        @property
        def stream_config_summary(self) -> FlextTypes.Dict:
            """Singer stream configuration summary."""
            return {
                "stream_name": self.stream_name,
                "extraction_type": self.replication_method,
                "ldap_settings": {
                    "filter": self.ldap_filter,
                    "scope": self.search_scope,
                    "page_size": self.page_size,
                },
                "attribute_count": len(self.attributes),
                "incremental": bool(self.replication_key),
            }

        @model_validator(mode="after")
        def validate_stream_metadata(self) -> Self:
            """Validate Singer stream metadata."""
            if not self.stream_name:
                msg = "Singer stream name is required"
                raise ValueError(msg)
            if not self.ldap_filter:
                msg = "LDAP filter is required for stream"
                raise ValueError(msg)
            return self

    class LdapEntry(FlextModels.Entity):
        """Represents an LDAP directory entry with comprehensive attributes."""

        # Pydantic 2.11 Configuration - Entry Features
        model_config = ConfigDict(
            validate_assignment=True,
            extra="forbid",
            frozen=False,
            json_schema_extra={
                "description": "LDAP directory entry with full attribute support",
                "examples": [
                    {
                        "dn": "cn=John Doe,ou=users,dc=example,dc=com",
                        "object_classes": ["inetOrgPerson", "organizationalPerson"],
                    }
                ],
            },
        )

        dn: str = Field(..., description="Distinguished Name")
        object_classes: FlextTapLdapTypes.Core.StringList = Field(
            ...,
            description="Object classes",
        )

        @computed_field
        @property
        def entry_summary(self) -> FlextTypes.Dict:
            """LDAP entry analysis summary."""
            return {
                "dn": self.dn,
                "object_class_count": len(self.object_classes),
                "primary_object_class": self.object_classes[0]
                if self.object_classes
                else None,
                "attribute_count": len(self.attributes)
                if hasattr(self, "attributes")
                else 0,
                "entry_type": "user"
                if any("person" in oc.lower() for oc in self.object_classes)
                else "other",
            }

        @model_validator(mode="after")
        def validate_ldap_entry(self) -> Self:
            """Validate LDAP entry structure."""
            if not self.dn:
                msg = "DN cannot be empty"
                raise ValueError(msg)
            if not self.object_classes:
                msg = "LDAP entry must have at least one object class"
                raise ValueError(msg)
            return self

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate business rules for LDAP entries."""
            if not self.dn:
                return FlextResult[None].fail("DN cannot be empty")
            # Additional LDAP entry validation can be added here
            return FlextResult[None].ok(None)

        attributes: FlextTapLdapTypes.Core.Dict = Field(
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
        # created_at is inherited from TimestampedModel
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
        controls: FlextTapLdapTypes.Core.StringList = Field(
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

        def to_dict(self) -> FlextTapLdapTypes.Core.Dict:
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
        def from_dict(
            cls, data: FlextTapLdapTypes.Core.Dict
        ) -> FlextTapLdapModels.LdapEntry:
            """Create LdapEntry from dictionary.

            Args:
                data: Dictionary with entry data.

            Returns:
                LdapEntry instance.

            """
            return cls(
                dn=cast("str", data.get("dn", "")),
                object_classes=FlextTapLdapModels.UtilityFunctions.safe_list_str(
                    data.get("objectClass", [])
                ),
                attributes=cast(
                    "FlextTapLdapTypes.Core.Dict", data.get("attributes", {})
                ),
                extracted_at=cast(
                    "str", data.get("extracted_at", datetime.now(UTC).isoformat())
                ),
                modified_at=cast("datetime | None", data.get("modified_at")),
                created_by=cast("str | None", data.get("created_by")),
                modified_by=cast("str | None", data.get("modified_by")),
                change_type=cast("str | None", data.get("change_type")),
            )

    class LdapUser(FlextModels.ArbitraryTypesModel):
        """LDAP user entry with standard inetOrgPerson attributes."""

        # Pydantic 2.11 Configuration - User Features
        model_config = ConfigDict(
            validate_assignment=True,
            extra="forbid",
            frozen=False,
            json_schema_extra={
                "description": "LDAP user with inetOrgPerson attributes",
                "examples": [
                    {
                        "dn": "cn=John Doe,ou=users,dc=example,dc=com",
                        "uid": "jdoe",
                        "mail": "john.doe@example.com",
                    }
                ],
            },
        )

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
        member_of: FlextTypes.StringList = Field(
            default_factory=list, description="Group memberships"
        )

        @computed_field
        @property
        def user_profile_summary(self) -> FlextTypes.Dict:
            """LDAP user profile summary."""
            return {
                "user_id": self.uid,
                "full_name": f"{self.given_name or ''} {self.sn or ''}".strip(),
                "email": self.mail,
                "department": self.department,
                "group_count": len(self.member_of),
                "has_manager": bool(self.manager),
                "profile_completeness": sum([
                    bool(self.uid),
                    bool(self.mail),
                    bool(self.given_name),
                    bool(self.sn),
                    bool(self.department),
                ])
                / 5,
            }

        @model_validator(mode="after")
        def validate_user_entry(self) -> Self:
            """Validate LDAP user entry."""
            if not self.dn:
                msg = "User DN is required"
                raise ValueError(msg)
            if self.mail and "@" not in self.mail:
                msg = "Invalid email format"
                raise ValueError(msg)
            return self

    class LdapGroup(FlextModels.ArbitraryTypesModel):
        """LDAP group entry with membership management."""

        # Pydantic 2.11 Configuration - Group Features
        model_config = ConfigDict(
            validate_assignment=True,
            extra="forbid",
            frozen=False,
            json_schema_extra={
                "description": "LDAP group with membership tracking",
                "examples": [
                    {
                        "dn": "cn=Developers,ou=groups,dc=example,dc=com",
                        "cn": "Developers",
                        "members": ["cn=John Doe,ou=users,dc=example,dc=com"],
                    }
                ],
            },
        )

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
        members: FlextTypes.StringList = Field(
            default_factory=list, description="Group member DNs"
        )
        member_of: FlextTypes.StringList = Field(
            default_factory=list, description="Parent group memberships"
        )

        # Metadata
        when_created: str | None = Field(
            default=None, description="Group creation timestamp"
        )
        when_changed: str | None = Field(
            default=None, description="Last modification timestamp"
        )

        @computed_field
        @property
        def group_membership_summary(self) -> FlextTypes.Dict:
            """LDAP group membership summary."""
            return {
                "group_name": self.cn,
                "member_count": len(self.members),
                "parent_group_count": len(self.member_of),
                "group_type": self.group_type,
                "has_nested_groups": any(
                    "ou=groups" in member for member in self.members
                ),
                "is_nested": bool(self.member_of),
            }

        @model_validator(mode="after")
        def validate_group_entry(self) -> Self:
            """Validate LDAP group entry."""
            if not self.dn:
                msg = "Group DN is required"
                raise ValueError(msg)
            if not self.cn:
                msg = "Group common name is required"
                raise ValueError(msg)
            return self

    class LdapSchema(FlextModels.ArbitraryTypesModel):
        """LDAP schema information with object classes and attributes."""

        # Pydantic 2.11 Configuration - Schema Features
        model_config = ConfigDict(
            validate_assignment=True,
            extra="forbid",
            frozen=False,
            json_schema_extra={
                "description": "LDAP schema definition and introspection",
                "examples": [
                    {
                        "object_classes": ["inetOrgPerson", "organizationalPerson"],
                        "attributes": ["cn", "sn", "mail", "uid"],
                    }
                ],
            },
        )

        object_classes: FlextTypes.StringList = Field(
            default_factory=list, description="Available object classes"
        )
        attributes: FlextTypes.StringList = Field(
            default_factory=list, description="Available attributes"
        )
        syntax_definitions: FlextTypes.StringDict = Field(
            default_factory=dict, description="Attribute syntax definitions"
        )

        @computed_field
        @property
        def schema_analysis_summary(self) -> FlextTypes.Dict:
            """LDAP schema analysis summary."""
            return {
                "object_class_count": len(self.object_classes),
                "attribute_count": len(self.attributes),
                "syntax_count": len(self.syntax_definitions),
                "has_person_classes": any(
                    "person" in oc.lower() for oc in self.object_classes
                ),
                "has_group_classes": any(
                    "group" in oc.lower() for oc in self.object_classes
                ),
            }

    class LdapConnection(FlextModels.Entity):
        """LDAP connection state and configuration."""

        # Pydantic 2.11 Configuration - Connection Features
        model_config = ConfigDict(
            validate_assignment=True,
            extra="forbid",
            frozen=False,
            json_schema_extra={
                "description": "LDAP connection state and performance tracking",
                "examples": [
                    {"host": "ldap.example.com", "port": 389, "is_connected": True}
                ],
            },
        )

        host: str = Field(..., description="LDAP server host")
        port: int = Field(..., description="LDAP server port")
        bind_dn: str = Field(..., description="Bind DN")
        password: str | None = Field(default=None, description="Bind password")
        use_ssl: bool = Field(default=False, description="Use SSL connection")
        timeout: int = Field(
            default=FlextConstants.Network.DEFAULT_TIMEOUT,
            description="Connection timeout in seconds",
        )
        pool_size: int = Field(
            default=FlextConstants.Container.DEFAULT_WORKERS,
            description="Connection pool size",
        )
        is_active: bool = Field(default=True, description="Connection active status")
        is_connected: bool = Field(default=False, description="Connection status")
        connection_time: float = Field(
            default=0.0, description="Connection establishment time"
        )
        last_operation: str | None = Field(
            default=None, description="Last LDAP operation"
        )
        last_tested: datetime | None = Field(
            default=None, description="Last connection test time"
        )
        last_error: str | None = Field(default=None, description="Last error message")

        @computed_field
        @property
        def connection_health_summary(self) -> FlextTypes.Dict:
            """LDAP connection health summary."""
            return {
                "server": f"{self.host}:{self.port}",
                "status": "connected" if self.is_connected else "disconnected",
                "security": "ssl" if self.use_ssl else "plain",
                "performance": {
                    "connection_time": self.connection_time,
                    "pool_size": self.pool_size,
                    "timeout": self.timeout,
                },
                "health": "healthy"
                if self.is_connected and not self.last_error
                else "degraded",
            }

        @model_validator(mode="after")
        def validate_connection_state(self) -> Self:
            """Validate LDAP connection state."""
            if not self.host:
                msg = "LDAP host is required"
                raise ValueError(msg)
            if not (1 <= self.port <= FlextConstants.Network.MAX_PORT):
                msg = "Invalid port number"
                raise ValueError(msg)
            return self

    class LdapStream(FlextModels.Entity):
        """Singer stream configuration for LDAP data."""

        # Pydantic 2.11 Configuration - Stream Features
        model_config = ConfigDict(
            validate_assignment=True,
            extra="forbid",
            frozen=False,
            json_schema_extra={
                "description": "Singer stream with LDAP extraction configuration",
                "examples": [
                    {
                        "name": "users",
                        "tap_stream_id": "users",
                        "search_filter": "(objectClass=inetOrgPerson)",
                    }
                ],
            },
        )

        name: str = Field(..., description="Stream name")
        connection_id: str = Field(..., description="Associated connection ID")
        stream_type: str = Field(..., description="Type of LDAP stream")
        search_filter: str = Field(..., description="LDAP search filter")
        attributes: FlextTypes.StringList = Field(
            default_factory=list, description="LDAP attributes"
        )
        tap_stream_id: str = Field(..., description="Singer tap stream ID")
        key_properties: FlextTypes.StringList = Field(
            default_factory=list, description="Key properties"
        )
        replication_method: str = Field(
            default="FULL_TABLE", description="Replication method"
        )
        replication_key: str | None = Field(
            default=None, description="Replication key attribute"
        )
        stream_schema: FlextTypes.Dict = Field(
            default_factory=dict, description="Stream JSON schema"
        )
        json_schema: FlextTypes.Dict = Field(
            default_factory=dict, description="JSON schema"
        )
        metadata: list[FlextTypes.Dict] = Field(
            default_factory=list, description="Stream metadata"
        )

        @computed_field
        @property
        def stream_extraction_summary(self) -> FlextTypes.Dict:
            """Singer stream extraction summary."""
            return {
                "stream_id": self.tap_stream_id,
                "extraction_type": self.replication_method,
                "ldap_filter": self.search_filter,
                "attribute_count": len(self.attributes),
                "has_schema": bool(self.json_schema),
                "is_incremental": bool(self.replication_key),
            }

        @model_validator(mode="after")
        def validate_stream_config(self) -> Self:
            """Validate Singer stream configuration."""
            if not self.name:
                msg = "Stream name is required"
                raise ValueError(msg)
            if not self.search_filter:
                msg = "LDAP search filter is required"
                raise ValueError(msg)
            return self

        def update_schema(self, schema: FlextTypes.Dict) -> None:
            """Update stream schema."""
            self.json_schema = schema
            self.stream_schema = schema

    class TapExecution(FlextModels.Entity):
        """Tap execution tracking and state management."""

        # Pydantic 2.11 Configuration - Execution Features
        model_config = ConfigDict(
            validate_assignment=True,
            extra="forbid",
            frozen=False,
            json_schema_extra={
                "description": "Singer tap execution with state tracking",
                "examples": [
                    {
                        "execution_id": "exec_123",
                        "command": "tap-ldap",
                        "tap_status": "running",
                    }
                ],
            },
        )

        execution_id: str = Field(..., description="Unique execution identifier")
        connection_id: str = Field(..., description="Associated connection ID")
        command: str = Field(..., description="Tap command executed")
        tap_status: str = Field(default="created", description="Tap execution status")
        config: FlextTypes.Dict = Field(
            default_factory=dict, description="Tap configuration"
        )
        catalog: FlextTypes.Dict = Field(
            default_factory=dict, description="Tap catalog"
        )
        state: FlextTypes.Dict = Field(default_factory=dict, description="Tap state")
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
        exit_code: int | None = Field(default=None, description="Process exit code")
        stdout: str | None = Field(default=None, description="Standard output")
        stderr: str | None = Field(default=None, description="Standard error")

        @computed_field
        @property
        def execution_performance_summary(self) -> FlextTypes.Dict:
            """Tap execution performance summary."""
            duration = 0.0
            if self.completed_at and self.started_at:
                duration = (self.completed_at - self.started_at).total_seconds()

            return {
                "execution_id": self.execution_id,
                "status": self.tap_status,
                "duration_seconds": duration,
                "records_extracted": self.records_extracted,
                "streams_processed": self.streams_processed,
                "records_per_second": self.records_extracted / duration
                if duration > 0
                else 0,
                "success": self.exit_code == 0 if self.exit_code is not None else None,
            }

        @model_validator(mode="after")
        def validate_execution_state(self) -> Self:
            """Validate tap execution state."""
            if not self.execution_id:
                msg = "Execution ID is required"
                raise ValueError(msg)
            if not self.command:
                msg = "Tap command is required"
                raise ValueError(msg)
            return self

        def start_execution(self) -> None:
            """Start the execution."""
            self.tap_status = "discovering"
            self.started_at = datetime.now(UTC)

        def complete_execution(
            self, exit_code: int, stdout: str | None = None, stderr: str | None = None
        ) -> None:
            """Complete the execution."""
            self.tap_status = "completed"
            self.exit_code = exit_code
            self.stdout = stdout
            self.stderr = stderr
            self.completed_at = datetime.now(UTC)

        def cancel_execution(self) -> None:
            """Cancel the execution."""
            self.tap_status = "cancelled"
            self.completed_at = datetime.now(UTC)

        def update_metrics(
            self, records_extracted: int, streams_processed: int
        ) -> None:
            """Update execution metrics."""
            self.records_extracted = records_extracted
            self.streams_processed = streams_processed

    class LdapRecord(FlextModels.ArbitraryTypesModel):
        """Individual LDAP record for Singer output."""

        # Pydantic 2.11 Configuration - Record Features
        model_config = ConfigDict(
            validate_assignment=True,
            extra="forbid",
            frozen=False,
            json_schema_extra={
                "description": "Singer LDAP record with extraction metadata",
                "examples": [
                    {
                        "stream": "users",
                        "record": {"dn": "cn=John,dc=example,dc=com"},
                        "time_extracted": "2023-01-01T00:00:00Z",
                    }
                ],
            },
        )

        stream: str = Field(..., description="Source stream name")
        record: FlextTypes.Dict = Field(..., description="Record data")
        time_extracted: datetime = Field(
            default_factory=lambda: datetime.now(UTC),
            description="Extraction timestamp",
        )

        @computed_field
        @property
        def record_analysis_summary(self) -> FlextTypes.Dict:
            """LDAP record analysis summary."""
            return {
                "stream": self.stream,
                "field_count": len(self.record),
                "has_dn": "dn" in self.record,
                "extraction_time": self.time_extracted.isoformat(),
                "record_size_bytes": len(str(self.record).encode("utf-8")),
            }

        @model_validator(mode="after")
        def validate_ldap_record(self) -> Self:
            """Validate LDAP record structure."""
            if not self.stream:
                msg = "Stream name is required"
                raise ValueError(msg)
            if not self.record:
                msg = "Record data cannot be empty"
                raise ValueError(msg)
            return self

    # Event Models with Enhanced Features

    class TapExecutionStartedEvent(FlextModels.DomainEvent):
        """Domain event for tap execution start."""

        # Pydantic 2.11 Configuration - Event Features
        model_config = ConfigDict(
            validate_assignment=True,
            extra="forbid",
            frozen=True,
            json_schema_extra={
                "description": "Singer tap execution started event",
                "examples": [
                    {"execution_id": "exec_123", "config": {"host": "ldap.example.com"}}
                ],
            },
        )

        execution_id: str = Field(..., description="Execution identifier")
        config: FlextTypes.Dict = Field(..., description="Tap configuration")

        @computed_field
        @property
        def event_summary(self) -> FlextTypes.Dict:
            """Tap execution started event summary."""
            return {
                "event_type": "tap_execution_started",
                "execution_id": self.execution_id,
                "config_keys": list(self.config.keys()),
                "timestamp": self.created_at.isoformat()
                if hasattr(self, "created_at")
                else None,
            }

    class TapExecutionCompletedEvent(FlextModels.DomainEvent):
        """Domain event for tap execution completion."""

        # Pydantic 2.11 Configuration - Event Features
        model_config = ConfigDict(
            validate_assignment=True,
            extra="forbid",
            frozen=True,
            json_schema_extra={
                "description": "Singer tap execution completed event",
                "examples": [
                    {
                        "execution_id": "exec_123",
                        "records_extracted": 1000,
                        "duration": 30.5,
                    }
                ],
            },
        )

        execution_id: str = Field(..., description="Execution identifier")
        records_extracted: int = Field(..., description="Total records extracted")
        duration: float = Field(..., description="Execution duration in seconds")

        @computed_field
        @property
        def completion_summary(self) -> FlextTypes.Dict:
            """Tap execution completion summary."""
            return {
                "event_type": "tap_execution_completed",
                "execution_id": self.execution_id,
                "performance": {
                    "records_extracted": self.records_extracted,
                    "duration_seconds": self.duration,
                    "records_per_second": self.records_extracted / self.duration
                    if self.duration > 0
                    else 0,
                },
                "success": True,
            }

    class StreamDiscoveredEvent(FlextModels.DomainEvent):
        """Domain event for stream discovery."""

        # Pydantic 2.11 Configuration - Event Features
        model_config = ConfigDict(
            validate_assignment=True,
            extra="forbid",
            frozen=True,
            json_schema_extra={
                "description": "Singer stream discovery event",
                "examples": [
                    {
                        "stream_name": "users",
                        "schema": {"type": "object", "properties": {}},
                    }
                ],
            },
        )

        stream_name: str = Field(..., description="Discovered stream name")
        stream_schema: FlextTypes.Dict = Field(..., description="Stream schema")

        @computed_field
        @property
        def discovery_summary(self) -> FlextTypes.Dict:
            """Stream discovery summary."""
            return {
                "event_type": "stream_discovered",
                "stream_name": self.stream_name,
                "schema_properties": len(self.stream_schema.get("properties", {})),
                "has_key_properties": bool(self.stream_schema.get("key_properties")),
            }

    class RecordExtractedEvent(FlextModels.DomainEvent):
        """Domain event for record extraction."""

        # Pydantic 2.11 Configuration - Event Features
        model_config = ConfigDict(
            validate_assignment=True,
            extra="forbid",
            frozen=True,
            json_schema_extra={
                "description": "LDAP record extraction event",
                "examples": [
                    {
                        "stream_name": "users",
                        "record": {"dn": "cn=John,dc=example,dc=com"},
                    }
                ],
            },
        )

        stream_name: str = Field(..., description="Source stream")
        record: FlextTypes.Dict = Field(..., description="Extracted record")

        @computed_field
        @property
        def extraction_summary(self) -> FlextTypes.Dict:
            """Record extraction summary."""
            return {
                "event_type": "record_extracted",
                "stream_name": self.stream_name,
                "record_fields": len(self.record),
                "has_dn": "dn" in self.record,
                "record_type": "ldap_entry",
            }

    class ConnectionTestedEvent(FlextModels.DomainEvent):
        """Domain event for connection testing."""

        # Pydantic 2.11 Configuration - Event Features
        model_config = ConfigDict(
            validate_assignment=True,
            extra="forbid",
            frozen=True,
            json_schema_extra={
                "description": "LDAP connection test event",
                "examples": [
                    {"host": "ldap.example.com", "success": True, "error_message": None}
                ],
            },
        )

        host: str = Field(..., description="LDAP server host")
        success: bool = Field(..., description="Connection test result")
        error_message: str | None = Field(
            default=None, description="Error message if failed"
        )

        @computed_field
        @property
        def connection_test_summary(self) -> FlextTypes.Dict:
            """Connection test summary."""
            return {
                "event_type": "connection_tested",
                "host": self.host,
                "test_result": "success" if self.success else "failure",
                "has_error": bool(self.error_message),
            }

    # Processing and Performance Models with Enhanced Features

    class LdifProcessingState(FlextModels.ArbitraryTypesModel):
        """LDIF file processing state and statistics."""

        # Pydantic 2.11 Configuration - Processing Features
        model_config = ConfigDict(
            validate_assignment=True,
            extra="forbid",
            frozen=False,
            json_schema_extra={
                "description": "LDIF file processing state with comprehensive statistics",
                "examples": [
                    {
                        "file_path": "/data/users.ldif",
                        "entries_processed": 1000,
                        "start_time": "2023-01-01T00:00:00Z",
                    }
                ],
            },
        )

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
        errors: FlextTypes.StringList = Field(
            default_factory=list, description="Processing errors"
        )
        warnings: FlextTypes.StringList = Field(
            default_factory=list, description="Processing warnings"
        )

        @computed_field
        @property
        def processing_performance_summary(self) -> FlextTypes.Dict:
            """LDIF processing performance summary."""
            success_rate = 0.0
            if self.entries_processed > 0:
                success_rate = (
                    self.entries_processed - self.entries_failed
                ) / self.entries_processed

            return {
                "file_path": self.file_path,
                "processing_status": "completed" if self.end_time else "in_progress",
                "performance": {
                    "entries_processed": self.entries_processed,
                    "success_rate": success_rate,
                    "duration_seconds": self.processing_duration,
                    "entries_per_second": self.entries_processed
                    / self.processing_duration
                    if self.processing_duration > 0
                    else 0,
                },
                "quality": {
                    "error_count": len(self.errors),
                    "warning_count": len(self.warnings),
                    "change_records": self.change_records,
                },
            }

        @model_validator(mode="after")
        def validate_processing_state(self) -> Self:
            """Validate LDIF processing state."""
            if not self.file_path:
                msg = "LDIF file path is required"
                raise ValueError(msg)
            if self.entries_failed > self.entries_processed:
                msg = "Failed entries cannot exceed processed entries"
                raise ValueError(msg)
            return self

    class LdapTapPerformanceMetrics(FlextModels.ArbitraryTypesModel):
        """Performance metrics for LDAP tap operations."""

        # Pydantic 2.11 Configuration - Metrics Features
        model_config = ConfigDict(
            validate_assignment=True,
            extra="forbid",
            frozen=False,
            json_schema_extra={
                "description": "LDAP tap performance metrics with comprehensive monitoring",
                "examples": [
                    {
                        "connection_time": 0.5,
                        "total_entries": 10000,
                        "entries_per_second": 500.0,
                    }
                ],
            },
        )

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

        @computed_field
        @property
        def performance_analysis_summary(self) -> FlextTypes.Dict:
            """LDAP tap performance analysis summary."""
            total_errors = (
                self.connection_errors + self.search_errors + self.timeout_errors
            )
            error_rate = (
                total_errors / self.ldap_operations if self.ldap_operations > 0 else 0
            )

            return {
                "extraction_performance": {
                    "total_entries": self.total_entries,
                    "entries_per_second": self.entries_per_second,
                    "total_bytes": self.total_bytes,
                    "bytes_per_second": self.bytes_per_second,
                },
                "ldap_operations": {
                    "total_operations": self.ldap_operations,
                    "paged_searches": self.paged_searches,
                    "referrals_followed": self.referrals_followed,
                },
                "reliability": {
                    "total_errors": total_errors,
                    "error_rate": error_rate,
                    "connection_errors": self.connection_errors,
                    "search_errors": self.search_errors,
                    "timeout_errors": self.timeout_errors,
                },
                "efficiency": {
                    "connection_time": self.connection_time,
                    "search_time": self.search_time,
                    "streams_processed": self.streams_processed,
                },
            }

        @model_validator(mode="after")
        def validate_performance_metrics(self) -> Self:
            """Validate performance metrics consistency."""
            if self.total_entries < 0 or self.total_bytes < 0:
                msg = "Volume metrics cannot be negative"
                raise ValueError(msg)
            if self.entries_per_second < 0 or self.bytes_per_second < 0:
                msg = "Rate metrics cannot be negative"
                raise ValueError(msg)
            return self

    # Legacy type aliases maintained for backward compatibility
    TapConfiguration = FlextTypes.Dict
    StreamConfiguration = FlextTypes.Dict

    # Convenience accessors for backward compatibility
    @classmethod
    def get_entry_value(
        cls, entry: FlextTypes.Dict, key: str, default: object = None
    ) -> object:
        """Convenience method for getting entry values."""
        return cls.UtilityFunctions.get_entry_value(entry, key, default)

    @classmethod
    def safe_list_str(cls, value: object) -> FlextTypes.StringList:
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
