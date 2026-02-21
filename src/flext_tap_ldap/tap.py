"""FlextTapLdapTap - Singer tap for LDAP data extraction using FLEXT patterns.

Consolidates tap functionality and client integration with Singer protocol compliance.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import ClassVar

from flext_core import FlextLogger
from flext_meltano import FlextMeltanoStream as Stream, FlextMeltanoTap as Tap

from flext_tap_ldap.ldif_streams import FlextTapLdapLdifStreams
from flext_tap_ldap.settings import FlextTapLdapSettings
from flext_tap_ldap.streams import FlextTapLdapStreams
from flext_tap_ldap.typings import t

logger = FlextLogger(__name__)


class FlextTapLdapTap(Tap):
    """Singer tap for LDAP data extraction using FLEXT centralized patterns.

    Consolidates main tap class, stream discovery, and client integration
    into single unified class following FlextTapLdap[Module] pattern.
    """

    name: str = "tap-ldap"
    config_class = FlextTapLdapSettings

    # NOTE(@flext-team): Use centralized LDAP schema when flext-meltano common_schemas is available
    # Issue: https://github.com/flext-team/flext-meltano/issues/1
    config_jsonschema: ClassVar[dict[str, t.GeneralValueType]] = {
        "type": "object",
        "properties": {
            # Basic LDAP connection properties
            "host": {"type": "string", "description": "LDAP server host"},
            "port": {
                "type": "integer",
                "default": 389,
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
            # Tap-specific properties
            "page_size": {
                "type": "integer",
                "default": 1000,
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
            # LDIF processing properties
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

    def discover_streams(self) -> list[Stream]:
        """Discover available streams.

        Discovers standard LDAP streams (users, groups, organizational units, schema)
        and optionally LDIF processing streams and custom streams based on configuration.
        """
        streams: list[Stream] = []

        # Standard LDAP streams (always available)
        streams.extend(
            [
                FlextTapLdapStreams.UsersStream(self),
                FlextTapLdapStreams.GroupsStream(self),
                FlextTapLdapStreams.OrganizationalUnitsStream(self),
                FlextTapLdapStreams.SchemaStream(self),
            ],
        )

        # Add LDIF streams if enabled
        if self.config.get("enable_ldif_streams", False):
            streams.extend(
                [
                    FlextTapLdapLdifStreams.LdifStream(self),
                    FlextTapLdapLdifStreams.LdifAnalysisStream(self),
                ],
            )

        # Add custom streams if configured
        raw_custom = self.config.get("custom_streams", [])
        custom_streams_config: list[dict[str, t.GeneralValueType]] = (
            list(raw_custom) if isinstance(raw_custom, list) else []
        )
        for custom_config in custom_streams_config:
            if not isinstance(custom_config, dict):
                continue
            raw_name = custom_config.get("name", "")
            raw_filter = custom_config.get("search_filter", "")
            raw_schema = custom_config.get("schema", {})
            schema_dict = raw_schema if isinstance(raw_schema, dict) else {}
            raw_props = schema_dict.get("properties", {})
            schema_props = raw_props if isinstance(raw_props, dict) else {}
            raw_pk = custom_config.get("primary_keys")
            raw_rk = custom_config.get("replication_key")
            params = FlextTapLdapStreams.CustomStreamParams(
                name=str(raw_name) if isinstance(raw_name, str) else "",
                search_filter=str(raw_filter) if isinstance(raw_filter, str) else "",
                schema_properties=schema_props,
                primary_keys=[str(k) for k in raw_pk]
                if isinstance(raw_pk, list)
                else None,
                replication_key=str(raw_rk) if isinstance(raw_rk, str) else None,
            )
            stream = FlextTapLdapStreams.CustomStream(tap=self, params=params)
            streams.append(stream)

        return streams


def main() -> None:
    """Run the main entry point for the tap."""
    FlextTapLdapTap.cli()


if __name__ == "__main__":
    main()
