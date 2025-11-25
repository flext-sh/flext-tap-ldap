"""FLEXT Tap LDAP Configuration - Settings using flext-core patterns.

Provides LDAP tap configuration management extending FlextConfig
with Pydantic Settings for environment variable support and validation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import Self, TypedDict

from flext_core import FlextConfig, FlextConstants, FlextResult
from pydantic import Field, SecretStr, field_validator
from pydantic_settings import SettingsConfigDict

from flext_tap_ldap.typings import FlextMeltanoTapLdapTypes


class ConfigDefaults(TypedDict, total=False):
    """Type-safe configuration defaults."""

    ldap_host: str
    ldap_port: int
    ldap_use_ssl: bool
    ldap_use_tls: bool
    ldap_timeout: int
    ldap_page_size: int
    ldap_max_retries: int
    ldif_ignore_errors: bool
    ldif_max_errors: int


class FlextTapLdapConfig(FlextConfig):
    """FLEXT Tap LDAP Configuration extending FlextConfig.

    Single flat configuration class for FLEXT LDAP tap with enterprise features:
    - Extends FlextConfig from flext-core
    - Uses Pydantic 2 Settings with SecretStr for sensitive data
    - Enhanced singleton pattern with thread-safe access
    - Consolidates custom stream and LDIF processing configurations
    """

    class CustomStreamConfig(FlextConfig):
        """Nested configuration for custom LDAP streams."""

        name: str = Field(..., description="Stream name")
        search_filter: str = Field(..., description="LDAP search filter")
        primary_keys: FlextMeltanoTapLdapTypes.Core.StringList | None = Field(
            default=None,
            description="Primary key fields",
        )
        replication_key: str | None = Field(
            default=None,
            description="Replication key field",
        )
        json_schema: FlextMeltanoTapLdapTypes.Core.Dict | None = Field(
            default=None,
            description="JSON schema for the stream",
        )

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate business rules for custom streams."""
            if not self.name or not self.search_filter:
                return FlextResult[None].fail(
                    "Custom stream requires name and search_filter",
                )

            return FlextResult[None].ok(None)

    class LDIFProcessingConfig(FlextConfig):
        """Nested configuration for LDIF file processing."""

        ldif_files: FlextMeltanoTapLdapTypes.Core.StringList | None = Field(
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
        ldif_transformation_rules: FlextMeltanoTapLdapTypes.Core.Dict | None = Field(
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

        def validate_business_rules(self) -> FlextResult[None]:
            """Validate business rules for LDIF processing."""
            if self.ldif_files and self.ldif_directory:
                return FlextResult[None].fail(
                    "Cannot specify both ldif_files and ldif_directory",
                )

            if self.enable_ldif_streams and not (
                self.ldif_files or self.ldif_directory
            ):
                return FlextResult[None].fail(
                    "LDIF streams enabled but no files or directory specified",
                )

            return FlextResult[None].ok(None)

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
        default=None, description="Bind DN for authentication"
    )
    ldap_bind_password: SecretStr | None = Field(
        default=None, description="Bind password"
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
        """Get the global singleton instance using enhanced FlextConfig pattern."""
        return cls()

    @classmethod
    def create_for_development(cls, **overrides: object) -> Self:
        """Create development configuration instance."""
        dev_defaults: ConfigDefaults = {
            "ldap_host": "localhost",
            "ldap_port": 10389,
            "ldap_use_ssl": False,
            "ldap_use_tls": False,
            "ldap_timeout": 10,
            "ldap_page_size": 100,
            "ldif_ignore_errors": True,
            "ldif_max_errors": 10,
        }
        dev_defaults.update(overrides)  # type: ignore[typeddict-item]
        return cls(**dev_defaults)

    @classmethod
    def create_for_production(cls, **overrides: object) -> Self:
        """Create production configuration instance."""
        prod_defaults: ConfigDefaults = {
            "ldap_use_ssl": True,
            "ldap_timeout": 30,
            "ldap_page_size": 1000,
            "ldap_max_retries": 5,
            "ldif_ignore_errors": False,
            "ldif_max_errors": 0,
        }
        prod_defaults.update(overrides)  # type: ignore[typeddict-item]
        return cls(**prod_defaults)

    @classmethod
    def create_for_testing(cls, **overrides: object) -> Self:
        """Create testing configuration instance."""
        test_defaults: ConfigDefaults = {
            "ldap_host": "test-ldap",
            "ldap_port": 3389,
            "ldap_use_ssl": False,
            "ldap_timeout": 5,
            "ldap_page_size": 50,
            "ldif_ignore_errors": True,
            "ldif_max_errors": 1,
        }
        test_defaults.update(overrides)  # type: ignore[typeddict-item]
        return cls(**test_defaults)

    def validate_configuration(self) -> FlextResult[bool]:  # type: ignore[override]
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
                    "Cannot specify both ldif_files and ldif_directory"
                )

            if self.ldif_max_errors <= 0:
                return FlextResult[bool].fail("LDIF max errors must be positive")

            return FlextResult[bool].ok(True)
        except Exception as e:
            return FlextResult[bool].fail(f"Configuration validation error: {e}")


# Re-export nested classes at module level for backwards compatibility during transition
CustomStreamConfig = FlextTapLdapConfig.CustomStreamConfig
LDIFProcessingConfig = FlextTapLdapConfig.LDIFProcessingConfig

# Export all configuration classes
__all__ = [
    "CustomStreamConfig",
    "FlextTapLdapConfig",
    "LDIFProcessingConfig",
]
