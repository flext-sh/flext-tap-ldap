"""tap-ldap main tap class using FLEXT centralized conventions.

This module implements the main tap class for LDAP data extraction
using the centralized patterns from flext-core.meltano.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import ClassVar

from flext_core import FlextLogger

# Use FLEXT Meltano wrappers instead of direct singer_sdk imports (domain separation)
from flext_meltano import FlextMeltanoStream as Stream, FlextMeltanoTap as Tap

from flext_tap_ldap.config import FlextTapLdapConfig
from flext_tap_ldap.ldif_stream import LDIFAnalysisStream, LDIFStream
from flext_tap_ldap.streams import (
    CustomStream,
    CustomStreamParams,
    GroupsStream,
    OrganizationalUnitsStream,
    SchemaStream,
    UsersStream,
)
from flext_tap_ldap.typings import FlextMeltanoTapLdapTypes

logger = FlextLogger(__name__)


class FlextMeltanoTapLDAP(Tap):
    """Singer tap for LDAP data extraction using FLEXT centralized patterns."""

    name: str = "tap-ldap"
    config_class = FlextTapLdapConfig

    # NOTE(@flext-team): Use centralized LDAP schema when flext-meltano common_schemas is available
    # Issue: https://github.com/flext-team/flext-meltano/issues/1
    config_jsonschema: ClassVar[FlextMeltanoTapLdapTypes.Core.Dict] = {
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
                "default": "False",
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
                "default": "False",
                "description": "Enable LDIF processing streams",
            },
            "migration_batch": {
                "type": "string",
                "description": "Migration batch identifier for tracking",
            },
        },
    }

    def discover_streams(self: object) -> list[Stream]:
        """Discover available streams."""
        streams: list[Stream] = []

        # Standard LDAP streams (always available)
        streams.extend(
            [
                UsersStream(self),
                GroupsStream(self),
                OrganizationalUnitsStream(self),
                SchemaStream(self),
            ],
        )

        # Add LDIF streams if enabled
        if self.config.get("enable_ldif_streams", False):
            streams.extend(
                [
                    LDIFStream(self),
                    LDIFAnalysisStream(self),
                ],
            )

        # Add custom streams if configured:
        custom_streams_config: dict[str, object] = self.config.get("custom_streams", [])
        for custom_config in custom_streams_config:
            params = CustomStreamParams(
                name=custom_config["name"],
                search_filter=custom_config["search_filter"],
                schema_properties=custom_config.get("schema", {}).get("properties", {}),
                primary_keys=custom_config.get("primary_keys"),
                replication_key=custom_config.get("replication_key"),
            )
            stream = CustomStream(tap=self, params=params)
            streams.append(stream)

        return streams


def main() -> None:
    """Run the main entry point for the tap."""
    FlextMeltanoTapLDAP.cli()


if __name__ == "__main__":
    main()
