"""Configuration models for tap-ldap v0.7.0 using flext-core patterns.

MIGRATED TO FLEXT-CORE:
Uses flext-core DomainValueObject and configuration patterns. Zero tolerance for code duplication.
"""

from __future__ import annotations

from typing import Any

from pydantic import Field
from pydantic import field_validator
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict

from flext_core.domain.pydantic_base import DomainValueObject


class LDAPConnectionConfig(DomainValueObject):
    """LDAP connection configuration using flext-core value object patterns."""

    # Connection settings
    host: str = Field(..., description="LDAP server hostname or IP address")
    port: int = Field(default=389, description="LDAP server port (389 for LDAP, 636 for LDAPS)")
    bind_dn: str | None = Field(default=None, description="Distinguished name for binding to LDAP")
    password: str | None = Field(default=None, description="Password for LDAP authentication")
    base_dn: str = Field(..., description="Base DN for LDAP searches")
    use_ssl: bool = Field(default=False, description="Use SSL/TLS for LDAP connection")

    # Performance settings
    timeout: int = Field(default=30, description="Connection timeout in seconds", gt=0)
    page_size: int = Field(default=1000, description="Page size for paged results", gt=0)

    # Search filters
    user_filter: str = Field(
        default="(objectClass=inetOrgPerson)",
        description="LDAP filter for user entries",
    )
    group_filter: str = Field(
        default="(objectClass=groupOfNames)",
        description="LDAP filter for group entries",
    )


class CustomStreamConfig(DomainValueObject):
    """Configuration for custom LDAP streams using flext-core patterns."""

    name: str = Field(..., description="Stream name")
    search_filter: str = Field(..., description="LDAP search filter")
    primary_keys: list[str] | None = Field(default=None, description="Primary key fields")
    replication_key: str | None = Field(default=None, description="Replication key field")
    json_schema: dict[str, Any] | None = Field(default=None, description="JSON schema for the stream")


class LDIFProcessingConfig(DomainValueObject):
    """Configuration for LDIF file processing using flext-core patterns."""

    ldif_files: list[str] | None = Field(default=None, description="List of LDIF files to process")
    ldif_directory: str | None = Field(default=None, description="Directory containing LDIF files")
    ldif_file_pattern: str = Field(default="*.ldif", description="File pattern for LDIF files in directory")
    ldif_ignore_errors: bool = Field(default=True, description="Continue processing on LDIF parsing errors")
    ldif_max_errors: int = Field(default=100, description="Maximum number of parsing errors before stopping", gt=0)
    ldif_ignore_file_errors: bool = Field(default=True, description="Continue processing if a file fails completely")
    ldif_ignore_entry_errors: bool = Field(default=True, description="Continue processing if an entry fails")
    ldif_apply_transformations: bool = Field(default=False, description="Apply transformation rules to LDIF entries")
    ldif_transformation_rules: dict[str, Any] | None = Field(
        default=None,
        description="Transformation rules for LDIF processing",
    )
    migration_batch: str | None = Field(default=None, description="Migration batch identifier for tracking")
    enable_ldif_streams: bool = Field(default=False, description="Enable LDIF processing streams")


class TapLDAPConfig(BaseSettings):
    """Complete configuration for tap-ldap using flext-core patterns with environment support.

    Combines LDAP connection and LDIF processing configurations with Pydantic settings.
    """

    model_config = SettingsConfigDict(
        env_prefix="TAP_LDAP_",
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="allow",
        validate_assignment=True,
        str_strip_whitespace=True,
        use_enum_values=True,
    )

    # Core configurations as embedded value objects
    connection: LDAPConnectionConfig = Field(..., description="LDAP connection configuration")
    ldif_processing: LDIFProcessingConfig = Field(
        default_factory=LDIFProcessingConfig,
        description="LDIF processing configuration",
    )

    # Project identification
    project_name: str = Field(default="flext-tap-ldap", description="Project name")
    project_version: str = Field(default="0.7.0", description="Project version")

    # Custom streams
    custom_streams: list[dict[str, Any]] | None = Field(default=None, description="Custom stream definitions")

    @field_validator("custom_streams")
    @classmethod
    def validate_custom_streams(cls, v: list[dict[str, Any]] | None) -> list[dict[str, Any]] | None:
        """Validate custom stream configurations."""
        if v is not None:
            # Validate each custom stream config
            for stream_config in v:
                CustomStreamConfig(**stream_config)
        return v

    @classmethod
    def create_with_defaults(cls, **overrides: Any) -> TapLDAPConfig:
        """Create config with intelligent defaults."""
        defaults: dict[str, Any] = {
            "ldap_connection": {
                "host": "localhost",
                "port": 389,
                "bind_dn": None,
                "password": None,
                "use_ssl": False,
                "timeout": 30,
                "pool_size": 5,
                "validate_certificates": True,
                "ca_cert_file": None,
                "client_cert_file": None,
                "client_key_file": None,
                "ssh_tunnel": {},
                "oracle_oid_compatibility": False,
                "retry_attempts": 3,
                "connection_timeout": 10,
                "read_timeout": 60,
                "keep_alive": True,
                "auto_reconnect": True,
            },
            "ldif_processing": {
                "enabled": False,
                "file_path": None,
                "batch_size": 1000,
                "skip_errors": False,
                "encoding": "utf-8",
                "max_file_size_mb": 100,
                "validate_dn": True,
                "include_metadata": True,
                "parallel_processing": False,
                "chunk_size": 10000,
                "use_memory_mapping": False,
                "progress_callback": None,
            },
            "stream_maps": {},
            "stream_map_config": {},
            "batch_size": 1000,
            "streams": [],
        }

        # Apply overrides
        for key, value in overrides.items():
            if key in defaults:
                if isinstance(defaults[key], dict) and isinstance(value, dict):
                    defaults[key].update(value)
                else:
                    defaults[key] = value

        # Create the config properly
        return cls(
            connection=defaults["ldap_connection"],
            ldif_processing=defaults["ldif_processing"],
        )


# Export main configuration classes
__all__ = [
    "CustomStreamConfig",
    "LDAPConnectionConfig",
    "LDIFProcessingConfig",
    "TapLDAPConfig",
]
