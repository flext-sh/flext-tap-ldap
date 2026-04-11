"""Tap LDAP utilities with strict typed contracts."""

from __future__ import annotations

from collections.abc import Mapping

from pydantic import ValidationError

from flext_core import e, r
from flext_ldap import FlextLdapUtilities
from flext_meltano import FlextMeltanoUtilities
from flext_tap_ldap import FlextTapLdapUtilitiesProcessorMixin, c, t


class FlextTapLdapUtilities(
    FlextTapLdapUtilitiesProcessorMixin,
    FlextMeltanoUtilities,
    FlextLdapUtilities,
):
    """Unified LDAP tap utilities class."""

    class TapLdap(FlextTapLdapUtilitiesProcessorMixin.TapLdap):
        """Tap LDAP namespace for cross-project access."""

        class ErrorHandling:
            """LDAP tap error handling utilities with enhanced context."""

            @staticmethod
            def create_bind_error(
                message: str = "LDAP bind failed",
                bind_dn: str | None = None,
                **kwargs: t.Scalar,
            ) -> e.AuthenticationError:
                """Create bind error with context."""
                context: t.MutableConfigurationMapping = dict(kwargs)
                if bind_dn is not None:
                    context["bind_dn"] = bind_dn
                return e.AuthenticationError(message, context=context)

            @staticmethod
            def create_connection_error(
                message: str = "LDAP connection failed",
                host: str | None = None,
                port: int | None = None,
                base_dn: str | None = None,
                **kwargs: t.Scalar,
            ) -> e.ConnectionError:
                """Create connection error with context."""
                context: t.MutableConfigurationMapping = dict(kwargs)
                if host is not None:
                    context["host"] = host
                if port is not None:
                    context["port"] = port
                if base_dn is not None:
                    context["base_dn"] = base_dn
                return e.ConnectionError(message, context=context)

            @staticmethod
            def create_search_error(
                message: str = "LDAP search failed",
                base_dn: str | None = None,
                filter_str: str | None = None,
                **kwargs: t.Scalar,
            ) -> e.OperationError:
                """Create search error with context."""
                context: t.MutableConfigurationMapping = dict(kwargs)
                if base_dn is not None:
                    context["base_dn"] = base_dn
                if filter_str is not None:
                    context["filter"] = filter_str[:100]
                return e.OperationError(message, context=context)

        class StreamManagement:
            """LDAP tap stream management utilities."""

            @staticmethod
            def create_stream_info_from_ldap_entry(
                dn: str,
                attributes: Mapping[str, t.StrSequence],
                stream_prefix: str = "ldap",
                replication_method: str = "FULL_TABLE",
            ) -> r[t.HeaderMapping]:
                """Create stream info from LDAP entry."""
                object_classes = attributes.get("objectClass", [])
                if not object_classes:
                    return r[t.HeaderMapping].fail("Entry has no objectClass")
                primary_class = object_classes[0].lower()
                stream_name = f"{stream_prefix}_{primary_class}"
                stream_info: t.HeaderMapping = {
                    "stream_name": stream_name,
                    "table_name": primary_class,
                    "dn": dn,
                    "replication_method": replication_method,
                    "attribute_count": len(attributes),
                    "object_class": primary_class,
                }
                return r[t.HeaderMapping].ok(stream_info)

        class ConfigurationValidation:
            """LDAP tap configuration validation utilities."""

            @staticmethod
            def validate_ldap_config(
                settings: t.ContainerMapping,
            ) -> r[t.ContainerMapping]:
                """Validate LDAP configuration."""
                config_map: t.MutableContainerMapping = {
                    str(key): value for key, value in settings.items()
                }
                required_fields = ["host", "base_dn"]
                for field in required_fields:
                    if field not in config_map:
                        return r[t.ContainerMapping].fail(
                            f"Missing required LDAP field: {field}",
                        )
                    if not str(config_map[field]).strip():
                        return r[t.ContainerMapping].fail(
                            f"Empty LDAP field: {field}",
                        )
                if "port" in config_map:
                    try:
                        port = t.INTEGER_ADAPTER.validate_python(config_map["port"])
                    except ValidationError:
                        return r[t.ContainerMapping].fail(
                            "LDAP port must be numeric",
                        )
                    if port <= 0 or port > c.TapLdap.Ldap.MAX_PORT:
                        return r[t.ContainerMapping].fail(
                            f"LDAP port must be between 1 and {c.TapLdap.Ldap.MAX_PORT}",
                        )
                    config_map["port"] = port
                return r[t.ContainerMapping].ok(config_map)


u = FlextTapLdapUtilities
__all__ = ["FlextTapLdapUtilities", "u"]
