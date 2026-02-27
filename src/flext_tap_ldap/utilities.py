"""Tap LDAP utilities with strict typed contracts."""

from __future__ import annotations

from collections.abc import Mapping
from typing import ClassVar

from flext_core import FlextContainer, FlextExceptions, FlextLogger, FlextResult
from flext_core.utilities import FlextUtilities

from .constants import c

type MetadataValue = str | int | float | bool | None
type MetadataContext = dict[str, MetadataValue]
type ServiceStatus = Mapping[str, str | list[str]]
type StreamInfo = Mapping[str, str | int]
type LdapConfig = Mapping[str, str | int | bool]


class FlextMeltanoTapLdapUtilities(FlextUtilities):
    """Unified LDAP tap utilities class."""

    class TapLdap:
        """Tap LDAP namespace for cross-project access."""

        def __init__(self) -> None:
            """Initialize TapLdap with global container and logger."""
            super().__init__()
            self._container = FlextContainer.get_global()
            self._logger = FlextLogger(__name__)

        def execute(self) -> FlextResult[ServiceStatus]:
            """Execute tap LDAP utilities and return operational status."""
            return FlextResult[ServiceStatus].ok({
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
            """Return the logger instance."""
            return self._logger

        @property
        def container(self) -> FlextContainer:
            """Return the global container instance."""
            return self._container

        class ErrorHandling:
            """LDAP tap error handling utilities with enhanced context."""

            @staticmethod
            def create_connection_error(
                message: str = "LDAP connection failed",
                host: str | None = None,
                port: int | None = None,
                base_dn: str | None = None,
                **kwargs: MetadataValue,
            ) -> FlextExceptions.ConnectionError:
                """Create connection error with context."""
                context: MetadataContext = dict(kwargs)
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
                **kwargs: MetadataValue,
            ) -> FlextExceptions.AuthenticationError:
                """Create bind error with context."""
                context: MetadataContext = dict(kwargs)
                if bind_dn is not None:
                    context["bind_dn"] = bind_dn
                return FlextExceptions.AuthenticationError(message, context=context)

            @staticmethod
            def create_search_error(
                message: str = "LDAP search failed",
                base_dn: str | None = None,
                filter_str: str | None = None,
                **kwargs: MetadataValue,
            ) -> FlextExceptions.OperationError:
                """Create search error with context."""
                context: MetadataContext = dict(kwargs)
                if base_dn is not None:
                    context["base_dn"] = base_dn
                if filter_str is not None:
                    context["filter"] = filter_str[:100]
                return FlextExceptions.OperationError(message, context=context)

        class StreamManagement:
            """LDAP tap stream management utilities."""

            @staticmethod
            def create_stream_info_from_ldap_entry(
                dn: str,
                attributes: Mapping[str, list[str]],
                stream_prefix: str = "ldap",
                replication_method: str = "FULL_TABLE",
            ) -> FlextResult[StreamInfo]:
                """Create stream info from LDAP entry."""
                object_classes = attributes.get("objectClass", [])
                if not object_classes:
                    return FlextResult[StreamInfo].fail("Entry has no objectClass")

                primary_class = object_classes[0].lower()
                stream_name = f"{stream_prefix}_{primary_class}"
                stream_info: StreamInfo = {
                    "stream_name": stream_name,
                    "table_name": primary_class,
                    "dn": dn,
                    "replication_method": replication_method,
                    "attribute_count": len(attributes),
                    "object_class": primary_class,
                }
                return FlextResult[StreamInfo].ok(stream_info)

        class ConfigurationValidation:
            """LDAP tap configuration validation utilities."""

            @staticmethod
            def validate_ldap_config(config: LdapConfig) -> FlextResult[LdapConfig]:
                """Validate LDAP configuration."""
                config_map = dict(config)
                required_fields = ["host", "base_dn"]
                for field in required_fields:
                    if field not in config_map:
                        return FlextResult[LdapConfig].fail(
                            f"Missing required LDAP field: {field}",
                        )
                    if not str(config_map[field]).strip():
                        return FlextResult[LdapConfig].fail(
                            f"Empty LDAP field: {field}",
                        )

                if "port" in config_map:
                    try:
                        port = int(str(config_map["port"]))
                    except ValueError:
                        return FlextResult[LdapConfig].fail("LDAP port must be numeric")
                    if port <= 0 or port > c.TapLdap.Ldap.MAX_PORT:
                        return FlextResult[LdapConfig].fail(
                            f"LDAP port must be between 1 and {c.TapLdap.Ldap.MAX_PORT}",
                        )
                    config_map["port"] = port

                return FlextResult[LdapConfig].ok(config_map)

        class PerformanceOptimization:
            """LDAP tap performance optimization utilities."""

            DEFAULT_PAGE_SIZE: ClassVar[int] = 1000
            MAX_PARALLEL_SEARCHES: ClassVar[int] = 5
            MEMORY_THRESHOLD_MB: ClassVar[int] = 256


u: type[FlextMeltanoTapLdapUtilities] = FlextMeltanoTapLdapUtilities

__all__ = ["FlextMeltanoTapLdapUtilities", "u"]
