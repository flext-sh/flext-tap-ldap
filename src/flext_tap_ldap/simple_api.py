"""Simple API for LDAP tap setup and operations using flext-core patterns.

# Constants
EXPECTED_DATA_COUNT = 3

MIGRATED TO FLEXT-CORE:
Provides enterprise-ready setup utilities with FlextResult pattern support.
"""

from __future__ import annotations

import os
from typing import Any

# Import from flext-core for foundational patterns (standardized)
from flext_core import (
    FlextResult,
)

from flext_tap_ldap.config import (
    LDAPConnectionConfig,
    LDIFProcessingConfig,
    TapLDAPConfig,
)


def setup_ldap_tap(config: TapLDAPConfig | None = None) -> FlextResult[Any]:
    """Setup LDAP tap with configuration.

    Args:
        config: Optional configuration. If None, creates defaults.

    Returns:
        FlextResult with TapLDAPConfig or error message.

    """
    try:
        if config is None:
            # Create with intelligent defaults
            config = TapLDAPConfig.create_with_defaults()

        # Validate configuration
        config.model_validate(config.model_dump())

        return FlextResult.ok(config)

    except (RuntimeError, ValueError, TypeError) as e:
        return FlextResult.fail(f"Failed to setup LDAP tap: {e}")


def create_ldap_connection_config(
    host: str,
    base_dn: str,
    port: int = 389,
    use_ssl: bool = False,
    bind_dn: str | None = None,
    bind_password: str | None = None,
) -> FlextResult[LDAPConnectionConfig]:
    """Create LDAP connection configuration.

    Args:
        host: LDAP server hostname
        base_dn: Base DN for searches
        port: LDAP server port (default 389)
        use_ssl: Use SSL connection (default False)
        bind_dn: Bind DN for authentication
        bind_password: Bind password

    Returns:
        FlextResult with LDAPConnectionConfig or error message.

    """
    try:
        config = LDAPConnectionConfig(
            host=host,
            base_dn=base_dn,
            port=port,
            use_ssl=use_ssl,
            bind_dn=bind_dn,
            bind_password=bind_password,
        )

        return FlextResult.ok(config)

    except (RuntimeError, ValueError, TypeError) as e:
        return FlextResult.fail(f"Failed to create LDAP connection config: {e}")


def create_ldif_processing_config(
    ldif_files: list[str] | None = None,
    ldif_directory: str | None = None,
    ldif_file_pattern: str = "*.ldif",
    ldif_ignore_errors: bool = True,
    ldif_max_errors: int = 100,
    ldif_ignore_file_errors: bool = True,
    ldif_ignore_entry_errors: bool = True,
    ldif_apply_transformations: bool = False,
    ldif_transformation_rules: dict[str, Any] | None = None,
    migration_batch: str | None = None,
    enable_ldif_streams: bool = False,
) -> FlextResult[LDIFProcessingConfig]:
    """Create LDIF processing configuration.

    Args:
        ldif_files: List of LDIF files to process
        ldif_directory: Directory containing LDIF files
        ldif_file_pattern: File pattern for LDIF files in directory
        ldif_ignore_errors: Continue processing on LDIF parsing errors
        ldif_max_errors: Maximum number of parsing errors before stopping
        ldif_ignore_file_errors: Continue processing if a file fails completely
        ldif_ignore_entry_errors: Continue processing if an entry fails
        ldif_apply_transformations: Apply transformation rules to LDIF entries
        ldif_transformation_rules: Transformation rules for LDIF processing
        migration_batch: Migration batch identifier for tracking
        enable_ldif_streams: Enable LDIF processing streams

    Returns:
        FlextResult with LDIFProcessingConfig or error message.

    """
    try:
        config = LDIFProcessingConfig(
            ldif_files=ldif_files,
            ldif_directory=ldif_directory,
            ldif_file_pattern=ldif_file_pattern,
            ldif_ignore_errors=ldif_ignore_errors,
            ldif_max_errors=ldif_max_errors,
            ldif_ignore_file_errors=ldif_ignore_file_errors,
            ldif_ignore_entry_errors=ldif_ignore_entry_errors,
            ldif_apply_transformations=ldif_apply_transformations,
            ldif_transformation_rules=ldif_transformation_rules,
            migration_batch=migration_batch,
            enable_ldif_streams=enable_ldif_streams,
        )
        return FlextResult.ok(config)

    except (RuntimeError, ValueError, TypeError) as e:
        return FlextResult.fail(f"Failed to create LDIF processing config: {e}")


