"""Configuration for tap-ldap using flext-core and flext-ldap integration.

Consolidates configuration and validation with maximum integration
to eliminate code duplication.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextResult, get_logger
from flext_ldap import FlextLdapConnectionConfig
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = get_logger(__name__)


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

    def validate_domain_rules(self) -> FlextResult[None]:
        """Validate domain-specific rules for custom streams."""
        if not self.name or not self.search_filter:
            return FlextResult.fail("Custom stream requires name and search_filter")

        return FlextResult.ok(None)


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

    def validate_domain_rules(self) -> FlextResult[None]:
        """Validate domain-specific rules for LDIF processing."""
        if self.ldif_files and self.ldif_directory:
            return FlextResult.fail("Cannot specify both ldif_files and ldif_directory")

        if self.enable_ldif_streams and not (self.ldif_files or self.ldif_directory):
            return FlextResult.fail(
                "LDIF streams enabled but no files or directory specified",
            )

        return FlextResult.ok(None)


class TapLDAPConfig(BaseSettings):
    """Complete configuration for tap-ldap using flext-core and flext-ldap patterns.

    Combines LDAP connection and LDIF processing configurations with Pydantic settings.
    Uses FlextLdapConnectionConfig from flext-ldap to eliminate duplication.
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

    # Core LDAP connection using flext-ldap config to eliminate duplication
    connection: FlextLdapConnectionConfig = Field(
        ...,
        description="LDAP connection configuration from flext-ldap",
    )

    # LDIF processing configuration
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

    # Tap-specific settings
    page_size: int = Field(
        default=1000,
        description="Page size for paged results",
        gt=0,
    )
    user_filter: str = Field(
        default="(objectClass=inetOrgPerson)",
        description="LDAP filter for user entries",
    )
    group_filter: str = Field(
        default="(objectClass=groupOfNames)",
        description="LDAP filter for group entries",
    )

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
            validation_errors: list[str] = []
            for stream_config in v:
                try:
                    # Convert dict[str, object] to proper types for validation
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

                    # Validate using our CustomStreamConfig
                    config_obj = CustomStreamConfig(
                        name=name,
                        search_filter=search_filter,
                        primary_keys=primary_keys,
                        replication_key=replication_key,
                        json_schema=json_schema,
                    )

                    # Validate domain rules
                    validation_result = config_obj.validate_domain_rules()

                    if not validation_result.success:
                        error_text = validation_result.error or "Unknown error"
                        validation_errors.append(
                            f"Invalid custom stream config: {error_text}",
                        )

                except (ValueError, TypeError) as e:
                    validation_errors.append(f"Invalid custom stream config: {e}")

            if validation_errors:
                # Raise a single ValueError summarizing all issues
                combined = "; ".join(validation_errors)
                raise ValueError(combined)
        return v

    def validate_complete_config(self) -> FlextResult[None]:
        """Validate the complete configuration with business rules."""
        try:
            # Validate LDIF processing config
            ldif_validation = self.ldif_processing.validate_domain_rules()
            if not ldif_validation.success:
                return FlextResult.fail(
                    f"LDIF config invalid: {ldif_validation.error or 'Unknown error'}",
                )

            # Validate custom streams if present
            if self.custom_streams:
                for stream_config in self.custom_streams:
                    name = str(stream_config.get("name", ""))
                    search_filter = str(stream_config.get("search_filter", ""))

                    # Normalize types safely for mypy
                    pk_raw = stream_config.get("primary_keys")
                    pk_list: list[str] | None = (
                        pk_raw if isinstance(pk_raw, list) else None
                    )
                    schema_raw = stream_config.get("json_schema")
                    schema_dict: dict[str, object] | None = (
                        schema_raw if isinstance(schema_raw, dict) else None
                    )

                    config_obj = CustomStreamConfig(
                        name=name,
                        search_filter=search_filter,
                        primary_keys=pk_list,
                        replication_key=str(stream_config.get("replication_key"))
                        if isinstance(stream_config.get("replication_key"), str)
                        else None,
                        json_schema=schema_dict,
                    )

                    stream_validation = config_obj.validate_domain_rules()
                    if not stream_validation.success:
                        msg = (
                            f"Custom stream '{name}' invalid: "
                            f"{stream_validation.error or 'Unknown error'}"
                        )
                        return FlextResult.fail(msg)

            return FlextResult.ok(None)

        except Exception as e:
            return FlextResult.fail(f"Configuration validation failed: {e}")

    @classmethod
    def create_with_defaults(cls, **overrides: object) -> TapLDAPConfig:
        """Create config with intelligent defaults using flext-ldap integration."""
        # Use FlextLdapConnectionConfig defaults
        ldap_defaults: dict[str, object] = {
            "host": "localhost",
            "port": 389,
            "use_ssl": False,
            "timeout_seconds": 30,
        }

        # LDIF processing defaults
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

        # Create FlextLdapConnectionConfig with proper parameters
        port_val = ldap_defaults.get("port", 389)
        timeout_val = ldap_defaults.get("timeout_seconds", 30)
        ldap_connection = FlextLdapConnectionConfig.model_validate(
            {
                "server": str(ldap_defaults.get("host", "localhost")),
                "port": int(port_val) if isinstance(port_val, (int, str)) else 389,
                "use_ssl": bool(ldap_defaults.get("use_ssl")),
                "timeout": int(timeout_val)
                if isinstance(timeout_val, (int, str))
                else 30,
            },
        )

        # Create LDIF processing config
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


# Export main configuration classes
__all__: list[str] = [
    "CustomStreamConfig",
    "LDIFProcessingConfig",
    "TapLDAPConfig",
]
