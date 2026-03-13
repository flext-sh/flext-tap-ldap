"""FlextTapLdapTap - Singer tap for LDAP data extraction using FLEXT patterns.

Consolidates tap functionality and client integration with Singer protocol compliance.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import ClassVar, override

from flext_core import FlextLogger, r
from flext_meltano import FlextMeltanoTapAbstractions as Tap, m
from pydantic import ConfigDict, TypeAdapter, ValidationError

from flext_tap_ldap.constants import c
from flext_tap_ldap.ldif_streams import FlextTapLdapLdifStreams
from flext_tap_ldap.settings import FlextTapLdapSettings
from flext_tap_ldap.streams import FlextTapLdapStreams
from flext_tap_ldap.typings import t

logger = FlextLogger(__name__)
_CONFIG_MAP_ADAPTER = TypeAdapter(dict[str, object], config=ConfigDict(strict=False))

type TapLdapStream = (
    FlextTapLdapStreams.LDAPBaseStream
    | FlextTapLdapLdifStreams.LdifStream
    | FlextTapLdapLdifStreams.LdifAnalysisStream
)


class FlextTapLdapTap(Tap):
    """Singer tap for LDAP data extraction using FLEXT centralized patterns.

    Consolidates main tap class, stream discovery, and client integration
    into single unified class following FlextTapLdap[Module] pattern.
    """

    name: ClassVar[str] = "tap-ldap"
    config_class: ClassVar[type[FlextTapLdapSettings]] = FlextTapLdapSettings
    config_jsonschema: ClassVar[dict[str, object]] = {
        "type": "object",
        "properties": {
            "host": {"type": "string", "description": "LDAP server host"},
            "port": {
                "type": "integer",
                "default": c.TapLdap.DEFAULT_PORT,
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
        source_config: m.Meltano.DataSourceConfig
        | m.Meltano.TapConfig
        | m.Meltano.TapInstance,
    ) -> r[t.Meltano.Singer.StreamCatalog]:
        """Discover available streams.

        Discovers standard LDAP streams (users, groups, organizational units, schema)
        and optionally LDIF processing streams and custom streams based on configuration.
        """
        source_payload = source_config.model_dump(mode="python")
        raw_connection_config = source_payload.get("connection_config", {})
        config_map: dict[str, object]
        try:
            config_map = _CONFIG_MAP_ADAPTER.validate_python(raw_connection_config)
        except ValidationError:
            config_map = {}

        streams: list[TapLdapStream] = [
            FlextTapLdapStreams.UsersStream(self),
            FlextTapLdapStreams.GroupsStream(self),
            FlextTapLdapStreams.OrganizationalUnitsStream(self),
            FlextTapLdapStreams.SchemaStream(self),
        ]
        if bool(config_map.get("enable_ldif_streams", False)):
            streams.extend([
                FlextTapLdapLdifStreams.LdifStream(self),
                FlextTapLdapLdifStreams.LdifAnalysisStream(self),
            ])

        catalog: t.Meltano.Singer.StreamCatalog = {
            "streams": [
                {
                    "stream": stream.name,
                    "schema": {},
                }
                for stream in streams
            ]
        }
        return r[t.Meltano.Singer.StreamCatalog].ok(catalog)


def main() -> None:
    """Run the main entry point for the tap."""
    execute_result = FlextTapLdapTap().execute()
    if execute_result.is_failure:
        logger.error("Tap execution failed", error=execute_result.error or "")


if __name__ == "__main__":
    main()
