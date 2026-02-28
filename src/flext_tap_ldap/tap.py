"""FlextTapLdapTap - Singer tap for LDAP data extraction using FLEXT patterns.

Consolidates tap functionality and client integration with Singer protocol compliance.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping
from typing import ClassVar, override

from flext_core import FlextLogger
from flext_meltano import FlextMeltanoStream as Stream, FlextMeltanoTap as Tap
from pydantic import ConfigDict, TypeAdapter, ValidationError

from flext_tap_ldap.constants import c
from flext_tap_ldap.ldif_streams import FlextTapLdapLdifStreams
from flext_tap_ldap.settings import FlextTapLdapSettings
from flext_tap_ldap.streams import FlextTapLdapStreams
from flext_tap_ldap.typings import t

logger = FlextLogger(__name__)

_LIST_ADAPTER = TypeAdapter(list[t.GeneralValueType], config=ConfigDict(strict=True))
_MAP_ADAPTER = TypeAdapter(
    dict[str, t.GeneralValueType],
    config=ConfigDict(strict=True),
)
_STR_ADAPTER = TypeAdapter(str, config=ConfigDict(strict=True))


def _as_list(value: t.GeneralValueType) -> list[t.GeneralValueType] | None:
    try:
        return _LIST_ADAPTER.validate_python(value)
    except ValidationError:
        return None


def _as_map(value: t.GeneralValueType) -> Mapping[str, t.GeneralValueType] | None:
    try:
        return _MAP_ADAPTER.validate_python(value)
    except ValidationError:
        return None


def _as_str(value: t.GeneralValueType) -> str | None:
    try:
        return _STR_ADAPTER.validate_python(value)
    except ValidationError:
        return None


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
            # Tap-specific properties
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

    @override
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
        custom_streams_list = _as_list(raw_custom) or []
        for custom_config_raw in custom_streams_list:
            custom_config = _as_map(custom_config_raw)
            if custom_config is None:
                continue
            raw_name = custom_config.get("name", "")
            raw_filter = custom_config.get("search_filter", "")
            schema_dict = _as_map(custom_config.get("schema", {})) or {}
            schema_props = _as_map(schema_dict.get("properties", {})) or {}
            raw_pk = custom_config.get("primary_keys")
            raw_rk = custom_config.get("replication_key")

            raw_pk_values = _as_list(raw_pk)
            primary_keys = (
                [_as_str(k) or "" for k in raw_pk_values]
                if raw_pk_values is not None
                else None
            )

            params = FlextTapLdapStreams.CustomStreamParams(
                name=_as_str(raw_name) or "",
                search_filter=_as_str(raw_filter) or "",
                schema_properties={str(k): v for k, v in schema_props.items()},
                primary_keys=primary_keys,
                replication_key=_as_str(raw_rk),
            )
            stream = FlextTapLdapStreams.CustomStream(tap=self, params=params)
            streams.append(stream)

        return streams


CLI_COMMAND: t.GeneralValueType = getattr(FlextTapLdapTap, "cli")


def main() -> None:
    """Run the main entry point for the tap."""
    if callable(CLI_COMMAND):
        CLI_COMMAND()


if __name__ == "__main__":
    main()
