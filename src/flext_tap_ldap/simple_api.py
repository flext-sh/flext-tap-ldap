"""Simple API for LDAP tap setup and operations using flext-core patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

from flext_core import FlextCore

from flext_tap_ldap.config import (
    FlextMeltanoTapLdapConfig,
    LDAPConnectionConfig,
    LDIFProcessingConfig,
)
from flext_tap_ldap.typings import FlextMeltanoTapLdapTypes


class FlextMeltanoTapLdapServices:
    """LDAP tap services for Meltano integration."""

    def _coerce_str_optional(self: object) -> str | None:
        """Coerce value to optional string using pattern matching."""
        match self:
            case str() as str_val if str_val:
                return str_val
            case _:
                return None

    def _coerce_bool(self: object, *, default: bool = False) -> bool:
        """Coerce arbitrary value to bool with sensible defaults."""
        if isinstance(self, bool):
            return self
        if isinstance(self, str):
            lowered = self.strip().lower()
            if lowered in {"true", "1", "yes", "y", "on"}:
                return True
            if lowered in {"false", "0", "no", "n", "off"}:
                return False
        if isinstance(self, (int, float)):
            return bool(self)
        return default

    def _coerce_int(self: object, default: int) -> int:
        """Coerce arbitrary value to int, or return default on failure."""
        if isinstance(self, int):
            return self
        if isinstance(self, float):
            return int(self)
        if isinstance(self, str):
            try:
                return int(self.strip())
            except ValueError:
                return default
        return default

    @dataclass
    class LDAPConnectionParams:
        """Parameter object for LDAP connection configuration.

        Implements Parameter Object Pattern to reduce argument count
        and improve maintainability
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

        ldif_files: FlextMeltanoTapLdapTypes.Core.StringList = field(
            default_factory=list
        )
        ldif_directory: str | None = None
        ldif_file_pattern: str = "*.ldif"
        ldif_ignore_errors: bool = True
        ldif_max_errors: int = 100
        ldif_ignore_file_errors: bool = True
        ldif_ignore_entry_errors: bool = True
        ldif_apply_transformations: bool = False
        ldif_transformation_rules: FlextMeltanoTapLdapTypes.Core.Dict = field(
            default_factory=dict
        )
        migration_batch: str | None = None
        enable_ldif_streams: bool = False

        def with_files(
            self, files: FlextMeltanoTapLdapTypes.Core.StringList
        ) -> FlextMeltanoTapLdapServices.LDIFConfigBuilder:
            """Set LDIF files to process."""
            self.ldif_files = files
            return self

        def with_directory(
            self, directory: str
        ) -> FlextMeltanoTapLdapServices.LDIFConfigBuilder:
            """Set LDIF directory to scan."""
            self.ldif_directory = directory
            return self

        def with_pattern(
            self, pattern: str
        ) -> FlextMeltanoTapLdapServices.LDIFConfigBuilder:
            """Set file pattern for scanning."""
            self.ldif_file_pattern = pattern
            return self

        def with_error_handling(
            self,
            *,
            ignore_errors: bool = True,
            max_errors: int = 100,
        ) -> FlextMeltanoTapLdapServices.LDIFConfigBuilder:
            """Configure error handling behavior."""
            self.ldif_ignore_errors = ignore_errors
            self.ldif_max_errors = max_errors
            return self

        def with_transformations(
            self,
            *,
            enable: bool = True,
            rules: FlextMeltanoTapLdapTypes.Core.Dict | None = None,
        ) -> FlextMeltanoTapLdapServices.LDIFConfigBuilder:
            """Configure transformation settings."""
            self.ldif_apply_transformations = enable
            if rules:
                self.ldif_transformation_rules = rules
            return self

        def with_migration_batch(
            self, batch_name: str
        ) -> FlextMeltanoTapLdapServices.LDIFConfigBuilder:
            """Set migration batch identifier."""
            self.migration_batch = batch_name
            return self

        def build(self: object) -> FlextCore.Result[LDIFProcessingConfig]:
            """Build the LDIF processing configuration."""
            try:
                return FlextCore.Result[LDIFProcessingConfig].ok(
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
                return FlextCore.Result[LDIFProcessingConfig].fail(
                    f"Failed to build LDIF processing config: {e}",
                )

    def setup_ldap_tap(
        self: FlextMeltanoTapLdapConfig | None = None,
    ) -> FlextCore.Result[FlextMeltanoTapLdapConfig]:
        """Set up the LDAP tap with configuration.

        Args:
        config: Optional configuration. If None, creates defaults.

        Returns:
        FlextCore.Result with FlextMeltanoTapLdapConfig or error message.

        """
        try:
            if self is None:
                # Create with intelligent defaults
                self = FlextMeltanoTapLdapConfig.create_with_defaults()

            # Validate configuration
            self.model_validate(self.model_dump())

            return FlextCore.Result[FlextMeltanoTapLdapConfig].ok(self)

        except (RuntimeError, ValueError, TypeError) as e:
            return FlextCore.Result[FlextMeltanoTapLdapConfig].fail(
                f"Failed to setup LDAP tap: {e}"
            )

    def create_ldap_connection_config(
        self: FlextMeltanoTapLdapServices.LDAPConnectionParams,
    ) -> FlextCore.Result[LDAPConnectionConfig]:
        """Create LDAP connection configuration using Parameter Object Pattern.

        Args:
        params: LDAP connection parameters object

        Returns:
        FlextCore.Result with LDAPConnectionConfig or error message.

        """
        try:
            config: FlextCore.Types.Dict = LDAPConnectionConfig(
                host=self.host,
                base_dn=self.base_dn,
                port=self.port,
                use_ssl=self.use_ssl,
                bind_dn=self.bind_dn,
                bind_password=self.bind_password,
            )

            return FlextCore.Result[LDAPConnectionConfig].ok(config)

        except (RuntimeError, ValueError, TypeError) as e:
            return FlextCore.Result[LDAPConnectionConfig].fail(
                f"Failed to create LDAP connection config: {e}",
            )

    def create_ldap_connection_config_convenience(
        self: str,
        base_dn: str,
        port: int = 389,
        **kwargs: object,
    ) -> FlextCore.Result[LDAPConnectionConfig]:
        """Create LDAP connection configuration (testing convenience interface).

        Testing convenience wrapper for the Parameter Object Pattern implementation.
        Use FlextMeltanoTapLdapServices.create_ldap_connection_config() with FlextMeltanoTapLdapServices.LDAPConnectionParams for new code.
        """
        try:
            params = FlextMeltanoTapLdapServices.LDAPConnectionParams(
                host=self,
                base_dn=base_dn,
                port=port,
                use_ssl=bool(kwargs.get("use_ssl")),
                bind_dn=self._coerce_str_optional(kwargs.get("bind_dn")),
                bind_password=self._coerce_str_optional(kwargs.get("bind_password")),
            )
            return FlextMeltanoTapLdapServices.create_ldap_connection_config(params)
        except Exception as e:
            return FlextCore.Result[LDAPConnectionConfig].fail(
                f"Failed to create convenience connection config: {e}",
            )

    def create_ldif_processing_config(
        self: FlextMeltanoTapLdapTypes.Core.StringList | None = None,
        ldif_directory: str | None = None,
        **kwargs: object,
    ) -> FlextCore.Result[LDIFProcessingConfig]:
        """Create LDIF processing configuration.

        REFACTORED: Now uses Builder Pattern internally to eliminate parameter proliferation.
        Maintains testing convenience while providing cleaner internal implementation.

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
        FlextCore.Result with LDIFProcessingConfig or error message.

        Keyword Args:
        **kwargs: Optional keyword-only parameters, including:
            - ldif_file_pattern: Pattern for LDIF files (default: *.ldif).
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
        builder = FlextMeltanoTapLdapServices.LDIFConfigBuilder()

        # Files and directory
        if self:
            builder.with_files(self)
        if ldif_directory:
            builder.with_directory(ldif_directory)

        builder.with_pattern(str(kwargs.get("ldif_file_pattern", "*.ldif")))

        ignore_errors = self._coerce_bool(
            kwargs.get("ldif_ignore_errors", True), default=True
        )
        max_errors = self._coerce_int(kwargs.get("ldif_max_errors", 100), 100)
        builder.with_error_handling(ignore_errors=ignore_errors, max_errors=max_errors)

        apply_transformations = self._coerce_bool(
            kwargs.get("ldif_apply_transformations", False),
            default=False,
        )
        rules = kwargs.get("ldif_transformation_rules")
        rules_dict: FlextCore.Types.Dict = rules if isinstance(rules, dict) else None
        builder.with_transformations(enable=apply_transformations, rules=rules_dict)

        batch = self._coerce_str_optional(kwargs.get("migration_batch"))
        if batch:
            builder.with_migration_batch(batch)

        # Direct attribute settings
        builder.ldif_ignore_file_errors = self._coerce_bool(
            kwargs.get("ldif_ignore_file_errors", True),
            default=True,
        )
        builder.ldif_ignore_entry_errors = self._coerce_bool(
            kwargs.get("ldif_ignore_entry_errors", True),
            default=True,
        )
        builder.enable_ldif_streams = self._coerce_bool(
            kwargs.get("enable_ldif_streams", False),
            default=False,
        )

        try:
            return builder.build()
        except Exception as e:
            return FlextCore.Result[LDIFProcessingConfig].fail(
                f"Failed to create LDIF processing config: {e}",
            )

    def validate_ldap_config(self: FlextMeltanoTapLdapConfig) -> FlextCore.Result[bool]:
        """Validate the LDAP tap configuration.

        Args:
        config: Configuration to validate

        Returns:
        FlextCore.Result with validation success or error message.

        """
        try:
            # Validate using Pydantic model validation
            self.model_validate(self.model_dump())

            # Constants for port validation
            max_port_number = 65535

            # Additional business rule validations
            if self.connection.port <= 0 or self.connection.port > max_port_number:
                return FlextCore.Result[bool].fail(
                    f"Port must be between 1 and {max_port_number}",
                )

            if not self.connection.base_dn:
                return FlextCore.Result[bool].fail("Base DN is required")

            default_ldap_port = 389
            if self.connection.use_ssl and self.connection.port == default_ldap_port:
                return FlextCore.Result[bool].fail(
                    "SSL enabled but port is 389 (consider using port 636 for LDAPS)",
                )

            return FlextCore.Result[bool].ok(data=True)

        except (RuntimeError, ValueError, TypeError) as e:
            return FlextCore.Result[bool].fail(f"Configuration validation failed: {e}")

    def create_development_ldap_config(
        **overrides: object,
    ) -> FlextCore.Result[FlextMeltanoTapLdapConfig]:
        """Create development LDAP configuration with defaults.

        Args:
        **overrides: Configuration overrides

        Returns:
        FlextCore.Result with FlextMeltanoTapLdapConfig for development use.

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

            config = FlextMeltanoTapLdapConfig(
                connection=connection_config,
                ldif_processing=LDIFProcessingConfig(enable_ldif_streams=False),
                project_name="flext-data.taps.flext-tap-ldap",
                project_version="0.9.0",
            )

            # Apply overrides
            if overrides:
                config_dict: FlextCore.Types.Dict = config.model_dump()
                config_dict.update(overrides)
                config = FlextMeltanoTapLdapConfig(**config_dict)

            return FlextCore.Result[FlextMeltanoTapLdapConfig].ok(config)

        except (RuntimeError, ValueError, TypeError) as e:
            return FlextCore.Result[FlextMeltanoTapLdapConfig].fail(
                f"Failed to create development config: {e}",
            )

    def create_production_ldap_config(
        **overrides: object,
    ) -> FlextCore.Result[FlextMeltanoTapLdapConfig]:
        """Create production LDAP configuration with security defaults.

        Args:
        **overrides: Configuration overrides

        Returns:
        FlextCore.Result with FlextMeltanoTapLdapConfig for production use.

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

            config = FlextMeltanoTapLdapConfig(
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
                config_dict: FlextCore.Types.Dict = config.model_dump()
                config_dict.update(overrides)
                config = FlextMeltanoTapLdapConfig(**config_dict)

            return FlextCore.Result[FlextMeltanoTapLdapConfig].ok(config)

        except (RuntimeError, ValueError, TypeError) as e:
            return FlextCore.Result[FlextMeltanoTapLdapConfig].fail(
                f"Failed to create production config: {e}",
            )

    def create_ldif_processing_config_advanced(
        self: str | None = None,
        ldif_files: FlextMeltanoTapLdapTypes.Core.StringList | None = None,
        **overrides: object,
    ) -> FlextCore.Result[FlextMeltanoTapLdapConfig]:
        """Create LDIF processing configuration for migration scenarios.

        Args:
        ldif_directory: Directory containing LDIF files
        ldif_files: List of specific LDIF files
        **overrides: Additional configuration overrides

        Returns:
        FlextCore.Result with FlextMeltanoTapLdapConfig optimized for LDIF processing.

        """
        try:
            # Minimal connection config (not used for LDIF processing)
            connection_config = LDAPConnectionConfig(
                host="dummy",
                base_dn="dc=migration,dc=temp",
            )

            ldif_config = LDIFProcessingConfig(
                ldif_directory=self,
                ldif_files=ldif_files,
                enable_ldif_streams=True,
                ldif_ignore_errors=True,
                ldif_ignore_file_errors=True,
                ldif_ignore_entry_errors=True,
                ldif_max_errors=1000,
                ldif_apply_transformations=False,
            )

            config = FlextMeltanoTapLdapConfig(
                connection=connection_config,
                ldif_processing=ldif_config,
                project_name="flext-data.taps.flext-tap-ldap",
                project_version="0.9.0",
            )

            # Apply overrides
            if overrides:
                config_dict: FlextCore.Types.Dict = config.model_dump()
                config_dict.update(overrides)
                config = FlextMeltanoTapLdapConfig(**config_dict)

            return FlextCore.Result[FlextMeltanoTapLdapConfig].ok(config)

        except (RuntimeError, ValueError, TypeError) as e:
            return FlextCore.Result[FlextMeltanoTapLdapConfig].fail(
                f"Failed to create LDIF processing config: {e}",
            )


# Export main API functions
__all__ = [
    "FlextMeltanoTapLdapServices",
]
