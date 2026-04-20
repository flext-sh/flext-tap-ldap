"""Tap LDAP utilities with strict typed contracts."""

from __future__ import annotations

from collections.abc import (
    Mapping,
    MutableSequence,
    Sequence,
)

from flext_ldap import FlextLdapUtilities
from flext_meltano import FlextMeltanoUtilities
from flext_tap_ldap import FlextTapLdapUtilitiesProcessorMixin, c, e, p, r, t


class FlextTapLdapUtilities(
    FlextTapLdapUtilitiesProcessorMixin,
    FlextMeltanoUtilities,
    FlextLdapUtilities,
):
    """Unified LDAP tap utilities class."""

    class TapLdap(FlextTapLdapUtilitiesProcessorMixin.TapLdap):
        """Tap LDAP namespace for cross-project access."""

        class ClientSupport:
            """Client-side normalization helpers shared across tap LDAP flows."""

            @staticmethod
            def build_server_uri(host: str, port: int, *, use_ssl: bool) -> str:
                """Build the canonical LDAP or LDAPS server URI."""
                protocol = "ldaps" if use_ssl else "ldap"
                return f"{protocol}://{host}:{port}"

            @staticmethod
            def normalize_scope(scope: str) -> str:
                """Normalize incoming scope strings to the canonical LDAP values."""
                normalized_scope = scope.upper()
                valid_scopes = {
                    c.Ldap.SearchScope.BASE,
                    c.Ldap.SearchScope.ONELEVEL,
                    c.Ldap.SearchScope.SUBTREE,
                }
                if normalized_scope in valid_scopes:
                    return normalized_scope
                return c.Ldap.SearchDefaults.DEFAULT_SCOPE

            @staticmethod
            def to_entry_mapping(
                entry_data: p.Ldif.Entry | Mapping[str, t.Container] | None,
            ) -> p.Result[t.MutableRecursiveContainerMapping]:
                """Normalize LDAP entry payloads into the canonical mutable mapping contract."""
                if entry_data is None:
                    return r[t.MutableRecursiveContainerMapping].fail(
                        "Cannot convert None entry data",
                    )
                if isinstance(entry_data, p.Ldif.Entry):
                    dn_value = entry_data.dn.value if entry_data.dn is not None else ""
                    empty_attributes: t.MutableStrSequenceMapping = {}
                    raw_attributes: Mapping[str, MutableSequence[str]] = (
                        entry_data.attributes.attributes
                        if entry_data.attributes is not None
                        else empty_attributes
                    )
                    entry_mapping: t.MutableRecursiveContainerMapping = {"dn": dn_value}
                    for key_str, value in raw_attributes.items():
                        if len(value) == 1:
                            entry_mapping[str(key_str)] = value[0]
                        else:
                            entry_mapping[str(key_str)] = list(value)
                    return r[t.MutableRecursiveContainerMapping].ok(entry_mapping)
                normalized_mapping: t.MutableRecursiveContainerMapping = {}
                for key, value in entry_data.items():
                    if isinstance(
                        value,
                        (str, int, float, bool, list, dict, type(None)),
                    ):
                        normalized_mapping[str(key)] = value
                return r[t.MutableRecursiveContainerMapping].ok(normalized_mapping)

            @staticmethod
            def extend_attributes_with_oracle_support(
                attributes: t.StrSequence | None,
                *,
                oracle_oid_mode: bool,
            ) -> MutableSequence[str] | None:
                """Extend requested attributes with Oracle-specific fields when enabled."""
                if not oracle_oid_mode or not attributes:
                    return list(attributes) if attributes else None
                oracle_attributes = [
                    "orclPassword",
                    "orclPasswordAttribute",
                    "userPassword",
                ]
                extended_attributes = list(attributes)
                for oracle_attribute in oracle_attributes:
                    if oracle_attribute not in extended_attributes:
                        extended_attributes.append(oracle_attribute)
                return extended_attributes

            @staticmethod
            def normalize_oracle_entry(
                entry: t.MutableRecursiveContainerMapping,
            ) -> t.MutableRecursiveContainerMapping:
                """Normalize Oracle-specific LDAP entry attributes for downstream consumers."""
                raw_attributes: t.Container = entry.get("attributes", {})
                attributes: t.MutableRecursiveContainerMapping = {}
                if not isinstance(raw_attributes, dict):
                    return entry
                attributes.update(raw_attributes)
                if "orclPassword" in attributes:
                    password_value = attributes.get("orclPassword")
                    if password_value is not None:
                        attributes["userPassword"] = password_value
                if "objectClass" in attributes:
                    raw_object_classes = attributes["objectClass"]
                    object_classes: MutableSequence[str] = []
                    if isinstance(raw_object_classes, str):
                        object_classes = [raw_object_classes]
                    elif isinstance(raw_object_classes, list):
                        object_classes = [str(item) for item in raw_object_classes]
                    if (
                        "orclContainer" in object_classes
                        and "organizationalUnit" not in object_classes
                    ):
                        object_classes.append("organizationalUnit")
                        attributes["objectClass"] = object_classes
                entry["attributes"] = attributes
                return entry

            @staticmethod
            def process_search_results(
                search_result: Sequence[p.Ldif.Entry | Mapping[str, t.Container]],
                *,
                size_limit: int,
            ) -> MutableSequence[t.MutableRecursiveContainerMapping]:
                """Normalize LDAP search results into mutable mappings with optional size limiting."""
                entries: MutableSequence[t.MutableRecursiveContainerMapping] = []
                for index, entry_data in enumerate(search_result):
                    if size_limit > 0 and index >= size_limit:
                        break
                    convert_result = (
                        FlextTapLdapUtilities.TapLdap.ClientSupport.to_entry_mapping(
                            entry_data,
                        )
                    )
                    if convert_result.failure:
                        continue
                    entries.append(convert_result.value)
                return entries

            @staticmethod
            def process_oracle_search_results(
                search_result: Sequence[p.Ldif.Entry | Mapping[str, t.Container]],
                *,
                oracle_oid_mode: bool,
            ) -> MutableSequence[t.MutableRecursiveContainerMapping]:
                """Normalize LDAP search results and apply Oracle-specific enrichment when requested."""
                results: MutableSequence[t.MutableRecursiveContainerMapping] = []
                for entry in search_result:
                    if isinstance(entry, Mapping):
                        entry_mapping: t.MutableRecursiveContainerMapping = {
                            str(key): value for key, value in entry.items()
                        }
                    else:
                        convert_result = FlextTapLdapUtilities.TapLdap.ClientSupport.to_entry_mapping(
                            entry,
                        )
                        if convert_result.failure:
                            continue
                        entry_mapping = convert_result.value
                    if oracle_oid_mode:
                        results.append(
                            FlextTapLdapUtilities.TapLdap.ClientSupport.normalize_oracle_entry(
                                entry_mapping,
                            ),
                        )
                    else:
                        results.append(entry_mapping)
                return results

        class ValueConversion:
            """Strict adapter-based value conversion helpers for tap LDAP flows."""

            @staticmethod
            def to_map(
                value: t.Container,
            ) -> t.ContainerValueMapping | None:
                """Convert a recursive container to the canonical mapping contract."""
                try:
                    return t.CONFIG_MAP_ADAPTER.validate_python(value)
                except c.ValidationError:
                    return None

            @staticmethod
            def to_str(value: t.Container) -> str | None:
                """Convert a recursive container to a strict string contract."""
                try:
                    return t.STRICT_STR_ADAPTER.validate_python(value)
                except c.ValidationError:
                    return None

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
            ) -> p.Result[t.HeaderMapping]:
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
                settings: Mapping[str, t.Container],
            ) -> p.Result[Mapping[str, t.Container]]:
                """Validate LDAP configuration."""
                config_map: t.MutableRecursiveContainerMapping = {
                    str(key): value for key, value in settings.items()
                }
                required_fields = ["host", "base_dn"]
                for field in required_fields:
                    if field not in config_map:
                        return r[Mapping[str, t.Container]].fail(
                            f"Missing required LDAP field: {field}",
                        )
                    if not str(config_map[field]).strip():
                        return r[Mapping[str, t.Container]].fail(
                            f"Empty LDAP field: {field}",
                        )
                if "port" in config_map:
                    try:
                        port = t.INTEGER_ADAPTER.validate_python(config_map["port"])
                    except c.ValidationError:
                        return r[Mapping[str, t.Container]].fail(
                            "LDAP port must be numeric",
                        )
                    if port <= 0 or port > c.TapLdap.Ldap.MAX_PORT:
                        return r[Mapping[str, t.Container]].fail(
                            f"LDAP port must be between 1 and {c.TapLdap.Ldap.MAX_PORT}",
                        )
                    config_map["port"] = port
                return r[Mapping[str, t.Container]].ok(config_map)


u = FlextTapLdapUtilities
__all__: list[str] = ["FlextTapLdapUtilities", "u"]
