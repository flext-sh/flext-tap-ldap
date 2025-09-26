"""FLEXT Tap LDAP Configuration - Settings using flext-core patterns.

Provides LDAP tap configuration management extending FlextConfig
with Pydantic Settings for environment variable support and validation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import threading
from typing import ClassVar

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import SettingsConfigDict

from flext_core import FlextConfig, FlextConstants, FlextResult


class FlextTapLdapConfig(FlextConfig):
    """FLEXT Tap LDAP Configuration extending FlextConfig.

    Single flat configuration class for FLEXT LDAP tap following [Project]Config pattern:
    - Extends FlextConfig from flext-core
    - Uses Pydantic 2 Settings with SecretStr for sensitive data
    - Singleton pattern with thread-safe access
    - Flat structure without nested configuration classes
    """

    # Singleton pattern attributes
    _global_instance: ClassVar[FlextTapLdapConfig | None] = None
    _lock: ClassVar[threading.Lock] = threading.Lock()

    model_config = SettingsConfigDict(
        env_prefix=FLEXT_TAP_LDAP_,
        case_sensitive=False,
        extra=ignore,
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter=__,
        use_enum_values=True,
        validate_assignment=True,
        validate_default=True,
        frozen=False,
        str_strip_whitespace=True,
    )

    # LDAP Connection Configuration - flat structure
    ldap_host: str = Field(description="LDAP server host")
    ldap_port: int = Field(default=389, description="LDAP server port")
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

    @field_validator("ldap_host")
    @classmethod
    def validate_ldap_host(cls, v: str) -> str:
        """Validate LDAP host is not empty."""
        if not v or not v.strip():
            msg = "LDAP host is required"
            raise ValueError(msg)
        return v.strip()

    @field_validator("ldap_port")
    @classmethod
    def validate_ldap_port(cls, v: int) -> int:
        """Validate LDAP port is in valid range."""
        if v <= 0 or v > FlextConstants.Network.MAX_PORT:
            msg = f"LDAP port must be between 1 and {FlextConstants.Network.MAX_PORT}"
            raise ValueError(msg)
        return v

    # Singleton pattern override for proper typing
    @classmethod
    def get_global_instance(cls) -> FlextTapLdapConfig:
        """Get the global singleton instance of FlextTapLdapConfig."""
        if cls._global_instance is None:
            with cls._lock:
                if cls._global_instance is None:
                    cls._global_instance = cls()
        return cls._global_instance

    @classmethod
    def reset_global_instance(cls) -> None:
        """Reset the global FlextTapLdapConfig instance (mainly for testing)."""
        cls._global_instance = None

    def validate_configuration(self) -> FlextResult[None]:
        """Validate the complete LDAP tap configuration."""
        try:
            # Validate LDAP connection settings
            if not self.ldap_host:
                return FlextResult[None].fail("LDAP host is required")

            if self.ldap_port <= 0:
                return FlextResult[None].fail("LDAP port must be positive")

            if self.ldap_timeout <= 0:
                return FlextResult[None].fail("LDAP timeout must be positive")

            if self.ldap_page_size <= 0:
                return FlextResult[None].fail("LDAP page size must be positive")

            # Validate LDIF processing settings
            if self.ldif_files and self.ldif_directory:
                return FlextResult[None].fail(
                    "Cannot specify both ldif_files and ldif_directory"
                )

            if self.ldif_max_errors <= 0:
                return FlextResult[None].fail("LDIF max errors must be positive")

            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Configuration validation error: {e}")


# Legacy compatibility aliases
TapLDAPConfig = FlextTapLdapConfig
LDAPConnectionConfig = FlextTapLdapConfig  # Legacy alias

# Export main configuration class
__all__ = [
    "FlextTapLdapConfig",
    "TapLDAPConfig",  # Legacy compatibility
]
