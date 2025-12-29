"""FLEXT Tap LDAP Utilities - Domain-specific utilities for LDAP tap operations.

This module provides complete LDAP tap utilities extending u
with nested classes for error handling, stream management, discovery operations,
and configuration validation. Follows FLEXT standards with single-class pattern.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import ClassVar

from flext_core import (
    FlextContainer,
    FlextExceptions,
    FlextLogger,
    FlextResult,
    FlextTypes as t,
)
from flext_core.utilities import u_core


class FlextMeltanoTapLdapUtilities(u_core):
    """Unified LDAP tap utilities class extending u classes.

    Provides complete LDAP tap utilities with nested classes for:
    - Error handling and exception creation
    - Stream information management
    - Discovery operations
    - Configuration validation
    - Performance optimization
    - Data extraction helpers

    Follows FLEXT pattern: single class with nested subclasses.
    """

    class TapLdap:
        """Tap LDAP namespace for cross-project access."""

        def __init__(self) -> None:
            """Initialize FlextMeltanoTapLdapUtilities service."""
            super().__init__()
            self._container = FlextContainer.get_global()
            self.logger = FlextLogger(__name__)

        def execute(self) -> FlextResult[dict[str, t.GeneralValueType]]:
            """Execute the main domain service operation.

            Returns:
            FlextResult[dict[str, t.GeneralValueType]]: Service status and capabilities.

            """
            return FlextResult[dict[str, t.GeneralValueType]].ok({
                "status": "operational",
                "service": "flext-tap-ldap-utilities",
                "capabilities": [
                    "error_handling",
                    "stream_management",
                    "discovery_operations",
                    "configuration_validation",
                    "performance_optimization",
                    "data_extraction",
                ],
            })

        @property
        def logger(self) -> FlextLogger:
            """Get logger instance."""
            return self.logger

        @property
        def container(self) -> FlextContainer:
            """Get container instance."""
            return self._container

        class ErrorHandling:
            """LDAP tap error handling utilities with enhanced context."""

            @staticmethod
            def create_connection_error(
                message: str = "LDAP connection failed",
                host: str | None = None,
                port: int | None = None,
                base_dn: str | None = None,
                **kwargs: object,
            ) -> FlextExceptions.ConnectionError:
                """Create LDAP connection errors with context."""
                context = kwargs.copy()
                if host is not None:
                    context["host"] = host
                if port is not None:
                    context["port"] = port
                if base_dn is not None:
                    context["base_dn"] = base_dn

                return FlextExceptions.ConnectionError(message, context=context)

            @staticmethod
            def create_bind_error(
                message: str = "LDAP bind failed",
                bind_dn: str | None = None,
                **kwargs: object,
            ) -> FlextExceptions.AuthenticationError:
                """Create LDAP bind/authentication errors with context."""
                context = kwargs.copy()
                if bind_dn is not None:
                    context["bind_dn"] = bind_dn

                return FlextExceptions.AuthenticationError(message, context=context)

            @staticmethod
            def create_search_error(
                message: str = "LDAP search failed",
                base_dn: str | None = None,
                filter_str: str | None = None,
                **kwargs: object,
            ) -> FlextExceptions.OperationError:
                """Create LDAP search errors with context."""
                context = kwargs.copy()
                if base_dn is not None:
                    context["base_dn"] = base_dn
                if filter_str is not None:
                    context["filter"] = filter_str[:100] if filter_str else None

                return FlextExceptions.OperationError(message, context=context)

            @staticmethod
            def create_stream_error(
                message: str = "Stream processing failed",
                stream_name: str | None = None,
                dn: str | None = None,
                **kwargs: object,
            ) -> FlextExceptions.OperationError:
                """Create stream processing errors with stream context."""
                context = kwargs.copy()
                if stream_name is not None:
                    context["stream_name"] = stream_name
                if dn is not None:
                    context["dn"] = dn

                return FlextExceptions.OperationError(message, context=context)

            @staticmethod
            def create_configuration_error(
                message: str = "Configuration validation failed",
                config_section: str | None = None,
                **kwargs: object,
            ) -> FlextExceptions.ConfigurationError:
                """Create configuration errors with section context."""
                context = kwargs.copy()
                if config_section is not None:
                    context["config_section"] = config_section

                return FlextExceptions.ConfigurationError(message, context=context)

        class StreamManagement:
            """LDAP tap stream management utilities."""

            @staticmethod
            def create_stream_info_from_ldap_entry(
                dn: str,
                attributes: dict[str, list[t.GeneralValueType]],
                stream_prefix: str = "ldap",
                replication_method: str = "FULL_TABLE",
            ) -> FlextResult[object]:
                """Create stream info from LDAP entry."""
                try:
                    # Extract object class to determine stream name
                    object_classes = attributes.get("objectClass", [])
                    if not object_classes:
                        return FlextResult[object].fail("Entry has no objectClass")

                    primary_class = str(object_classes[0]).lower()

                    stream_name = f"{stream_prefix}_{primary_class}"

                    stream_info = {
                        "stream_name": stream_name,
                        "table_name": primary_class,
                        "dn": dn,
                        "replication_method": replication_method,
                        "attribute_count": len(attributes),
                        "object_class": primary_class,
                    }

                    return FlextResult[object].ok(stream_info)

                except (ValueError, TypeError, KeyError, AttributeError, OSError) as e:
                    return FlextResult[object].fail(
                        f"Failed to create stream info from LDAP entry: {e}",
                    )

        class ConfigurationValidation:
            """LDAP tap configuration validation utilities."""

            @staticmethod
            def validate_ldap_config(
                config: dict,
            ) -> FlextResult[dict[str, t.GeneralValueType]]:
                """Validate LDAP configuration parameters."""
                try:
                    required_fields = [
                        "host",
                        "base_dn",
                    ]
                    for field in required_fields:
                        if field not in config:
                            return FlextResult[dict[str, t.GeneralValueType]].fail(
                                f"Missing required LDAP field: {field}",
                            )
                        if not config[field]:
                            return FlextResult[dict[str, t.GeneralValueType]].fail(
                                f"Empty LDAP field: {field}",
                            )

                    # Validate port if provided
                    if "port" in config:
                        try:
                            port = int(config["port"])
                            if port <= 0 or port > 65535:
                                return FlextResult[dict[str, t.GeneralValueType]].fail(
                                    "LDAP port must be between 1 and 65535",
                                )
                            config["port"] = port
                        except ValueError:
                            return FlextResult[dict[str, t.GeneralValueType]].fail(
                                "LDAP port must be numeric",
                            )

                    return FlextResult[dict[str, t.GeneralValueType]].ok(config)

                except (ValueError, TypeError, KeyError, AttributeError, OSError) as e:
                    return FlextResult[dict[str, t.GeneralValueType]].fail(
                        f"LDAP config validation failed: {e}",
                    )

        class PerformanceOptimization:
            """LDAP tap performance optimization utilities."""

            # Performance optimization constants
            DEFAULT_PAGE_SIZE: ClassVar[int] = 1000
            MAX_PARALLEL_SEARCHES: ClassVar[int] = 5
            MEMORY_THRESHOLD_MB: ClassVar[int] = 256

    # Constants for backward compatibility (imported from c.Ldap)
    # Use c.Ldap.DEFAULT_LDAP_PORT, c.Ldap.DEFAULT_LDAPS_PORT, c.Network.Port.MAX_PORT


# Runtime alias for simplified usage
u = FlextMeltanoTapLdapUtilities

__all__ = [
    "FlextMeltanoTapLdapUtilities",
    "u",
]
