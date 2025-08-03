"""Configuration models for tap-ldap using consolidated patterns.

CONSOLIDATED: Uses flext-meltano common LDAP config to eliminate duplication
with flext-target-ldap.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class LDAPConnectionConfig(BaseModel):
    """LDAP connection configuration."""

    host: str = Field(description="LDAP server host")
    port: int = Field(default=389, description="LDAP server port")
    use_ssl: bool = Field(default=False, description="Use SSL connection")
    bind_dn: str | None = Field(default=None, description="Bind DN for authentication")
    bind_password: str | None = Field(default=None, description="Bind password")
    base_dn: str = Field(description="Base DN for searches")


class CustomStreamConfig(BaseModel):
    """Configuration for custom LDAP streams using flext-core patterns."""

    name: str = Field(..., description="Stream name")
    search_filter: str = Field(..., description="LDAP search filter")
    primary_keys: list[str] | None = Field(
        default=None,
        description="Primary key fields",
    )
    replication_key: str | None = Field(
        default=None,
        description="Replication key field",
    )
    json_schema: dict[str, object] | None = Field(
        default=None,
        description="JSON schema for the stream",
    )


class LDIFProcessingConfig(BaseModel):
    """Configuration for LDIF file processing using flext-core patterns."""

    ldif_files: list[str] | None = Field(
        default=None,
        description="List of LDIF files to process",
    )
    ldif_directory: str | None = Field(
        default=None,
        description="Directory containing LDIF files",
    )
    ldif_file_pattern: str = Field(
        default="*.ldif",
        description="File pattern for LDIF files in directory",
    )
    ldif_ignore_errors: bool = Field(
        default=True,
        description="Continue processing on LDIF parsing errors",
    )
    ldif_max_errors: int = Field(
        default=100,
        description="Maximum number of parsing errors before stopping",
        gt=0,
    )
    ldif_ignore_file_errors: bool = Field(
        default=True,
        description="Continue processing if a file fails completely",
    )
    ldif_ignore_entry_errors: bool = Field(
        default=True,
        description="Continue processing if an entry fails",
    )
    ldif_apply_transformations: bool = Field(
        default=False,
        description="Apply transformation rules to LDIF entries",
    )
    ldif_transformation_rules: dict[str, object] | None = Field(
        default=None,
        description="Transformation rules for LDIF processing",
    )
    migration_batch: str | None = Field(
        default=None,
        description="Migration batch identifier for tracking",
    )
    enable_ldif_streams: bool = Field(
        default=False,
        description="Enable LDIF processing streams",
    )


class TapLDAPConfig(BaseSettings):
    """Complete configuration for tap-ldap using flext-core patterns.

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
    connection: LDAPConnectionConfig = Field(
        ...,
        description="LDAP connection configuration",
    )
    ldif_processing: LDIFProcessingConfig = Field(
        default_factory=LDIFProcessingConfig,
        description="LDIF processing configuration",
    )

    # Project identification
    project_name: str = Field(
        default="flext-data.taps.flext-tap-ldap",
        description="Project name",
    )
    project_version: str = Field(default="0.9.0", description="Project version")

    # Custom streams
    custom_streams: list[dict[str, object]] | None = Field(
        default=None,
        description="Custom stream definitions",
    )

    @field_validator("custom_streams")
    @classmethod
    def validate_custom_streams(
        cls,
        v: list[dict[str, object]] | None,
    ) -> list[dict[str, object]] | None:
        """Validate custom stream configurations."""
        if v is not None:
            # Validate each custom stream config with proper type conversion
            for stream_config in v:
                try:
                    # Convert dict[str, object] to proper types for validation
                    config_data = {
                        "name": str(stream_config.get("name", "")),
                        "search_filter": str(stream_config.get("search_filter", "")),
                        "primary_keys": stream_config.get("primary_keys"),
                        "replication_key": stream_config.get("replication_key"),
                        "json_schema": stream_config.get("json_schema"),
                    }
                    CustomStreamConfig(**config_data)  # type: ignore[arg-type]
                except (ValueError, TypeError) as e:
                    msg = f"Invalid custom stream config: {e}"
                    raise ValueError(msg) from e
        return v

    @classmethod
    def create_with_defaults(cls, **overrides: Any) -> TapLDAPConfig:
        """Create config with intelligent defaults."""
        # Use proper typed defaults for LDAPConnectionConfig
        ldap_defaults: dict[str, Any] = {
            "host": "localhost",
            "port": 389,
            "bind_dn": None,
            "bind_password": None,
            "base_dn": "",
            "use_ssl": False,
            "use_tls": False,
            "timeout_seconds": 30,
            "page_size": 1000,
            "max_retries": 3,
        }

        # Use proper typed defaults for LDIFProcessingConfig
        ldif_defaults: dict[str, Any] = {
            "ldif_files": None,
            "ldif_directory": None,
            "ldif_file_pattern": "*.ldif",
            "ldif_ignore_errors": True,
            "ldif_max_errors": 100,
            "ldif_ignore_file_errors": True,
            "ldif_ignore_entry_errors": True,
            "ldif_apply_transformations": False,
            "ldif_transformation_rules": None,
            "migration_batch": None,
            "enable_ldif_streams": False,
        }

        # Apply overrides to connection config
        if "connection" in overrides and isinstance(overrides["connection"], dict):
            ldap_defaults.update(overrides["connection"])

        # Apply overrides to LDIF config
        if "ldif_processing" in overrides and isinstance(
            overrides["ldif_processing"],
            dict,
        ):
            ldif_defaults.update(overrides["ldif_processing"])

        # Create properly typed config objects
        return cls(
            connection=LDAPConnectionConfig(**ldap_defaults),
            ldif_processing=LDIFProcessingConfig(**ldif_defaults),
        )


# Export main configuration classes
__all__ = [
    "CustomStreamConfig",
    "LDAPConnectionConfig",
    "LDIFProcessingConfig",
    "TapLDAPConfig",
]
