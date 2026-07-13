"""Behavioral integration tests for the tap-ldap Singer CLI contract.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING

import pytest
from click.core import Command
from click.testing import CliRunner

from flext_cli import u as cli_u
from flext_tap_ldap import c
from tests import t, u

if TYPE_CHECKING:
    from pathlib import Path

STANDARD_STREAMS: tuple[str, ...] = (
    "users",
    "groups",
    "organizational_units",
    "schema",
)


def _extract_catalog(output: str) -> t.JsonMapping:
    """Extract the single JSON catalog object emitted on the CLI stdout."""
    for line in output.strip().splitlines():
        stripped = line.strip()
        if stripped.startswith("{"):
            return t.Cli.JSON_MAPPING_ADAPTER.validate_json(stripped)
    msg = f"No JSON catalog found in output: {output[:200]}"
    raise ValueError(msg)


def _stream_ids(catalog: t.JsonMapping) -> list[str]:
    """Return the observable stream identifiers declared in a discovery catalog."""
    streams = t.Cli.JSON_LIST_ADAPTER.validate_python(catalog["streams"])
    ids: list[str] = []
    for raw in streams:
        entry = t.Cli.JSON_MAPPING_ADAPTER.validate_python(raw)
        stream_id = entry.get("tap_stream_id", entry.get("stream"))
        if isinstance(stream_id, str):
            ids.append(stream_id)
    return ids


def _singer_messages(output: str) -> list[t.JsonMapping]:
    """Parse the newline-delimited Singer messages emitted on stdout."""
    messages: list[t.JsonMapping] = []
    for line in output.strip().splitlines():
        if not line.strip():
            continue
        parsed_result = cli_u.Cli.json_loads(line)
        if parsed_result.failure:
            continue
        parsed = parsed_result.unwrap()
        if isinstance(parsed, Mapping):
            messages.append(t.Cli.JSON_MAPPING_ADAPTER.validate_python(parsed))
    return messages


class TestsFlextTapLdapIntegration:
    """Observable-contract tests for the tap-ldap Singer CLI command."""

    @staticmethod
    def _command() -> Command:
        assert isinstance(c.TapLdap.CLI_COMMAND, Command)
        return c.TapLdap.CLI_COMMAND

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Provide a Click CLI runner."""
        return CliRunner()

    @pytest.fixture
    def ldap_config(self) -> t.JsonMapping:
        """Provide a minimal LDAP tap configuration."""
        return {
            "ldap_host": "test.ldap.com",
            "ldap_port": 389,
            "base_dn": "dc=test,dc=com",
            "bind_dn": "cn=admin,dc=test,dc=com",
            "bind_password": "test_password",
        }

    @pytest.fixture
    def config_file(self, tmp_path: Path, ldap_config: t.JsonMapping) -> Path:
        """Write the tap configuration to a temporary file."""
        config_path = tmp_path / "settings.json"
        u.Cli.json_write(config_path, ldap_config)
        return config_path

    @pytest.fixture
    def catalog_file(self, tmp_path: Path) -> Path:
        """Write a minimal Singer catalog to a temporary file."""
        catalog_path = tmp_path / "catalog.json"
        catalog: t.JsonMapping = {
            "streams": [
                {
                    "tap_stream_id": "users",
                    "schema": {"properties": {"dn": {"type": "string"}}},
                    "metadata": [],
                },
            ],
        }
        u.Cli.json_write(catalog_path, catalog)
        return catalog_path

    @pytest.fixture
    def state_file(self, tmp_path: Path) -> Path:
        """Write a Singer state file to a temporary location."""
        state_path = tmp_path / "state.json"
        u.Cli.json_write(state_path, {"bookmarks": {}})
        return state_path

    def test_discover_emits_parseable_catalog_with_streams_key(
        self,
        runner: CliRunner,
        config_file: Path,
    ) -> None:
        """Discovery exits cleanly and emits a JSON catalog exposing a streams list."""
        result = runner.invoke(
            self._command(),
            ["--config", str(config_file), "--discover"],
            catch_exceptions=False,
        )
        assert result.exit_code == 0
        catalog = _extract_catalog(result.output)
        assert "streams" in catalog
        assert isinstance(catalog["streams"], list)

    @pytest.mark.parametrize("expected_stream", STANDARD_STREAMS)
    def test_discover_publishes_each_standard_ldap_stream(
        self,
        runner: CliRunner,
        config_file: Path,
        expected_stream: str,
    ) -> None:
        """Discovery advertises every standard LDAP stream in its catalog."""
        result = runner.invoke(
            self._command(),
            ["--config", str(config_file), "--discover"],
            catch_exceptions=False,
        )
        assert result.exit_code == 0
        assert expected_stream in _stream_ids(_extract_catalog(result.output))

    def test_discover_includes_custom_streams_from_config(
        self,
        runner: CliRunner,
        tmp_path: Path,
    ) -> None:
        """Custom streams declared in config surface as discoverable streams."""
        settings: t.JsonMapping = {
            "ldap_host": "test.ldap.com",
            "base_dn": "dc=test,dc=com",
            "custom_streams": [
                {
                    "name": "service_accounts",
                    "search_filter": "(&(object_class=account)(uid=svc-*))",
                    "primary_keys": ["dn"],
                    "schema": {"properties": {"dn": {"type": "string"}}},
                },
            ],
        }
        config_path = tmp_path / "settings.json"
        u.Cli.json_write(config_path, settings)
        result = runner.invoke(
            self._command(),
            ["--config", str(config_path), "--discover"],
            catch_exceptions=False,
        )
        assert result.exit_code == 0
        stream_ids = _stream_ids(_extract_catalog(result.output))
        assert "service_accounts" in stream_ids
        # Custom streams extend, not replace, the standard catalog.
        assert "users" in stream_ids

    def test_sync_emits_schema_messages_for_standard_streams(
        self,
        runner: CliRunner,
        config_file: Path,
        catalog_file: Path,
    ) -> None:
        """Sync mode emits a Singer SCHEMA message per standard stream."""
        result = runner.invoke(
            self._command(),
            ["--config", str(config_file), "--catalog", str(catalog_file)],
            catch_exceptions=False,
        )
        assert result.exit_code == 0
        messages = _singer_messages(result.output)
        assert messages
        assert {str(msg["type"]) for msg in messages} == {"SCHEMA"}
        emitted_streams = {str(msg["stream"]) for msg in messages}
        assert set(STANDARD_STREAMS) <= emitted_streams

    def test_schema_message_declares_dn_key_property(
        self,
        runner: CliRunner,
        config_file: Path,
        catalog_file: Path,
    ) -> None:
        """Each SCHEMA message advertises the LDAP dn as its key property."""
        result = runner.invoke(
            self._command(),
            ["--config", str(config_file), "--catalog", str(catalog_file)],
            catch_exceptions=False,
        )
        assert result.exit_code == 0
        messages = _singer_messages(result.output)
        assert messages
        for msg in messages:
            assert msg["key_properties"] == ["dn"]

    def test_incremental_sync_accepts_state_and_still_emits_schema(
        self,
        runner: CliRunner,
        config_file: Path,
        catalog_file: Path,
        state_file: Path,
    ) -> None:
        """Supplying a state file is accepted and does not suppress SCHEMA output."""
        result = runner.invoke(
            self._command(),
            [
                "--config",
                str(config_file),
                "--catalog",
                str(catalog_file),
                "--state",
                str(state_file),
            ],
            catch_exceptions=False,
        )
        assert result.exit_code == 0
        message_types = {str(msg["type"]) for msg in _singer_messages(result.output)}
        assert "SCHEMA" in message_types

    def test_missing_config_file_is_rejected(
        self,
        runner: CliRunner,
        tmp_path: Path,
    ) -> None:
        """A non-existent --config path fails validation with a non-zero exit."""
        result = runner.invoke(
            self._command(),
            ["--config", str(tmp_path / "does_not_exist.json"), "--discover"],
        )
        assert result.exit_code != 0

    def test_incomplete_config_degrades_gracefully(
        self,
        runner: CliRunner,
        tmp_path: Path,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Config missing LDAP connection fields still discovers streams (exit 0)."""
        config_path = tmp_path / "bad_config.json"
        u.Cli.json_write(config_path, {"invalid": "settings"})
        result = runner.invoke(
            self._command(),
            ["--config", str(config_path), "--discover"],
        )
        assert result.exit_code == 0
        combined = " ".join(record.getMessage() for record in caplog.records)
        combined += (result.output or "") + (result.stderr or "")
        assert "Invalid LDAP connection configuration" in combined


__all__: list[str] = ["TestsFlextTapLdapIntegration"]
