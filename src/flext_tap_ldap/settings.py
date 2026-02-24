"""FLEXT Tap LDAP Configuration - Settings using flext-core patterns.

Provides LDAP tap configuration management extending FlextSettings
with Pydantic Settings for environment variable support and validation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import Self

from flext_core import FlextConstants, FlextResult, FlextSettings
from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator
from pydantic_settings import SettingsConfigDict

from flext_tap_ldap.typings import t


class ConfigDefaults(BaseModel):
    """Type-safe configuration defaults."""

    model_config = ConfigDict(frozen=False, extra="forbid")

    ldap_host: str | None = Field(default=None)
    ldap_port: int | None = Field(default=None)
    ldap_use_ssl: bool | None = Field(default=None)
    ldap_use_tls: bool | None = Field(default=None)
    ldap_timeout: int | None = Field(default=None)
    ldap_page_size: int | None = Field(default=None)
    ldap_max_retries: int | None = Field(default=None)
    ldif_ignore_errors: bool | None = Field(default=None)
    ldif_max_errors: int | None = Field(default=None)


class FlextTapLdapSettings(FlextSettings):
    """FLEXT Tap LDAP Configuration extending FlextSettings.

    Single flat configuration class for FLEXT LDAP tap with enterprise features:
    - Extends FlextSettings from flext-core
    - Uses Pydantic 2 Settings with SecretStr for sensitive data
    - Enhanced singleton pattern with thread-safe access
    - Consolidates custom stream and LDIF processing configurations
    """

    class CustomStreamConfig(FlextSettings):
        """Nested configuration for custom LDAP streams."""

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
        json_schema: dict[str, t.JsonValue] | None = Field(
            default=None,
            description="JSON schema for the stream",
        )

        def validate_business_rules(self) -> FlextResult[bool]:
            """Validate business rules for custom streams."""
            if not self.name or not self.search_filter:
                return FlextResult[bool].fail(
                    "Custom stream requires name and search_filter",
                )

            return FlextResult[bool].ok(value=True)

    class LDIFProcessingConfig(FlextSettings):
        """Nested configuration for LDIF file processing."""

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
            default=FlextConstants.Performance.BatchProcessing.DEFAULT_SIZE // 10,
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
        ldif_transformation_rules: dict[str, t.JsonValue] | None = Field(
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

        def validate_business_rules(self) -> FlextResult[bool]:
            """Validate business rules for LDIF processing."""
            if self.ldif_files and self.ldif_directory:
                return FlextResult[bool].fail(
                    "Cannot specify both ldif_files and ldif_directory",
                )

            if self.enable_ldif_streams and not (
                self.ldif_files or self.ldif_directory
            ):
                return FlextResult[bool].fail(
                    "LDIF streams enabled but no files or directory specified",
                )

            return FlextResult[bool].ok(value=True)

    model_config = SettingsConfigDict(
        env_prefix="FLEXT_TAP_LDAP_",
        case_sensitive=False,
        extra="ignore",
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        use_enum_values=True,
        validate_assignment=True,
        validate_default=True,
        frozen=False,
        str_strip_whitespace=True,
    )

    # LDAP Connection Configuration - flat structure
    ldap_host: str = Field(min_length=1, description="LDAP server host")
    ldap_port: int = Field(
        default=389,
        description="LDAP server port",
    )
    ldap_use_ssl: bool = Field(default=False, description="Use SSL connection")
    ldap_use_tls: bool = Field(default=False, description="Use TLS connection")
    ldap_bind_dn: str | None = Field(
        default=None,
        description="Bind DN for authentication",
    )
    ldap_bind_password: SecretStr | None = Field(
        default=None,
        description="Bind password",
    )
    ldap_base_dn: str = Field(default="", description="Base DN for searches")
    ldap_timeout: int = Field(
        default=FlextConstants.Network.DEFAULT_TIMEOUT,
        description="Connection timeout in seconds",
    )
    ldap_page_size: int = Field(
        default=FlextConstants.Defaults.PAGE_SIZE * 10,
        description="LDAP search page size",
    )
    ldap_max_retries: int = Field(
        default=FlextConstants.Reliability.MAX_RETRY_ATTEMPTS,
        description="Maximum connection retries",
    )

    # LDIF Processing Configuration - flat structure
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
        default=FlextConstants.Performance.BatchProcessing.DEFAULT_SIZE,
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
    ldif_transformation_rules: dict[str, str] | None = Field(
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

    # Custom Streams Configuration - flat structure
    custom_streams: list[dict[str, str]] | None = Field(
        default=None,
        description="Custom stream definitions",
    )

    # Validation methods
    @field_validator("custom_streams")
    @classmethod
    def validate_custom_streams(
        cls,
        v: list[dict[str, str]] | None,
    ) -> list[dict[str, str]] | None:
        """Validate custom stream configurations."""
        if v is not None:
            for stream_config in v:
                name = stream_config.get("name", "")
                search_filter = stream_config.get("search_filter", "")
                if not name or not search_filter:
                    msg = "Custom stream must have 'name' and 'search_filter'"
                    raise ValueError(msg)
        return v

    @field_validator("ldap_port")
    @classmethod
    def validate_ldap_port(cls, v: int) -> int:
        """Validate LDAP port is in valid range."""
        if v <= 0 or v > FlextConstants.Network.MAX_PORT:
            msg = f"LDAP port must be between 1 and {FlextConstants.Network.MAX_PORT}"
            raise ValueError(msg)
        return v

    # Enhanced singleton pattern methods
    @classmethod
    def get_global_instance(cls) -> Self:
        """Get the global singleton instance using enhanced FlextSettings pattern."""
        return cls()

    @classmethod
    def create_for_development(cls, **overrides: t.JsonValue) -> Self:
        """Create development configuration instance."""
        dev_defaults: dict[str, t.JsonValue] = {
            "ldap_host": "localhost",
            "ldap_port": 10389,
            "ldap_use_ssl": False,
            "ldap_use_tls": False,
            "ldap_timeout": 10,
            "ldap_page_size": 100,
            "ldif_ignore_errors": True,
            "ldif_max_errors": 10,
        }
        dev_defaults.update(overrides)
        return cls(**dev_defaults)

    @classmethod
    def create_for_production(cls, **overrides: t.JsonValue) -> Self:
        """Create production configuration instance."""
        prod_defaults: dict[str, t.JsonValue] = {
            "ldap_use_ssl": True,
            "ldap_timeout": 30,
            "ldap_page_size": 1000,
            "ldap_max_retries": 5,
            "ldif_ignore_errors": False,
            "ldif_max_errors": 0,
        }
        prod_defaults.update(overrides)
        return cls(**prod_defaults)

    @classmethod
    def create_for_testing(cls, **overrides: t.JsonValue) -> Self:
        """Create testing configuration instance."""
        test_defaults: dict[str, t.JsonValue] = {
            "ldap_host": "test-ldap",
            "ldap_port": 3389,
            "ldap_use_ssl": False,
            "ldap_timeout": 5,
            "ldap_page_size": 50,
            "ldif_ignore_errors": True,
            "ldif_max_errors": 1,
        }
        test_defaults.update(overrides)
        return cls(**test_defaults)

    def validate_tap_configuration(self) -> FlextResult[bool]:
        """Validate the complete LDAP tap configuration."""
        try:
            # Validate LDAP connection settings
            if not self.ldap_host:
                return FlextResult[bool].fail("LDAP host is required")

            if self.ldap_port <= 0:
                return FlextResult[bool].fail("LDAP port must be positive")

            if self.ldap_timeout <= 0:
                return FlextResult[bool].fail("LDAP timeout must be positive")

            if self.ldap_page_size <= 0:
                return FlextResult[bool].fail("LDAP page size must be positive")

            # Validate LDIF processing settings
            if self.ldif_files and self.ldif_directory:
                return FlextResult[bool].fail(
                    "Cannot specify both ldif_files and ldif_directory",
                )

            if self.ldif_max_errors <= 0:
                return FlextResult[bool].fail("LDIF max errors must be positive")

            return FlextResult[bool].ok(value=True)
        except Exception as e:
            return FlextResult[bool].fail(f"Configuration validation error: {e}")


# Re-export nested classes at module level with real inheritance for backwards compatibility
class CustomStreamConfig(FlextTapLdapSettings.CustomStreamConfig):
    """CustomStreamConfig - real inheritance from FlextTapLdapSettings.CustomStreamConfig."""


class LDIFProcessingConfig(FlextTapLdapSettings.LDIFProcessingConfig):
    """LDIFProcessingConfig - real inheritance from FlextTapLdapSettings.LDIFProcessingConfig."""


# Export all configuration classes
__all__ = [
    "CustomStreamConfig",
    "FlextTapLdapSettings",
    "LDIFProcessingConfig",
]
