"""FlextTapLdapTap - Singer FlextMeltanoTapAbstractions for LDAP data extraction using FLEXT patterns.

Consolidates FlextMeltanoTapAbstractions functionality and client integration with Singer protocol compliance.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import MutableSequence
from typing import ClassVar, override

from flext_meltano.services.abstractions import FlextMeltanoAbstractions
from flext_tap_ldap import c, m, p, r, t, u
from flext_tap_ldap.ldif_streams import FlextTapLdapLdifStreams
from flext_tap_ldap.settings import FlextTapLdapSettings
from flext_tap_ldap.streams import FlextTapLdapStreams


class FlextTapLdapTap(FlextMeltanoAbstractions):
    """Singer FlextMeltanoTapAbstractions for LDAP data extraction using FLEXT centralized patterns.

    Consolidates main FlextMeltanoTapAbstractions class, stream discovery, and client integration
    into single unified class following FlextTapLdap[Module] pattern.
    """

    name: ClassVar[str] = "FlextMeltanoTapAbstractions-ldap"

    _tap_config: t.MutableConfigurationMapping

    def __init__(self) -> None:
        """Initialize tap with empty settings."""
        self._tap_config = {}

    @property
    def tap_config(self) -> t.MutableConfigurationMapping:
        """The mutable tap configuration mapping."""
        return self._tap_config

    @tap_config.setter
    def tap_config(self, value: t.MutableConfigurationMapping) -> None:
        """Set mutable tap configuration mapping."""
        self._tap_config = value

    config_class: ClassVar[type[FlextTapLdapSettings]] = FlextTapLdapSettings
    config_jsonschema: ClassVar[t.JsonValue] = {
        "type": "object",
        "properties": {
            "host": {"type": "string", "description": "LDAP server host"},
            "port": {
                "type": "integer",
                "default": c.Ldap.PORT,
                "description": "LDAP server port",
            },
            "bind_dn": {"type": "string", "description": "Bind DN for authentication"},
            "password": {
                "type": "string",
                "description": "Password for authentication",
            },
            "base_dn": {"type": "string", "description": "Base DN for searches"},
            "use_ssl": {
                "type": "boolean",
                "default": False,
                "description": "Use SSL connection",
            },
            "page_size": {
                "type": "integer",
                "default": c.TapLdap.DEFAULT_PAGE_SIZE,
                "description": "Page size for paged results",
            },
            "user_filter": {
                "type": "string",
                "default": "(objectClass=inetOrgPerson)",
                "description": "LDAP filter for user entries",
            },
            "group_filter": {
                "type": "string",
                "default": "(objectClass=groupOfNames)",
                "description": "LDAP filter for group entries",
            },
            "ldif_files": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of LDIF files to process",
            },
            "ldif_directory": {
                "type": "string",
                "description": "Directory containing LDIF files",
            },
            "enable_ldif_streams": {
                "type": "boolean",
                "default": False,
                "description": "Enable LDIF processing streams",
            },
            "migration_batch": {
                "type": "string",
                "description": "Migration batch identifier for tracking",
            },
        },
    }

    @override
    def discover_streams(
        self,
        tap_instance: m.Meltano.DataSourceConfig
        | m.Meltano.TapConfig
        | m.Meltano.TapInstance,
    ) -> p.Result[t.JsonMapping]:
        """Discover available streams.

        Discovers standard LDAP streams (users, groups, organizational units, schema)
        and optionally LDIF processing streams and custom streams based on configuration.
        """
        source_payload = tap_instance.model_dump(mode="python")
        raw_connection_config = source_payload.get("connection_config", {})
        config_map: t.MappingKV[str, t.JsonMapping] | t.ConfigurationMapping
        try:
            config_map = t.json_mapping_by_str_adapter().validate_python(
                raw_connection_config,
            )
        except c.ValidationError:
            config_map = {}

        ldap_streams: MutableSequence[FlextTapLdapStreams.LDAPBaseStream] = [
            FlextTapLdapStreams.UsersStream(self),
            FlextTapLdapStreams.GroupsStream(self),
            FlextTapLdapStreams.OrganizationalUnitsStream(self),
            FlextTapLdapStreams.SchemaStream(self),
        ]
        streams: MutableSequence[
            FlextTapLdapStreams.LDAPBaseStream
            | FlextTapLdapLdifStreams.LdifStream
            | FlextTapLdapLdifStreams.LdifAnalysisStream
        ] = list(ldap_streams)
        if bool(config_map.get("enable_ldif_streams", False)):
            ldif_stream_list: MutableSequence[
                FlextTapLdapLdifStreams.LdifStream
                | FlextTapLdapLdifStreams.LdifAnalysisStream
            ] = [
                FlextTapLdapLdifStreams.LdifStream(self),
                FlextTapLdapLdifStreams.LdifAnalysisStream(self),
            ]
            streams.extend(ldif_stream_list)

        streams_list: MutableSequence[m.Meltano.SingerCatalogEntry] = []
        for stream in streams:
            entry_result = u.Meltano.build_catalog_entry(
                stream_name=str(stream.name),
                schema={},
                key_properties=(),
            )
            if entry_result.failure:
                return r[t.JsonMapping].fail(  # type: ignore[no-any-return]
                    entry_result.error or "Failed to build LDAP Singer catalog entry",
                )
            streams_list.append(entry_result.value)
        stream_catalog: t.JsonMapping = t.json_mapping_adapter().validate_python(
            m.Meltano.SingerCatalog(streams=streams_list).model_dump(
                by_alias=True,
                exclude_defaults=True,
                exclude_none=True,
                mode="json",
            ),
        )
        stream_catalog_payload: t.JsonMapping = (
            t.json_mapping_adapter().validate_python(
                {"streams": stream_catalog.get("streams", [])},
            )
        )
        return r[t.JsonMapping].ok(stream_catalog_payload)  # type: ignore[no-any-return]

    @override
    def execute(self) -> p.Result[t.JsonMapping]:
        """Execute the tap and return execution state with stream discovery results."""
        discover_result = self.discover_streams(
            m.Meltano.TapConfig.model_validate({
                "name": self.name,
                "tap_type": "tap-ldap",
                "connection_config": self._tap_config,
            }),
        )
        status = (
            c.Meltano.StreamStatus.COMPLETED
            if discover_result.success
            else c.Meltano.StreamStatus.FAILED
        )
        return r[t.JsonMapping].ok({  # type: ignore[no-any-return]
            "status": status,
            "tap_name": self.name,
            "streams_discovered": discover_result.success,
        })

    @staticmethod
    def validate_custom_stream(raw_item: t.JsonValue) -> t.StrMapping | None:
        """Validate a custom stream definition, returning name if valid."""
        try:
            validated: t.JsonMapping = t.json_mapping_adapter().validate_python(
                raw_item,
            )
        except c.ValidationError as exc:
            u.fetch_logger(__name__).warning(
                "Invalid custom stream definition ignored: %s",
                exc,
            )
            return None
        name_val: t.JsonValue = validated.get("name")
        if isinstance(name_val, str) and name_val:
            return {"name": name_val}
        return None


if __name__ == "__main__":
    u.main()
