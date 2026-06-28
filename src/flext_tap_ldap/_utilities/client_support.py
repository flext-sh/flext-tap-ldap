"""Tap LDAP client support utility namespace."""

from __future__ import annotations

from collections.abc import Mapping, MutableSequence

from flext_meltano import u
from flext_tap_ldap import c, p, r, t


class FlextTapLdapUtilitiesClientSupport:
    """Client-side normalization helpers shared across tap LDAP flows."""

    class ClientSupport:
        """Client-side normalization helpers shared across tap LDAP flows."""

        @staticmethod
        def build_server_uri(host: str, port: int, *, use_ssl: bool) -> str:
            """Build the canonical LDAP or LDAPS server URI."""
            protocol = "ldaps" if use_ssl else "ldap"
            return f"{protocol}://{host}:{port}"

        @staticmethod
        def normalize_scope(scope: str) -> str:
            """Normalize incoming scope strings to canonical LDAP values."""
            normalized_scope = scope.upper()
            valid_scopes = {
                c.Ldap.SearchScope.BASE,
                c.Ldap.SearchScope.ONELEVEL,
                c.Ldap.SearchScope.SUBTREE,
            }
            if normalized_scope in valid_scopes:
                return normalized_scope
            default_scope: str = str(c.Ldap.DEFAULT_SCOPE)
            return default_scope

        @staticmethod
        def to_entry_mapping(
            entry_data: p.Ldif.Entry
            | t.MappingKV[str, t.JsonValue | t.StrSequence]
            | None,
        ) -> p.Result[t.JsonMapping]:
            """Normalize LDAP entry payloads into a JSON mapping."""
            if entry_data is None:
                return r[t.JsonMapping].fail(
                    "Cannot convert None entry data",
                )
            if isinstance(entry_data, p.Ldif.Entry):
                dn_value = entry_data.dn.value if entry_data.dn is not None else ""
                empty_attributes: t.MutableStrSequenceMapping = {}
                raw_attributes: t.MappingKV[str, MutableSequence[str]] = (
                    entry_data.attributes.attributes
                    if entry_data.attributes is not None
                    else empty_attributes
                )
                entry_mapping: t.JsonDict = {"dn": dn_value}
                for key_str, value in raw_attributes.items():
                    if len(value) == 1:
                        entry_mapping[key_str] = value[0]
                    else:
                        value_payload: t.JsonValueList = list(value)
                        entry_mapping[key_str] = value_payload
                return r[t.JsonMapping].ok(entry_mapping)
            normalized_mapping = t.Cli.JSON_MAPPING_ADAPTER.validate_python(
                {
                    key: u.normalize_to_json_value(value)
                    for key, value in entry_data.items()
                },
            )
            return r[t.JsonMapping].ok(normalized_mapping)

        @staticmethod
        def extend_attributes_with_oracle_support(
            attributes: t.StrSequence | None,
            *,
            oracle_oid_mode: bool,
        ) -> MutableSequence[str] | None:
            """Extend requested attributes with Oracle-specific fields."""
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
            entry: t.JsonMapping,
        ) -> t.JsonMapping:
            """Normalize Oracle-specific LDAP entry attributes."""
            normalized_entry: t.JsonDict = {
                key: u.normalize_to_json_value(value) for key, value in entry.items()
            }
            raw_attributes: t.JsonValue = normalized_entry.get("attributes", {})
            attributes: t.JsonDict = {}
            if not isinstance(raw_attributes, dict):
                return normalized_entry
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
                    attributes["objectClass"] = u.normalize_to_json_value(
                        object_classes,
                    )
            normalized_entry["attributes"] = attributes
            return normalized_entry

        @classmethod
        def process_search_results(
            cls,
            search_result: t.SequenceOf[
                p.Ldif.Entry | t.MappingKV[str, t.JsonValue | t.StrSequence]
            ],
            *,
            size_limit: int,
        ) -> MutableSequence[t.JsonMapping]:
            """Normalize LDAP search results with optional size limiting."""
            entries: MutableSequence[t.JsonMapping] = []
            for index, entry_data in enumerate(search_result):
                if size_limit > 0 and index >= size_limit:
                    break
                convert_result = cls.to_entry_mapping(entry_data)
                if convert_result.failure:
                    continue
                entries.append(convert_result.value)
            return entries

        @classmethod
        def process_oracle_search_results(
            cls,
            search_result: t.SequenceOf[
                p.Ldif.Entry
                | t.JsonMapping
                | t.MappingKV[str, t.JsonValue | t.StrSequence]
            ],
            *,
            oracle_oid_mode: bool,
        ) -> MutableSequence[t.JsonMapping]:
            """Normalize LDAP search results and apply Oracle enrichment."""
            results: MutableSequence[t.JsonMapping] = []
            for entry in search_result:
                if isinstance(entry, Mapping):
                    entry_mapping: t.JsonMapping = (
                        t.Cli.JSON_MAPPING_ADAPTER.validate_python(
                            {
                                key: u.normalize_to_json_value(value)
                                for key, value in entry.items()
                            },
                        )
                    )
                else:
                    convert_result = cls.to_entry_mapping(entry)
                    if convert_result.failure:
                        continue
                    entry_mapping = convert_result.value
                if oracle_oid_mode:
                    results.append(cls.normalize_oracle_entry(entry_mapping))
                else:
                    results.append(entry_mapping)
            return results


__all__: list[str] = ["FlextTapLdapUtilitiesClientSupport"]
