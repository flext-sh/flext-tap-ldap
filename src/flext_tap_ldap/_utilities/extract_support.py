"""Tap LDAP extract-support helpers — stream rules, tap spec, entry packing.

All the tap's non-trivial logic lives here as a ``_utilities`` mixin composed
into the ``u`` facade; ``services/*`` stay thin orchestrators. Business rules are
read from the business rules under ``config.TapLdap`` (validated by
``u.TapLdap.tap_ldap()``) and packed into flext-meltano transport models.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Sequence

from flext_tap_ldap import c, config, m, p, r, settings, t


class FlextTapLdapUtilitiesExtractSupport:
    """Extract helpers consumed by the tap services and CLI facade."""

    @staticmethod
    def tap_ldap() -> m.TapLdap.TapLdap:
        """Validated TapLdap business-rule config (streams and their contracts).

        Returns:
            The resulting ``m.TapLdap.TapLdap``.

        """
        payload: t.JsonMapping = config.TapLdap.model_dump()
        return m.TapLdap.TapLdap.model_validate(dict(payload))

    @staticmethod
    def tap_spec() -> m.Meltano.TapSpec:
        """Build the Singer tap spec: config streams + settings config schema.

        Returns:
            The resulting ``m.Meltano.TapSpec``.

        """
        streams = tuple(
            m.Meltano.StreamSpec(
                name=rule.name,
                json_schema=rule.stream_schema,
                primary_keys=tuple(rule.primary_keys),
            )
            for rule in FlextTapLdapUtilitiesExtractSupport.tap_ldap().streams
        )
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
        """Resolve a stream's business rules into typed LDAP search options.

        Args:
            stream_name: Singer stream name to resolve.
            source: Tap runtime config mapping providing the base DN.

        Returns:
            The resulting ``p.Result[m.Ldap.SearchOptions]``.

        """
        rule = next(
            (
                item
                for item in FlextTapLdapUtilitiesExtractSupport.tap_ldap().streams
                if item.name == stream_name
            ),
            None,
        )
        if rule is None:
            return r[m.Ldap.SearchOptions].fail(f"Unknown stream: {stream_name}")
        return r[m.Ldap.SearchOptions].from_validation(
            {
                "base_dn": source.get("base_dn", settings.TapLdap.base_dn),
                "filter_str": rule.filter,
                "attributes": list(rule.attributes),
            },
            m.Ldap.SearchOptions,
        )

    @staticmethod
    def connection(source: t.JsonMapping) -> m.Ldap.ConnectionConfig:
        """Build the LDAP connection config from the tap runtime config.

        Args:
            source: Tap runtime config mapping validated into the
                connection model.

        Returns:
            The resulting ``m.Ldap.ConnectionConfig``.

        """
        return m.Ldap.ConnectionConfig.model_validate(dict(source))

    @staticmethod
    def pack_entries(
        entries: Sequence[p.Ldif.Entry],
    ) -> Sequence[t.JsonMapping]:
        """Pack flext-ldap entries into Singer-native JSON records.

        Args:
            entries: flext-ldap directory entries to convert.

        Returns:
            The resulting ``Sequence[t.JsonMapping]``.

        """
        records: list[t.JsonMapping] = []
        for entry in entries:
            dn_value: t.JsonValue = entry.dn_str
            attributes = entry.attributes_dict
            record: t.JsonDict = {"dn": dn_value}
            for key, value in attributes.items():
                multiple: t.JsonValueList = list(value)
                record[key] = value[0] if len(value) == 1 else multiple
            records.append(record)
        return records


__all__: list[str] = ["FlextTapLdapUtilitiesExtractSupport"]
