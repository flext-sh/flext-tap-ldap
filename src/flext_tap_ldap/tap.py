"""FlextTapLdapTap - Singer tap for LDAP data extraction using FLEXT patterns.

Consolidates tap functionality and client integration with Singer protocol compliance.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import ClassVar

from flext_core import FlextLogger
from flext_meltano import FlextMeltanoStream as Stream, FlextMeltanoTap as Tap

from flext_tap_ldap.config import FlextTapLdapSettings
from flext_tap_ldap.ldif_streams import FlextTapLdapLdifStreams
from flext_tap_ldap.streams import FlextTapLdapStreams

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
    config_jsonschema: ClassVar[dict[str, object]] = {
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
        custom_streams_config: list[dict[str, object]] = self.config.get(
            "custom_streams",
            [],
        )
        for custom_config in custom_streams_config:
            params = FlextTapLdapStreams.CustomStreamParams(
                name=custom_config.get("name", ""),
                search_filter=custom_config.get("search_filter", ""),
                schema_properties=custom_config.get("schema", {}).get("properties", {}),
                primary_keys=custom_config.get("primary_keys"),
                replication_key=custom_config.get("replication_key"),
            )
            stream = FlextTapLdapStreams.CustomStream(tap=self, params=params)
            streams.append(stream)

        return streams


def main() -> None:
    """Run the main entry point for the tap."""
    FlextTapLdapTap.cli()


if __name__ == "__main__":
    main()
