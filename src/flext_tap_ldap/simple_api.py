"""Simple API for LDAP tap setup and operations using flext-core patterns.

MIGRATED TO FLEXT-CORE:
Provides enterprise-ready setup utilities with ServiceResult pattern support.
"""

from __future__ import annotations

from typing import Any

# Use centralized ServiceResult from flext-core - ELIMINATE DUPLICATION
from flext_core.domain.types import ServiceResult
from flext_tap_ldap.config import LDAPConnectionConfig
from flext_tap_ldap.config import LDIFProcessingConfig
from flext_tap_ldap.config import TapLDAPConfig


def setup_ldap_tap(config: TapLDAPConfig | None = None) -> ServiceResult[TapLDAPConfig]:
    """Setup LDAP tap with configuration.

    Args:
        config: Optional configuration. If None, creates defaults.

    Returns:
        ServiceResult with TapLDAPConfig or error message.

    """
    try:
        if config is None:
            # Create with intelligent defaults
            config = TapLDAPConfig.create_with_defaults()

        # Validate configuration
        config.model_validate(config.model_dump())

        return ServiceResult.ok(config)

    except Exception as e:
        return ServiceResult.fail(f"Failed to setup LDAP tap: {e}")


def create_ldap_connection_config(
    host: str,
    base_dn: str,
    port: int = 389,
    **kwargs: Any,
) -> ServiceResult[LDAPConnectionConfig]:
    """Create LDAP connection configuration.

    Args:
        host: LDAP server hostname
        base_dn: Base DN for searches
        port: LDAP server port (default 389)
        **kwargs: Additional configuration parameters

    Returns:
        ServiceResult with LDAPConnectionConfig or error message.

    """
    try:
        config = LDAPConnectionConfig(
            host=host,
            base_dn=base_dn,
            port=port,
            **kwargs,
        )

        return ServiceResult.ok(config)

    except Exception as e:
        return ServiceResult.fail(f"Failed to create LDAP connection config: {e}")


def create_ldif_processing_config(**kwargs: Any) -> ServiceResult[LDIFProcessingConfig]:
    """Create LDIF processing configuration.

    Args:
        **kwargs: LDIF processing parameters

    Returns:
        ServiceResult with LDIFProcessingConfig or error message.

    """
    try:
        config = LDIFProcessingConfig(**kwargs)
        return ServiceResult.ok(config)

    except Exception as e:
        return ServiceResult.fail(f"Failed to create LDIF processing config: {e}")


def validate_ldap_config(config: TapLDAPConfig) -> ServiceResult[bool]:
    """Validate LDAP tap configuration.

    Args:
        config: Configuration to validate

    Returns:
        ServiceResult with validation success or error message.

    """
    try:
        # Validate using Pydantic model validation
        config.model_validate(config.model_dump())

        # Additional business rule validations
        if config.connection.port <= 0 or config.connection.port > 65535:
            return ServiceResult.fail("Port must be between 1 and 65535")

        if not config.connection.base_dn:
            return ServiceResult.fail("Base DN is required")

        if config.connection.use_ssl and config.connection.port == 389:
            return ServiceResult.fail(
                "SSL enabled but port is 389 (consider using port 636 for LDAPS)",
            )

        return ServiceResult.ok(True)

    except Exception as e:
        return ServiceResult.fail(f"Configuration validation failed: {e}")


def create_development_ldap_config(**overrides: Any) -> ServiceResult[TapLDAPConfig]:
    """Create development LDAP configuration with defaults.

    Args:
        **overrides: Configuration overrides

    Returns:
        ServiceResult with TapLDAPConfig for development use.

    """
    try:
        connection_config = LDAPConnectionConfig(
            host="localhost",
            port=389,
            base_dn="dc=example,dc=com",
            bind_dn="cn=REDACTED_LDAP_BIND_PASSWORD,dc=example,dc=com",
            password="REDACTED_LDAP_BIND_PASSWORD",
            use_ssl=False,
            timeout=30,
            page_size=100,
            user_filter="(objectClass=person)",
            group_filter="(objectClass=groupOfNames)",
        )

        config = TapLDAPConfig(
            connection=connection_config,
            ldif_processing=LDIFProcessingConfig(enable_ldif_streams=False),
            project_name="flext-tap-ldap",
            project_version="0.7.0",
        )

        # Apply overrides
        if overrides:
            config_dict = config.model_dump()
            config_dict.update(overrides)
            config = TapLDAPConfig(**config_dict)

        return ServiceResult.ok(config)

    except Exception as e:
        return ServiceResult.fail(f"Failed to create development config: {e}")


def create_production_ldap_config(**overrides: Any) -> ServiceResult[TapLDAPConfig]:
    """Create production LDAP configuration with security defaults.

    Args:
        **overrides: Configuration overrides

    Returns:
        ServiceResult with TapLDAPConfig for production use.

    """
    try:
        connection_config = LDAPConnectionConfig(
            host="ldap.company.com",
            port=636,
            base_dn="dc=company,dc=com",
            use_ssl=True,
            timeout=60,
            page_size=1000,
            user_filter="(objectClass=inetOrgPerson)",
            group_filter="(objectClass=groupOfNames)",
        )

        config = TapLDAPConfig(
            connection=connection_config,
            ldif_processing=LDIFProcessingConfig(
                enable_ldif_streams=False,
                ldif_ignore_errors=False,
                ldif_max_errors=10,
            ),
            project_name="flext-tap-ldap",
            project_version="0.7.0",
        )

        # Apply overrides
        if overrides:
            config_dict = config.model_dump()
            config_dict.update(overrides)
            config = TapLDAPConfig(**config_dict)

        return ServiceResult.ok(config)

    except Exception as e:
        return ServiceResult.fail(f"Failed to create production config: {e}")


def create_ldif_processing_config_advanced(
    ldif_directory: str | None = None,
    ldif_files: list[str] | None = None,
    **overrides: Any,
) -> ServiceResult[TapLDAPConfig]:
    """Create LDIF processing configuration for migration scenarios.

    Args:
        ldif_directory: Directory containing LDIF files
        ldif_files: List of specific LDIF files
        **overrides: Additional configuration overrides

    Returns:
        ServiceResult with TapLDAPConfig optimized for LDIF processing.

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
            project_name="flext-tap-ldap",
            project_version="0.7.0",
        )

        # Apply overrides
        if overrides:
            config_dict = config.model_dump()
            config_dict.update(overrides)
            config = TapLDAPConfig(**config_dict)

        return ServiceResult.ok(config)

    except Exception as e:
        return ServiceResult.fail(f"Failed to create LDIF processing config: {e}")


# Export main API functions
__all__ = [
    "ServiceResult",
    "create_development_ldap_config",
    "create_ldap_connection_config",
    "create_ldif_processing_config",
    "create_ldif_processing_config_advanced",
    "create_production_ldap_config",
    "setup_ldap_tap",
    "validate_ldap_config",
]
