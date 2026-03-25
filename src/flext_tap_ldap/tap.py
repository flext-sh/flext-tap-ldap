"""FlextTapLdapTap - Singer FlextMeltanoTapAbstractions for LDAP data extraction using FLEXT patterns.

Consolidates FlextMeltanoTapAbstractions functionality and client integration with Singer protocol compliance.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping, MutableSequence, Sequence
from pathlib import Path
from typing import ClassVar

import click
from flext_core import FlextLogger, r
from flext_meltano import FlextMeltanoAbstractions
from pydantic import ConfigDict, TypeAdapter, ValidationError

from flext_tap_ldap.constants import c
from flext_tap_ldap.ldif_streams import FlextTapLdapLdifStreams
from flext_tap_ldap.models import m
from flext_tap_ldap.settings import FlextTapLdapSettings
from flext_tap_ldap.streams import FlextTapLdapStreams
from flext_tap_ldap.typings import t

logger = FlextLogger(__name__)
_SINGER_OUTPUT_ADAPTER: TypeAdapter[t.ContainerMapping] = TypeAdapter(
    t.ContainerMapping,
    config=ConfigDict(strict=False),
)
_CUSTOM_STREAM_ADAPTER: TypeAdapter[t.ContainerMapping] = TypeAdapter(
    t.ContainerMapping,
    config=ConfigDict(strict=False),
)


class FlextTapLdapTap(FlextMeltanoAbstractions):
    """Singer FlextMeltanoTapAbstractions for LDAP data extraction using FLEXT centralized patterns.

    Consolidates main FlextMeltanoTapAbstractions class, stream discovery, and client integration
    into single unified class following FlextTapLdap[Module] pattern.
    """

    name: ClassVar[str] = "FlextMeltanoTapAbstractions-ldap"
    _config_map_adapter: ClassVar[TypeAdapter[Mapping[str, t.ContainerMapping]]] = (
        TypeAdapter(Mapping[str, t.ContainerMapping], config=ConfigDict(strict=False))
    )
    config: t.MutableConfigurationMapping

    def __init__(self) -> None:
        """Initialize tap with empty config."""
        self.config: t.MutableConfigurationMapping = {}

    config_class: ClassVar[type[FlextTapLdapSettings]] = FlextTapLdapSettings
    config_jsonschema: ClassVar[t.ContainerMapping] = {
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
    ) -> r[t.ContainerMapping]:
        """Discover available streams.

        Discovers standard LDAP streams (users, groups, organizational units, schema)
        and optionally LDIF processing streams and custom streams based on configuration.
        """
        source_payload = source_config.model_dump(mode="python")
        raw_connection_config = source_payload.get("connection_config", {})
        config_map: Mapping[str, t.ContainerMapping] | t.ConfigurationMapping
        try:
            config_map = FlextTapLdapTap._config_map_adapter.validate_python(
                raw_connection_config,
            )
        except ValidationError:
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

        streams_list: MutableSequence[t.Meltano.Singer.CatalogEntry] = [
            {
                "stream": str(stream.name),
                "tap_stream_id": str(stream.name),
                "schema": {},
            }
            for stream in streams
        ]
        stream_catalog: t.Meltano.Singer.StreamCatalog = {"streams": streams_list}
        return r[t.ContainerMapping].ok(stream_catalog)

    def execute(self) -> r[t.ContainerMapping]:
        """Execute the tap. Returns success after stream discovery."""
        return r[t.ContainerMapping].ok({"success": True})

    @staticmethod
    def validate_custom_stream(raw_item: t.NormalizedValue) -> t.StrMapping | None:
        """Validate a custom stream definition, returning name if valid."""
        try:
            validated: t.ContainerMapping = _CUSTOM_STREAM_ADAPTER.validate_python(
                raw_item,
            )
        except ValidationError:
            return None
        name_val: t.NormalizedValue = validated.get("name")
        if isinstance(name_val, str) and name_val:
            return {"name": name_val}
        return None


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
        "--config",
        "config_path",
        type=click.Path(exists=True),
        required=True,
    )
    @click.option("--discover", is_flag=True, default=False)
    @click.option(
        "--catalog",
        "catalog_path",
        type=click.Path(exists=True),
        default=None,
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
        raw_config: t.ContainerMapping = _CUSTOM_STREAM_ADAPTER.validate_json(
            Path(config_path).read_bytes(),
        )
        config_data: t.MutableConfigurationMapping = {
            k: v
            for k, v in raw_config.items()
            if isinstance(v, (str, int, float, bool))
        }
        tap = FlextTapLdapTap()
        tap.config = config_data

        if discover:
            source_config = m.Meltano.DataSourceConfig(
                source_type="ldap",
                connection_config={str(k): v for k, v in config_data.items()},
                stream_config={},
                source_version="latest",
            )
            result = tap.discover_streams(source_config=source_config)
            if result.is_success and result.value:
                catalog = result.value
                raw_streams = catalog.get("streams", [])
                catalog_streams: MutableSequence[Mapping[str, t.NormalizedValue]] = []
                if isinstance(raw_streams, Sequence):
                    for rs_item in raw_streams:
                        if isinstance(rs_item, Mapping):
                            catalog_streams.append(rs_item)
                raw_custom: t.NormalizedValue = raw_config.get("custom_streams")
                if isinstance(raw_custom, list):
                    for cs_item in raw_custom:
                        cs_dict = FlextTapLdapTap.validate_custom_stream(cs_item)
                        if cs_dict is not None:
                            cs_entry: t.Meltano.Singer.CatalogEntry = {
                                "stream": cs_dict["name"],
                                "tap_stream_id": cs_dict["name"],
                                "schema": {},
                            }
                            catalog_streams.append(cs_entry)
                output_catalog: Mapping[str, t.NormalizedValue] = {
                    "streams": catalog_streams,
                }
                click.echo(_SINGER_OUTPUT_ADAPTER.dump_json(output_catalog).decode())
            return

        if catalog_path:
            _SINGER_OUTPUT_ADAPTER.validate_json(Path(catalog_path).read_bytes())

        if state_path:
            _SINGER_OUTPUT_ADAPTER.validate_json(Path(state_path).read_bytes())

        source_config = m.Meltano.DataSourceConfig(
            source_type="ldap",
            connection_config={str(k): v for k, v in config_data.items()},
            stream_config={},
            source_version="latest",
        )
        result = tap.discover_streams(source_config=source_config)
        if result.is_success and result.value:
            raw_streams_val = result.value.get("streams", [])
            stream_entries: list[Mapping[str, t.NormalizedValue]] = []
            if isinstance(raw_streams_val, Sequence):
                for se_item in raw_streams_val:
                    if isinstance(se_item, Mapping):
                        stream_entries.append(se_item)
            for stream_entry in stream_entries:
                schema_msg = {
                    "type": "SCHEMA",
                    "stream": stream_entry["stream"],
                    "schema": stream_entry.get("schema", {}),
                    "key_properties": ["dn"],
                }
                click.echo(_SINGER_OUTPUT_ADAPTER.dump_json(schema_msg).decode())

    return _cli


CLI_COMMAND: click.Command = _build_cli_command()


if __name__ == "__main__":
    main()
