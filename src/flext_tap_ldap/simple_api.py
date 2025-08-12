"""Simple API for LDAP tap setup and operations using flext-core patterns.

# Constants
EXPECTED_DATA_COUNT = 3

MIGRATED TO FLEXT-CORE:
Provides enterprise-ready setup utilities with FlextResult pattern support.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

from flext_core import (
    FlextResult,
)

from flext_tap_ldap.config import (
    LDAPConnectionConfig,
    LDIFProcessingConfig,
    TapLDAPConfig,
)


def _coerce_str_optional(value: object) -> str | None:
    """Coerce value to optional string using pattern matching."""
    match value:
        case str() as str_val if str_val:
            return str_val
        case _:
            return None


def _coerce_bool(value: object, *, default: bool = False) -> bool:
    """Coerce arbitrary value to bool with sensible defaults."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "1", "yes", "y", "on"}:
            return True
        if lowered in {"false", "0", "no", "n", "off"}:
            return False
    if isinstance(value, (int, float)):
        return bool(value)
    return default


def _coerce_int(value: object, default: int) -> int:
    """Coerce arbitrary value to int, or return default on failure."""
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        try:
            return int(value.strip())
        except ValueError:
            return default
    return default


@dataclass
class LDAPConnectionParams:
    """Parameter object for LDAP connection configuration.

    Implements Parameter Object Pattern to reduce argument count
    and improve maintainability following SOLID principles.
    """

    host: str
    base_dn: str
    port: int = 389
    use_ssl: bool = False
    bind_dn: str | None = None
    bind_password: str | None = None


@dataclass
class LDIFConfigBuilder:
    """Builder for LDIF processing configuration.

    Implements Builder Pattern to eliminate parameter proliferation
    following Interface Segregation Principle.
    """

    ldif_files: list[str] = field(default_factory=list)
    ldif_directory: str | None = None
    ldif_file_pattern: str = "*.ldif"
    ldif_ignore_errors: bool = True
    ldif_max_errors: int = 100
    ldif_ignore_file_errors: bool = True
    ldif_ignore_entry_errors: bool = True
    ldif_apply_transformations: bool = False
    ldif_transformation_rules: dict[str, object] = field(default_factory=dict)
    migration_batch: str | None = None
    enable_ldif_streams: bool = False

    def with_files(self, files: list[str]) -> LDIFConfigBuilder:
        """Set LDIF files to process."""
        self.ldif_files = files
        return self

    def with_directory(self, directory: str) -> LDIFConfigBuilder:
        """Set LDIF directory to scan."""
        self.ldif_directory = directory
        return self

    def with_pattern(self, pattern: str) -> LDIFConfigBuilder:
        """Set file pattern for scanning."""
        self.ldif_file_pattern = pattern
        return self

    def with_error_handling(
        self,
        *,
        ignore_errors: bool = True,
        max_errors: int = 100,
    ) -> LDIFConfigBuilder:
        """Configure error handling behavior."""
        self.ldif_ignore_errors = ignore_errors
        self.ldif_max_errors = max_errors
        return self

    def with_transformations(
        self,
        *,
        enable: bool = True,
        rules: dict[str, object] | None = None,
    ) -> LDIFConfigBuilder:
        """Configure transformation settings."""
        self.ldif_apply_transformations = enable
        if rules:
            self.ldif_transformation_rules = rules
        return self

    def with_migration_batch(self, batch_name: str) -> LDIFConfigBuilder:
        """Set migration batch identifier."""
        self.migration_batch = batch_name
        return self

    def build(self) -> FlextResult[LDIFProcessingConfig]:
        """Build the LDIF processing configuration."""
        try:
            return FlextResult.ok(
                LDIFProcessingConfig(
                    ldif_files=self.ldif_files,
                    ldif_directory=self.ldif_directory,
                    ldif_file_pattern=self.ldif_file_pattern,
                    ldif_ignore_errors=self.ldif_ignore_errors,
                    ldif_max_errors=self.ldif_max_errors,
                    ldif_ignore_file_errors=self.ldif_ignore_file_errors,
                    ldif_ignore_entry_errors=self.ldif_ignore_entry_errors,
                    ldif_apply_transformations=self.ldif_apply_transformations,
                    ldif_transformation_rules=self.ldif_transformation_rules,
                    migration_batch=self.migration_batch,
                    enable_ldif_streams=self.enable_ldif_streams,
                ),
            )
        except (RuntimeError, ValueError, TypeError) as e:
            return FlextResult.fail(f"Failed to build LDIF processing config: {e}")


