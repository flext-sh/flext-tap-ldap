"""Tap LDAP utility facade."""

from __future__ import annotations

import importlib
import sys
from collections.abc import Mapping, MutableSequence, Sequence
from typing import TYPE_CHECKING

from flext_cli import cli, p as cli_p
from flext_ldap import FlextLdapUtilities
from flext_meltano import u
from flext_tap_ldap import m, p, r, t
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
        """Run the Singer-compatible command through the flext-cli boundary."""
        execute_result = cli.execute_external_command(
            FlextTapLdapUtilities.build_cli_command(),
            prog_name="tap-ldap",
            args=sys.argv[1:],
        )
        if execute_result.failure:
            logger = FlextTapLdapUtilities.fetch_logger("flext_tap_ldap.tap")
            logger.error(
                "tap-ldap command failed",
                error=execute_result.error or "",
            )
            cli.exit(1)

    @staticmethod
    def build_cli_command() -> cli_p.Cli.ExternalCommand:
        """Build the Singer-compatible root command through flext-cli."""
        app = cli.create_group(
            name="tap-ldap", help_text="Singer-compatible LDAP extraction"
        )
        cli.register_result_callback(
            app,
            model_cls=m.TapLdap.CliRequest,
            handler=FlextTapLdapUtilities._execute_cli,
        )
        return cli.external_command(app)

    @staticmethod
    def _execute_cli(params: m.TapLdap.CliRequest) -> p.Result[bool]:
        """Execute one validated Singer-compatible LDAP request."""
        tap_module = importlib.import_module("flext_tap_ldap.tap")
        tap_class: type[FlextTapLdapTap] = tap_module.FlextTapLdapTap
        raw_config: t.JsonMapping = t.json_mapping_adapter().validate_json(
            FlextTapLdapUtilities.Cli.files_read_text(params.config_path).unwrap()
        )
        config_data: t.MutableConfigurationMapping = {
            key: value
            for key, value in raw_config.items()
            if isinstance(value, t.PRIMITIVES_TYPES)
        }
        connection_config_payload = t.json_mapping_adapter().validate_python(
            config_data
        )
        tap = tap_class()
        tap.tap_config = config_data

        source_config = m.Meltano.DataSourceConfig(
            source_type="ldap",
            connection_config=connection_config_payload,
            stream_config={},
            source_version="latest",
        )
        result = tap.discover_streams(tap_instance=source_config)
        if result.failure:
            return r[bool].fail(result.error or "LDAP stream discovery failed")
        if not result.value:
            return r[bool].fail("LDAP stream discovery returned no catalog")

        if params.discover:
            catalog = result.value
            raw_streams = catalog.get("streams", [])
            catalog_streams: MutableSequence[t.JsonMapping] = []
            if isinstance(raw_streams, Sequence):
                for stream_item in raw_streams:
                    if isinstance(stream_item, Mapping):
                        catalog_streams.append(
                            t.json_mapping_adapter().validate_python(stream_item)
                        )
            raw_custom = raw_config.get("custom_streams")
            if isinstance(raw_custom, list):
                for custom_item in raw_custom:
                    custom_stream = tap_class.validate_custom_stream(custom_item)
                    if custom_stream is None:
                        continue
                    entry_result = u.Meltano.build_catalog_entry(
                        stream_name=custom_stream["name"],
                        schema={},
                        key_properties=(),
                    )
                    if entry_result.failure:
                        return r[bool].fail(
                            entry_result.error
                            or "Failed to build custom Singer catalog entry"
                        )
                    catalog_streams.append(
                        t.json_mapping_adapter().validate_python(
                            entry_result.value.model_dump(
                                by_alias=True,
                                exclude_defaults=True,
                                exclude_none=True,
                                mode="json",
                            )
                        )
                    )
            output_catalog = t.json_mapping_adapter().validate_python({
                "streams": catalog_streams
            })
            cli.emit_stdout(t.json_mapping_adapter().dump_json(output_catalog).decode())
            return r[bool].ok(True)

        if params.catalog_path is not None:
            _ = t.json_mapping_adapter().validate_json(
                FlextTapLdapUtilities.Cli.files_read_text(params.catalog_path).unwrap()
            )
        if params.state_path is not None:
            _ = t.json_mapping_adapter().validate_json(
                FlextTapLdapUtilities.Cli.files_read_text(params.state_path).unwrap()
            )

        raw_streams = result.value.get("streams", [])
        stream_entries: MutableSequence[t.JsonMapping] = []
        if isinstance(raw_streams, Sequence):
            stream_entries.extend(
                t.json_mapping_adapter().validate_python(stream_item)
                for stream_item in raw_streams
                if isinstance(stream_item, Mapping)
            )
        for stream_entry in stream_entries:
            schema_message = t.json_mapping_adapter().validate_python({
                "type": "SCHEMA",
                "stream": stream_entry["stream"],
                "schema": stream_entry.get("schema", {}),
                "key_properties": ["dn"],
            })
            cli.emit_stdout(t.json_mapping_adapter().dump_json(schema_message).decode())
        return r[bool].ok(True)


u = FlextTapLdapUtilities

__all__: list[str] = ["FlextTapLdapUtilities", "u"]