def validate_ldap_config(config: TapLDAPConfig) -> FlextResult[Any]:
    """Validate LDAP tap configuration.

    Args:
        config: Configuration to validate

    Returns:
        FlextResult with validation success or error message.

    """
    try:
        # Validate using Pydantic model validation
        config.model_validate(config.model_dump())

        # Additional business rule validations
        if config.connection.port <= 0 or config.connection.port > 65535:
            return FlextResult.fail("Port must be between 1 and 65535")

        if not config.connection.base_dn:
            return FlextResult.fail("Base DN is required")

        if config.connection.use_ssl and config.connection.port == 389:
            return FlextResult.fail(
                "SSL enabled but port is 389 (consider using port 636 for LDAPS)",
            )

        return FlextResult.ok(True)

    except (RuntimeError, ValueError, TypeError) as e:
        return FlextResult.fail(f"Configuration validation failed: {e}")


def create_development_ldap_config(**overrides: Any) -> FlextResult[Any]:
    """Create development LDAP configuration with defaults.

    Args:
        **overrides: Configuration overrides

    Returns:
        FlextResult with TapLDAPConfig for development use.

    """
    try:
        connection_config = LDAPConnectionConfig(
            host="localhost",
            port=389,
            use_ssl=False,
            bind_dn="cn=REDACTED_LDAP_BIND_PASSWORD,dc=example,dc=com",
            bind_password=os.getenv(
                "LDAP_PASSWORD",
                "REDACTED_LDAP_BIND_PASSWORD",
            ),  # nosec B106 - Uses env var in production
            base_dn="dc=example,dc=com",
        )

        config = TapLDAPConfig(
            connection=connection_config,
            ldif_processing=LDIFProcessingConfig(enable_ldif_streams=False),
            project_name="flext-data.taps.flext-tap-ldap",
            project_version="0.9.0",
        )

        # Apply overrides
        if overrides:
            config_dict = config.model_dump()
            config_dict.update(overrides)
            config = TapLDAPConfig(**config_dict)

        return FlextResult.ok(config)

    except (RuntimeError, ValueError, TypeError) as e:
        return FlextResult.fail(f"Failed to create development config: {e}")


def create_production_ldap_config(**overrides: Any) -> FlextResult[Any]:
    """Create production LDAP configuration with security defaults.

    Args:
        **overrides: Configuration overrides

    Returns:
        FlextResult with TapLDAPConfig for production use.

    """
    try:
        connection_config = LDAPConnectionConfig(
            host="ldap.company.com",
            port=636,
            use_ssl=True,
            bind_dn="",  # Should be configured via environment
            bind_password="",  # Should be configured via environment
            base_dn="dc=company,dc=com",
        )

        config = TapLDAPConfig(
            connection=connection_config,
            ldif_processing=LDIFProcessingConfig(
                enable_ldif_streams=False,
                ldif_ignore_errors=False,
                ldif_max_errors=10,
            ),
            project_name="flext-data.taps.flext-tap-ldap",
            project_version="0.9.0",
        )

        # Apply overrides
        if overrides:
            config_dict = config.model_dump()
            config_dict.update(overrides)
            config = TapLDAPConfig(**config_dict)

        return FlextResult.ok(config)

    except (RuntimeError, ValueError, TypeError) as e:
        return FlextResult.fail(f"Failed to create production config: {e}")


def create_ldif_processing_config_advanced(
    ldif_directory: str | None = None,
    ldif_files: list[str] | None = None,
    **overrides: object,
) -> FlextResult[Any]:
    """Create LDIF processing configuration for migration scenarios.

    Args:
        ldif_directory: Directory containing LDIF files
        ldif_files: List of specific LDIF files
        **overrides: Additional configuration overrides

    Returns:
        FlextResult with TapLDAPConfig optimized for LDIF processing.

    """
    try:
        # Minimal connection config (not used for LDIF processing)
        connection_config = LDAPConnectionConfig(
            host="dummy",
            base_dn="dc=migration,dc=temp",
        )

        ldif_config = LDIFProcessingConfig(
            ldif_directory=ldif_directory,
            ldif_files=ldif_files,
            enable_ldif_streams=True,
            ldif_ignore_errors=True,
            ldif_ignore_file_errors=True,
            ldif_ignore_entry_errors=True,
            ldif_max_errors=1000,
            ldif_apply_transformations=False,
        )

        config = TapLDAPConfig(
            connection=connection_config,
            ldif_processing=ldif_config,
            project_name="flext-data.taps.flext-tap-ldap",
            project_version="0.9.0",
        )

        # Apply overrides
        if overrides:
            config_dict = config.model_dump()
            config_dict.update(overrides)
            config = TapLDAPConfig(**config_dict)

        return FlextResult.ok(config)

    except (RuntimeError, ValueError, TypeError) as e:
        return FlextResult.fail(f"Failed to create LDIF processing config: {e}")


# Export main API functions
__all__ = [
    "FlextResult",
    "create_development_ldap_config",
    "create_ldap_connection_config",
    "create_ldif_processing_config",
    "create_ldif_processing_config_advanced",
    "create_production_ldap_config",
    "setup_ldap_tap",
    "validate_ldap_config",
]
