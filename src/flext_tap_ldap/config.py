"""Configuration models for tap-ldap using consolidated patterns.

CONSOLIDATED: Uses flext-meltano common LDAP config to eliminate duplication
with flext-target-ldap.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextModels, FlextResult
from pydantic import Field, field_validator
from pydantic_settings import SettingsConfigDict

# Constants
MAX_PORT = 65535


class LDAPConnectionConfig(FlextModels.Config):
    """LDAP connection configuration using FlextModels pattern."""

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate LDAP connection configuration."""
        if not self.host:
            return FlextResult[None].fail("Host is required")
        if self.port <= 0 or self.port > MAX_PORT:
            return FlextResult[None].fail(f"Port must be between 1 and {MAX_PORT}")
        if self.timeout <= 0:
            return FlextResult[None].fail("Timeout must be positive")
        if self.page_size <= 0:
            return FlextResult[None].fail("Page size must be positive")
        return FlextResult[None].ok(None)

    host: str = Field(description="LDAP server host")
    port: int = Field(default=389, description="LDAP server port")
    use_ssl: bool = Field(default=False, description="Use SSL connection")
    use_tls: bool = Field(default=False, description="Use TLS connection")
    bind_dn: str | None = Field(default=None, description="Bind DN for authentication")
    bind_password: str | None = Field(default=None, description="Bind password")
    base_dn: str = Field(default="", description="Base DN for searches")
    timeout: int = Field(default=30, description="Connection timeout in seconds")
    page_size: int = Field(default=1000, description="LDAP search page size")
    max_retries: int = Field(default=3, description="Maximum connection retries")


class CustomStreamConfig(FlextModels.Config):
    """Configuration for custom LDAP streams using flext-core patterns."""

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate custom stream configuration."""
        if not self.name:
            return FlextResult[None].fail("Stream name is required")
        if not self.search_filter:
            return FlextResult[None].fail("Search filter is required")
        return FlextResult[None].ok(None)

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


class LDIFProcessingConfig(FlextModels.Config):
    """Configuration for LDIF file processing using flext-core patterns."""

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate LDIF processing configuration."""
        if self.ldif_max_errors <= 0:
            return FlextResult[None].fail("LDIF max errors must be positive")
        if self.ldif_files and self.ldif_directory:
            return FlextResult[None].fail(
                "Cannot specify both ldif_files and ldif_directory"
            )
        return FlextResult[None].ok(None)

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


class TapLDAPConfig(FlextModels.Config):
    """Complete configuration for tap-ldap using flext-core patterns.

    Combines LDAP connection and LDIF processing configurations with FlextConfig.BaseModel.
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
                    # Type-safe config construction
                    name = str(stream_config.get("name", ""))
                    search_filter = str(stream_config.get("search_filter", ""))
                    primary_keys = stream_config.get("primary_keys")
                    replication_key = stream_config.get("replication_key")
                    json_schema = stream_config.get("json_schema")

                    # Ensure proper types for primary_keys
                    if primary_keys is not None and not isinstance(primary_keys, list):
                        primary_keys = None

                    # Ensure proper types for replication_key
                    if replication_key is not None and not isinstance(
                        replication_key,
                        str,
                    ):
                        replication_key = None

                    # Ensure proper types for json_schema
                    if json_schema is not None and not isinstance(json_schema, dict):
                        json_schema = None

                    # Validate custom stream config (no need to create instance)
                    if not name or not search_filter:
                        cls._raise_invalid_stream_config()
                except (ValueError, TypeError) as e:
                    cls._raise_invalid_stream_config_with_error(e)
        return v

    @classmethod
    def create_with_defaults(cls, **overrides: object) -> TapLDAPConfig:
        """Create config with intelligent defaults."""
        # Use proper typed defaults for LDAPConnectionConfig
        ldap_defaults: dict[str, object] = {
            "host": "localhost",
            "port": 389,
            "bind_dn": None,
            "bind_password": None,
            "base_dn": "",
            "use_ssl": False,
            "use_tls": False,
            "timeout": 30,
            "page_size": 1000,
            "max_retries": 3,
        }

        # Use proper typed defaults for LDIFProcessingConfig
        ldif_defaults: dict[str, object] = {
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

        # Create properly typed config objects with explicit parameters
        ldap_connection = LDAPConnectionConfig(
            host=str(ldap_defaults["host"]),
            port=int(ldap_defaults["port"])
            if isinstance(ldap_defaults["port"], (int, str))
            else 389,
            bind_dn=ldap_defaults["bind_dn"]
            if isinstance(ldap_defaults["bind_dn"], str)
            else None,
            bind_password=ldap_defaults["bind_password"]
            if isinstance(ldap_defaults["bind_password"], str)
            else None,
            base_dn=str(ldap_defaults["base_dn"]),
            use_ssl=bool(ldap_defaults["use_ssl"]),
            use_tls=bool(ldap_defaults["use_tls"]),
            timeout=int(ldap_defaults["timeout"])
            if isinstance(ldap_defaults["timeout"], (int, str))
            else 30,
            page_size=int(ldap_defaults["page_size"])
            if isinstance(ldap_defaults["page_size"], (int, str))
            else 1000,
            max_retries=int(ldap_defaults["max_retries"])
            if isinstance(ldap_defaults["max_retries"], (int, str))
            else 3,
        )

        ldif_proc_config = LDIFProcessingConfig(
            ldif_files=ldif_defaults["ldif_files"]
            if isinstance(ldif_defaults["ldif_files"], list)
            else None,
            ldif_directory=ldif_defaults["ldif_directory"]
            if isinstance(ldif_defaults["ldif_directory"], str)
            else None,
            ldif_file_pattern=str(ldif_defaults["ldif_file_pattern"]),
            ldif_ignore_errors=bool(ldif_defaults["ldif_ignore_errors"]),
            ldif_max_errors=int(ldif_defaults["ldif_max_errors"])
            if isinstance(ldif_defaults["ldif_max_errors"], (int, str))
            else 100,
            ldif_ignore_file_errors=bool(ldif_defaults["ldif_ignore_file_errors"]),
            ldif_ignore_entry_errors=bool(ldif_defaults["ldif_ignore_entry_errors"]),
            ldif_apply_transformations=bool(
                ldif_defaults["ldif_apply_transformations"],
            ),
            ldif_transformation_rules=ldif_defaults["ldif_transformation_rules"]
            if isinstance(ldif_defaults["ldif_transformation_rules"], dict)
            else None,
            migration_batch=ldif_defaults["migration_batch"]
            if isinstance(ldif_defaults["migration_batch"], str)
            else None,
            enable_ldif_streams=bool(ldif_defaults["enable_ldif_streams"]),
        )

        return cls(
            connection=ldap_connection,
            ldif_processing=ldif_proc_config,
        )

    @classmethod
    def _raise_invalid_stream_config(cls) -> None:
        """Raise invalid stream config error."""
        raise ValueError(INVALID_STREAM_CONFIG_MSG)

    @classmethod
    def _raise_invalid_stream_config_with_error(cls, error: Exception) -> None:
        """Raise invalid stream config error with details."""
        raise ValueError(INVALID_STREAM_CONFIG_WITH_ERROR_MSG.format(error)) from error


# Constants for error messages
INVALID_STREAM_CONFIG_MSG = "Invalid custom stream config"
INVALID_STREAM_CONFIG_WITH_ERROR_MSG = "Invalid custom stream config: {}"

# Export main configuration classes
__all__: list[str] = [
    "CustomStreamConfig",
    "LDAPConnectionConfig",
    "LDIFProcessingConfig",
    "TapLDAPConfig",
]
