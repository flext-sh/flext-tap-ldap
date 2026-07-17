"""Tap LDAP extract-support helpers — stream rules, tap spec, entry packing.

All the tap's non-trivial logic lives here as a ``_utilities`` mixin composed
into the ``u`` facade; ``services/*`` stay thin orchestrators. Business rules are
read from ``config.TapLdap`` and packed into flext-meltano transport models.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tap_ldap import c, config, m, p, r, settings, t


class FlextTapLdapUtilitiesExtractSupport:
    """Extract helpers consumed by the tap services and CLI facade."""

    class TapLdap:
        """Tap-LDAP extract helper namespace."""

        @staticmethod
        def tap_spec() -> m.Meltano.TapSpec:
            """Build the Singer tap spec: config streams + settings config schema."""
            streams = [
                m.Meltano.StreamSpec(
                    name=rule.name,
                    json_schema=rule.stream_schema,
                    primary_keys=rule.primary_keys,
                )
                for rule in config.TapLdap.streams
            ]
            return m.Meltano.TapSpec(
                tap_name=c.TapLdap.TAP_NAME,
                config_jsonschema=type(settings).model_json_schema(),
                streams=streams,
            )

        @staticmethod
        def stream_search(
            stream_name: str,
            source: t.JsonMapping,
        ) -> p.Result[m.Ldap.SearchOptions]:
            """Resolve a stream's business rules into typed LDAP search options."""
            rule = next(
                (item for item in config.TapLdap.streams if item.name == stream_name),
                None,
            )
            if rule is None:
                return r[m.Ldap.SearchOptions].fail(f"Unknown stream: {stream_name}")
            base_dn = str(source.get("base_dn", settings.TapLdap.base_dn))
            return r[m.Ldap.SearchOptions].ok(
                m.Ldap.SearchOptions(
                    base_dn=base_dn,
                    filter_str=rule.filter,
                    attributes=list(rule.attributes),
                ),
            )

        @staticmethod
        def connection(source: t.JsonMapping) -> m.Ldap.ConnectionConfig:
            """Build the LDAP connection config from the tap runtime config."""
            return m.Ldap.ConnectionConfig.model_validate(dict(source))

        @staticmethod
        def pack_entries(
            entries: t.SequenceOf[p.Ldif.Entry],
        ) -> t.SequenceOf[t.JsonMapping]:
            """Pack flext-ldap entries into Singer-native JSON records."""
            records: list[t.JsonMapping] = []
            for entry in entries:
                dn_value: t.JsonValue = entry.dn.value if entry.dn is not None else ""
                attributes: t.MappingKV[str, t.StrSequence] = (
                    entry.attributes.attributes if entry.attributes is not None else {}
                )
                record: dict[str, t.JsonValue] = {"dn": dn_value}
                for key, value in attributes.items():
                    multiple: t.JsonValueList = list(value)
                    record[key] = value[0] if len(value) == 1 else multiple
                records.append(record)
            return records


__all__: list[str] = ["FlextTapLdapUtilitiesExtractSupport"]
