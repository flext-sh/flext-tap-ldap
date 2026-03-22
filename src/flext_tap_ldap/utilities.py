"""Tap LDAP utilities with strict typed contracts."""

from __future__ import annotations

from collections.abc import Mapping
from typing import ClassVar

from flext_core import FlextContainer, FlextExceptions, FlextLogger, r
from flext_core.protocols import FlextProtocols as p
from flext_core.typings import t
from flext_ldap import FlextLdapUtilities
from flext_meltano import FlextMeltanoUtilities

from flext_tap_ldap.constants import FlextTapLdapConstants as c


class FlextTapLdapUtilities(FlextMeltanoUtilities, FlextLdapUtilities):
    """Unified LDAP tap utilities class."""

    class TapLdap:
        """Tap LDAP namespace for cross-project access."""

        def __init__(self) -> None:
            """Initialize TapLdap with global container and logger."""
            super().__init__()
            self._container = FlextContainer.get_global()
            self._logger = FlextLogger(__name__)

        @property
        def container(self) -> p.Container:
            """Return the global container instance."""
            return self._container

        @property
        def logger(self) -> FlextLogger:
            """Return the logger instance."""
            return self._logger

        def execute(self) -> r[Mapping[str, str | list[str]]]:
            """Execute tap LDAP utilities and return operational status."""
            return r[Mapping[str, str | list[str]]].ok({
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

        class ErrorHandling:
            """LDAP tap error handling utilities with enhanced context."""

            @staticmethod
            def create_bind_error(
                message: str = "LDAP bind failed",
                bind_dn: str | None = None,
                **kwargs: t.Scalar,
            ) -> FlextExceptions.AuthenticationError:
                """Create bind error with context."""
                context: dict[str, t.Scalar] = dict(kwargs)
                if bind_dn is not None:
                    context["bind_dn"] = bind_dn
                return FlextExceptions.AuthenticationError(message, context=context)

            @staticmethod
            def create_connection_error(
                message: str = "LDAP connection failed",
                host: str | None = None,
                port: int | None = None,
                base_dn: str | None = None,
                **kwargs: t.Scalar,
            ) -> FlextExceptions.ConnectionError:
                """Create connection error with context."""
                context: dict[str, t.Scalar] = dict(kwargs)
                if host is not None:
                    context["host"] = host
                if port is not None:
                    context["port"] = port
                if base_dn is not None:
                    context["base_dn"] = base_dn
                return FlextExceptions.ConnectionError(message, context=context)

            @staticmethod
            def create_search_error(
                message: str = "LDAP search failed",
                base_dn: str | None = None,
                filter_str: str | None = None,
                **kwargs: t.Scalar,
            ) -> FlextExceptions.OperationError:
                """Create search error with context."""
                context: dict[str, t.Scalar] = dict(kwargs)
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
            ) -> r[Mapping[str, str | int]]:
                """Create stream info from LDAP entry."""
                object_classes = attributes.get("objectClass", [])
                if not object_classes:
                    return r[Mapping[str, str | int]].fail("Entry has no objectClass")
                primary_class = object_classes[0].lower()
                stream_name = f"{stream_prefix}_{primary_class}"
                stream_info: Mapping[str, str | int] = {
                    "stream_name": stream_name,
                    "table_name": primary_class,
                    "dn": dn,
                    "replication_method": replication_method,
                    "attribute_count": len(attributes),
                    "object_class": primary_class,
                }
                return r[Mapping[str, str | int]].ok(stream_info)

        class ConfigurationValidation:
            """LDAP tap configuration validation utilities."""

            @staticmethod
            def validate_ldap_config(
                config: dict[str, t.NormalizedValue],
            ) -> r[Mapping[str, t.NormalizedValue]]:
                """Validate LDAP configuration."""
                if not isinstance(config, Mapping):
                    return r[Mapping[str, t.NormalizedValue]].fail(
                        "LDAP config must be a mapping",
                    )
                config_map: dict[str, t.NormalizedValue] = {
                    str(key): value for key, value in config.items()
                }
                required_fields = ["host", "base_dn"]
                for field in required_fields:
                    if field not in config_map:
                        return r[Mapping[str, t.NormalizedValue]].fail(
                            f"Missing required LDAP field: {field}",
                        )
                    if not str(config_map[field]).strip():
                        return r[Mapping[str, t.NormalizedValue]].fail(
                            f"Empty LDAP field: {field}",
                        )
                if "port" in config_map:
                    try:
                        port = int(str(config_map["port"]))
                    except ValueError:
                        return r[Mapping[str, t.NormalizedValue]].fail(
                            "LDAP port must be numeric",
                        )
                    if port <= 0 or port > c.TapLdap.Ldap.MAX_PORT:
                        return r[Mapping[str, t.NormalizedValue]].fail(
                            f"LDAP port must be between 1 and {c.TapLdap.Ldap.MAX_PORT}",
                        )
                    config_map["port"] = port
                return r[Mapping[str, t.NormalizedValue]].ok(config_map)

        class PerformanceOptimization:
            """LDAP tap performance optimization utilities."""

            DEFAULT_PAGE_SIZE: ClassVar[int] = c.TapLdap.DEFAULT_PAGE_SIZE
            MAX_PARALLEL_SEARCHES: ClassVar[int] = 5
            MEMORY_THRESHOLD_MB: ClassVar[int] = 256


u = FlextTapLdapUtilities
__all__ = ["FlextTapLdapUtilities", "u"]