def setup_ldap_tap(config: TapLDAPConfig | None = None) -> FlextResult[TapLDAPConfig]:
    """Set up the LDAP tap with configuration.

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
    params: LDAPConnectionParams,
) -> FlextResult[LDAPConnectionConfig]:
    """Create LDAP connection configuration using Parameter Object Pattern.

    Args:
        params: LDAP connection parameters object

    Returns:
        FlextResult with LDAPConnectionConfig or error message.

    """
    try:
        config = LDAPConnectionConfig(
            host=params.host,
            base_dn=params.base_dn,
            port=params.port,
            use_ssl=params.use_ssl,
            bind_dn=params.bind_dn,
            bind_password=params.bind_password,
        )

        return FlextResult.ok(config)

    except (RuntimeError, ValueError, TypeError) as e:
        return FlextResult.fail(f"Failed to create LDAP connection config: {e}")


def create_ldap_connection_config_legacy(
    host: str,
    base_dn: str,
    port: int = 389,
    **kwargs: object,
) -> FlextResult[LDAPConnectionConfig]:
    """Create LDAP connection configuration (legacy interface).

    Backward compatibility wrapper for the Parameter Object Pattern implementation.
    Use create_ldap_connection_config() with LDAPConnectionParams for new code.
    """
    try:
        params = LDAPConnectionParams(
            host=host,
            base_dn=base_dn,
            port=port,
            use_ssl=bool(kwargs.get("use_ssl")),
            bind_dn=_coerce_str_optional(kwargs.get("bind_dn")),
            bind_password=_coerce_str_optional(kwargs.get("bind_password")),
        )
        return create_ldap_connection_config(params)
    except Exception as e:
        return FlextResult.fail(f"Failed to create legacy connection config: {e}")


def create_ldif_processing_config(
    ldif_files: list[str] | None = None,
    ldif_directory: str | None = None,
    **kwargs: object,
) -> FlextResult[LDIFProcessingConfig]:
    """Create LDIF processing configuration.

    REFACTORED: Now uses Builder Pattern internally to eliminate parameter proliferation.
    Maintains backward compatibility while providing cleaner internal implementation.

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

    Keyword Args:
        **kwargs: Optional keyword-only parameters, including:
            - ldif_file_pattern: Pattern for LDIF files (default: "*.ldif").
            - ldif_ignore_errors: Continue on parsing errors (default: True).
            - ldif_max_errors: Max errors before stopping (default: 100).
            - ldif_ignore_file_errors: Continue if a file fails (default: True).
            - ldif_ignore_entry_errors: Continue if an entry fails (default: True).
            - ldif_apply_transformations: Apply transformation rules (default: False).
            - ldif_transformation_rules: Dict of transformation rules.
            - migration_batch: Identifier for batch processing.
            - enable_ldif_streams: Enable LDIF streams (default: False).

    """
    # Use Builder Pattern to construct configuration
    builder = LDIFConfigBuilder()

    # Files and directory
    if ldif_files:
        builder.with_files(ldif_files)
    if ldif_directory:
        builder.with_directory(ldif_directory)

    # Simple field normalization (no branching besides None checks)
    builder.with_pattern(str(kwargs.get("ldif_file_pattern", "*.ldif")))

    ignore_errors = _coerce_bool(kwargs.get("ldif_ignore_errors", True), default=True)
    max_errors = _coerce_int(kwargs.get("ldif_max_errors", 100), 100)
    builder.with_error_handling(ignore_errors=ignore_errors, max_errors=max_errors)

    apply_transformations = _coerce_bool(
        kwargs.get("ldif_apply_transformations", False), default=False,
    )
    rules = kwargs.get("ldif_transformation_rules")
    rules_dict = rules if isinstance(rules, dict) else None
    builder.with_transformations(enable=apply_transformations, rules=rules_dict)

    batch = _coerce_str_optional(kwargs.get("migration_batch"))
    if batch:
        builder.with_migration_batch(batch)

    # Direct attribute settings
    builder.ldif_ignore_file_errors = _coerce_bool(
        kwargs.get("ldif_ignore_file_errors", True), default=True,
    )
    builder.ldif_ignore_entry_errors = _coerce_bool(
        kwargs.get("ldif_ignore_entry_errors", True), default=True,
    )
    builder.enable_ldif_streams = _coerce_bool(
        kwargs.get("enable_ldif_streams", False), default=False,
    )

    try:
        return builder.build()
    except Exception as e:
        return FlextResult.fail(f"Failed to create LDIF processing config: {e}")


def validate_ldap_config(config: TapLDAPConfig) -> FlextResult[bool]:
    """Validate the LDAP tap configuration.

    Args:
        config: Configuration to validate

    Returns:
        FlextResult with validation success or error message.

    """
    try:
        # Validate using Pydantic model validation
        config.model_validate(config.model_dump())

        # Constants for port validation
        max_port_number = 65535

        # Additional business rule validations
        if config.connection.port <= 0 or config.connection.port > max_port_number:
            return FlextResult.fail(f"Port must be between 1 and {max_port_number}")

        if not config.connection.base_dn:
            return FlextResult.fail("Base DN is required")

        default_ldap_port = 389
        if config.connection.use_ssl and config.connection.port == default_ldap_port:
            return FlextResult.fail(
                "SSL enabled but port is 389 (consider using port 636 for LDAPS)",
            )

        return FlextResult.ok(data=True)

    except (RuntimeError, ValueError, TypeError) as e:
        return FlextResult.fail(f"Configuration validation failed: {e}")


def create_development_ldap_config(**overrides: object) -> FlextResult[TapLDAPConfig]:
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


def create_production_ldap_config(**overrides: object) -> FlextResult[TapLDAPConfig]:
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
) -> FlextResult[TapLDAPConfig]:
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
__all__: list[str] = [
    "FlextResult",
    "LDAPConnectionParams",
    "LDIFConfigBuilder",
    "create_development_ldap_config",
    "create_ldap_connection_config",
    "create_ldap_connection_config_legacy",
    "create_ldif_processing_config",
    "create_ldif_processing_config_advanced",
    "create_production_ldap_config",
    "setup_ldap_tap",
    "validate_ldap_config",
]
