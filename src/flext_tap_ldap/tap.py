"""FlextTapLdapTap - Singer FlextMeltanoTapAbstractions for LDAP data extraction using FLEXT patterns.

Consolidates FlextMeltanoTapAbstractions functionality and client integration with Singer protocol compliance.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import ClassVar

import click
from flext_core import FlextLogger, r
from flext_meltano import FlextMeltanoAbstractions
from pydantic import ConfigDict, TypeAdapter, ValidationError

from flext_tap_ldap.constants import FlextTapLdapConstants as c
from flext_tap_ldap.ldif_streams import FlextTapLdapLdifStreams
from flext_tap_ldap.models import FlextTapLdapModels as m
from flext_tap_ldap.settings import FlextTapLdapSettings
from flext_tap_ldap.streams import FlextTapLdapStreams
from flext_tap_ldap.typings import FlextTapLdapTypes as t

logger = FlextLogger(__name__)
_CONFIG_MAP_ADAPTER = TypeAdapter(
    dict[str, Mapping[str, object]],
    config=ConfigDict(strict=False),
)

type TapLdapStream = (
    FlextTapLdapStreams.LDAPBaseStream
    | FlextTapLdapLdifStreams.LdifStream
    | FlextTapLdapLdifStreams.LdifAnalysisStream
)


class FlextTapLdapTap(FlextMeltanoAbstractions):
    """Singer FlextMeltanoTapAbstractions for LDAP data extraction using FLEXT centralized patterns.

    Consolidates main FlextMeltanoTapAbstractions class, stream discovery, and client integration
    into single unified class following FlextTapLdap[Module] pattern.
    """

    name: ClassVar[str] = "FlextMeltanoTapAbstractions-ldap"
    config: dict[str, t.Scalar]

    def __init__(self) -> None:
        self.config = {}
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
        config_map: dict[str, Mapping[str, object]]
        try:
            config_map = _CONFIG_MAP_ADAPTER.validate_python(raw_connection_config)
        except ValidationError:
            config_map = {}

        ldap_streams: list[FlextTapLdapStreams.LDAPBaseStream] = [
            FlextTapLdapStreams.UsersStream(self),
            FlextTapLdapStreams.GroupsStream(self),
            FlextTapLdapStreams.OrganizationalUnitsStream(self),
            FlextTapLdapStreams.SchemaStream(self),
        ]
        streams: list[TapLdapStream] = list(ldap_streams)
        if bool(config_map.get("enable_ldif_streams", False)):
            ldif_stream_list: list[TapLdapStream] = [
                FlextTapLdapLdifStreams.LdifStream(self),
                FlextTapLdapLdifStreams.LdifAnalysisStream(self),
            ]
            streams.extend(ldif_stream_list)

        streams_list: list[t.Meltano.Singer.CatalogEntry] = [
            {
                "stream": str(stream.name),
                "tap_stream_id": str(stream.name),
                "schema": {},
            }
            for stream in streams
        ]
        stream_catalog: t.Meltano.Singer.StreamCatalog = {"streams": streams_list}
        return r[t.Meltano.Singer.StreamCatalog].ok(stream_catalog)

    def execute(self) -> r[bool]:
        """Execute the tap. Delegates to parent if available, otherwise returns success."""
        if hasattr(super(), "execute"):
            return super().execute()  # type: ignore[no-any-return]
        return r[bool].ok(True)


def main() -> None:
    """Run the main entry point for the FlextMeltanoTapAbstractions."""
    execute_result = FlextTapLdapTap().execute()
    if execute_result.is_failure:
        logger.error(
            "FlextMeltanoTapAbstractions execution failed",
            error=execute_result.error or "",
        )


def _build_cli_command() -> click.Command:
    """Build the Singer-compatible Click CLI command for tap-ldap."""

    @click.command("tap-ldap")
    @click.option(
        "--config", "config_path", type=click.Path(exists=True), required=True
    )
    @click.option("--discover", is_flag=True, default=False)
    @click.option(
        "--catalog", "catalog_path", type=click.Path(exists=True), default=None
    )
    @click.option("--state", "state_path", type=click.Path(exists=True), default=None)
    def _cli(
        config_path: str,
        *,
        discover: bool,
        catalog_path: str | None,
        state_path: str | None,
    ) -> None:
        """Singer-compatible CLI for LDAP data extraction."""
        raw_config: dict[str, object] = json.loads(
            Path(config_path).read_text(encoding="utf-8")
        )
        config_data: dict[str, t.Scalar] = {
            k: v
            for k, v in raw_config.items()
            if isinstance(v, (str, int, float, bool))
        }
        tap = FlextTapLdapTap()
        tap.config = config_data

        if discover:
            source_config = m.Meltano.DataSourceConfig(
                source_type="ldap",
                connection_config=dict(config_data),
                stream_config={},
                source_version="latest",
            )
            result = tap.discover_streams(source_config=source_config)
            if result.is_success and result.value:
                catalog = result.value
                raw_custom: object = raw_config.get("custom_streams")
                if isinstance(raw_custom, list):
                    custom_list: list[object] = list(raw_custom)
                    for cs_item in custom_list:
                        if isinstance(cs_item, dict):
                            cs_dict: dict[str, object] = {
                                str(k): v for k, v in cs_item.items()
                            }
                            if "name" in cs_dict:
                                cs_entry: t.Meltano.Singer.CatalogEntry = {
                                    "stream": str(cs_dict["name"]),
                                    "tap_stream_id": str(cs_dict["name"]),
                                    "schema": {},
                                }
                                catalog["streams"].append(cs_entry)
                click.echo(json.dumps(catalog))
            return

        if catalog_path:
            json.loads(Path(catalog_path).read_text(encoding="utf-8"))

        if state_path:
            json.loads(Path(state_path).read_text(encoding="utf-8"))

        source_config = m.Meltano.DataSourceConfig(
            source_type="ldap",
            connection_config=config_data,
            stream_config={},
            source_version="latest",
        )
        result = tap.discover_streams(source_config=source_config)
        if result.is_success and result.value:
            for stream_entry in result.value.get("streams", []):
                schema_msg = {
                    "type": "SCHEMA",
                    "stream": stream_entry["stream"],
                    "schema": stream_entry.get("schema", {}),
                    "key_properties": ["dn"],
                }
                click.echo(json.dumps(schema_msg))

    return _cli


CLI_COMMAND: click.Command = _build_cli_command()


if __name__ == "__main__":
    main()
