"""Tap LDAP utility facade."""

from __future__ import annotations

import importlib
from collections.abc import Mapping, MutableSequence, Sequence
from pathlib import Path
from typing import TYPE_CHECKING

import click

from flext_ldap import FlextLdapUtilities
from flext_meltano import u
from flext_tap_ldap import m, t
from flext_tap_ldap._utilities._processor import FlextTapLdapUtilitiesProcessorMixin
from flext_tap_ldap._utilities.client_support import (
    FlextTapLdapUtilitiesClientSupport,
)
from flext_tap_ldap._utilities.error_handling import (
    FlextTapLdapUtilitiesErrorHandling,
)

if TYPE_CHECKING:
    from flext_tap_ldap.tap import FlextTapLdapTap


class FlextTapLdapUtilities(
    FlextTapLdapUtilitiesProcessorMixin,
    FlextTapLdapUtilitiesClientSupport,
    FlextTapLdapUtilitiesErrorHandling,
    u,
    FlextLdapUtilities,
):
    """Unified LDAP tap utility facade."""

    class TapLdap(
        FlextTapLdapUtilitiesProcessorMixin.TapLdap,
        FlextTapLdapUtilitiesClientSupport,
        FlextTapLdapUtilitiesErrorHandling,
    ):
        """Tap LDAP namespace for cross-project access."""

    @staticmethod
    def main() -> None:
        """Run the main entry point for the FlextMeltanoTapAbstractions."""
        tap_module = importlib.import_module("flext_tap_ldap.tap")
        tap_class: type[FlextTapLdapTap] = tap_module.FlextTapLdapTap
        execute_result = tap_class().execute()
        if execute_result.failure:
            logger = FlextTapLdapUtilities.fetch_logger("flext_tap_ldap.tap")
            logger.error(
                "FlextMeltanoTapAbstractions execution failed",
                error=execute_result.error or "",
            )

    @staticmethod
    def build_cli_command() -> click.Command:
        """Build the Singer-compatible Click CLI command for tap-ldap."""
        tap_module = importlib.import_module("flext_tap_ldap.tap")
        tap_class: type[FlextTapLdapTap] = tap_module.FlextTapLdapTap

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
        @click.option(
            "--state",
            "state_path",
            type=click.Path(exists=True),
            default=None,
        )
        def _cli(
            config_path: str,
            *,
            discover: bool,
            catalog_path: str | None,
            state_path: str | None,
        ) -> None:
            """Singer-compatible CLI for LDAP data extraction."""
            raw_config: t.JsonMapping = t.json_mapping_adapter().validate_json(
                FlextTapLdapUtilities.Cli.files_read_text(Path(config_path)).unwrap(),
            )
            config_data: t.MutableConfigurationMapping = {
                k: v for k, v in raw_config.items() if isinstance(v, t.PRIMITIVES_TYPES)
            }
            connection_config_payload: t.JsonMapping = (
                t.json_mapping_adapter().validate_python(
                    config_data,
                )
            )
            tap = tap_class()
            tap.tap_config = config_data

            if discover:
                source_config = m.Meltano.DataSourceConfig(
                    source_type="ldap",
                    connection_config=connection_config_payload,
                    stream_config={},
                    source_version="latest",
                )
                result = tap.discover_streams(tap_instance=source_config)
                if result.success and result.value:
                    catalog = result.value
                    raw_streams = catalog.get("streams", [])
                    catalog_streams: MutableSequence[t.JsonMapping] = []
                    if isinstance(raw_streams, Sequence):
                        for rs_item in raw_streams:
                            if isinstance(rs_item, Mapping):
                                catalog_streams.append(
                                    t.json_mapping_adapter().validate_python(rs_item),
                                )
                    raw_custom: t.JsonValue = raw_config.get("custom_streams")
                    if isinstance(raw_custom, list):
                        for cs_item in raw_custom:
                            cs_dict = tap_class.validate_custom_stream(cs_item)
                            if cs_dict is not None:
                                entry_result = u.Meltano.build_catalog_entry(
                                    stream_name=cs_dict["name"],
                                    schema={},
                                    key_properties=(),
                                )
                                if entry_result.failure:
                                    raise click.ClickException(
                                        entry_result.error
                                        or "Failed to build custom Singer catalog entry",
                                    )
                                cs_entry = entry_result.value
                                catalog_streams.append(
                                    t.json_mapping_adapter().validate_python(
                                        cs_entry.model_dump(
                                            by_alias=True,
                                            exclude_defaults=True,
                                            exclude_none=True,
                                            mode="json",
                                        ),
                                    ),
                                )
                    output_catalog: t.JsonMapping = (
                        t.json_mapping_adapter().validate_python({
                            "streams": catalog_streams,
                        })
                    )
                    click.echo(
                        t.json_mapping_adapter().dump_json(output_catalog).decode(),
                    )
                return

            if catalog_path:
                t.json_mapping_adapter().validate_json(
                    FlextTapLdapUtilities.Cli.files_read_text(
                        Path(catalog_path),
                    ).unwrap(),
                )

            if state_path:
                t.json_mapping_adapter().validate_json(
                    FlextTapLdapUtilities.Cli.files_read_text(
                        Path(state_path),
                    ).unwrap(),
                )

            source_config = m.Meltano.DataSourceConfig(
                source_type="ldap",
                connection_config=connection_config_payload,
                stream_config={},
                source_version="latest",
            )
            result = tap.discover_streams(tap_instance=source_config)
            if result.success and result.value:
                raw_streams_val = result.value.get("streams", [])
                stream_entries: MutableSequence[t.JsonMapping] = []
                if isinstance(raw_streams_val, Sequence):
                    stream_entries.extend(
                        t.json_mapping_adapter().validate_python(se_item)
                        for se_item in raw_streams_val
                        if isinstance(se_item, Mapping)
                    )
                for stream_entry in stream_entries:
                    schema_msg: t.JsonMapping = (
                        t.json_mapping_adapter().validate_python({
                            "type": "SCHEMA",
                            "stream": stream_entry["stream"],
                            "schema": stream_entry.get("schema", {}),
                            "key_properties": ["dn"],
                        })
                    )
                    click.echo(t.json_mapping_adapter().dump_json(schema_msg).decode())

        return _cli


u = FlextTapLdapUtilities

__all__: list[str] = ["FlextTapLdapUtilities", "u"]
