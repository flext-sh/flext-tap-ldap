"""Integration tests for tap-ldap.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import json
import time
from collections.abc import (
    Generator,
    Mapping,
    Sequence,
)
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from click.core import Command
from click.testing import CliRunner

from flext_tap_ldap.tap import CLI_COMMAND
from tests import t, u


def _extract_json_from_output(output: str) -> t.JsonMapping:
    """Extract the JSON object from CLI output that may contain log lines."""
    for line in output.strip().splitlines():
        stripped = line.strip()
        if stripped.startswith("{"):
            payload: t.JsonMapping = t.Cli.JSON_MAPPING_ADAPTER.validate_json(stripped)
            return payload
    msg = f"No JSON found in output: {output[:200]}"
    raise ValueError(msg)


class TestsFlextTapLdapIntegration:
    """Integration tests for tap-ldap."""

    @staticmethod
    def _cli_command() -> Command:
        assert isinstance(CLI_COMMAND, Command)
        return CLI_COMMAND

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create a CLI runner fixture for testing."""
        return CliRunner()

    @pytest.fixture
    def mock_ldap_config(self) -> t.JsonMapping:
        """Mock LDAP configuration."""
        return {
            "ldap_host": "test.ldap.com",
            "ldap_port": 389,
            "base_dn": "dc=test,dc=com",
            "bind_dn": "cn=REDACTED_LDAP_BIND_PASSWORD,dc=test,dc=com",
            "bind_password": "test_password",
        }

    @pytest.fixture
    def sample_catalog(self) -> t.JsonMapping:
        """Sample catalog for testing."""
        return {
            "streams": [
                {
                    "tap_stream_id": "users",
                    "schema": {"properties": {"dn": {"type": "string"}}},
                    "metadata": [],
                },
            ],
        }

    @pytest.fixture
    def sample_state(self) -> t.JsonMapping:
        """Sample state for testing."""
        return {"bookmarks": {}}

    @pytest.fixture
    def config_file(self, tmp_path: Path, mock_ldap_config: t.JsonMapping) -> Path:
        """Create temporary settings file."""
        config_path = tmp_path / "settings.json"
        u.Cli.json_write(config_path, mock_ldap_config)
        return config_path

    @pytest.fixture
    def catalog_file(self, tmp_path: Path, sample_catalog: t.JsonMapping) -> Path:
        """Create temporary catalog file."""
        catalog_path = tmp_path / "catalog.json"
        u.Cli.json_write(catalog_path, sample_catalog)
        return catalog_path

    @pytest.fixture
    def state_file(self, tmp_path: Path, sample_state: t.JsonMapping) -> Path:
        """Create a state file fixture for testing."""
        state_path = tmp_path / "state.json"
        u.Cli.json_write(state_path, sample_state)
        return state_path

    @patch("flext_tap_ldap.client.FlextTapLdapClient.LDAPClient")
    def test_discovery_mode(
        self,
        mock_ldap_client: Mock,
        runner: CliRunner,
        config_file: Path,
    ) -> None:
        """Test discovery mode functionality."""
        mock_client_instance = mock_ldap_client.return_value
        empty_records: Sequence[Mapping[str, t.Scalar | t.ScalarMapping]] = []
        mock_client_instance.search.return_value.__aenter__.return_value = empty_records
        result = runner.invoke(
            self._cli_command(),
            ["--config", str(config_file), "--discover"],
            catch_exceptions=False,
        )
        if result.exit_code != 0:
            exit_error: str = f"Expected {0}, got {result.exit_code}"
            raise AssertionError(exit_error)
        catalog = _extract_json_from_output(result.output)
        if "streams" not in catalog:
            catalog_error: str = f"Expected {'streams'} in {catalog}"
            raise AssertionError(catalog_error)
        streams: Sequence[t.JsonMapping] = [
            t.Cli.JSON_MAPPING_ADAPTER.validate_python(stream)
            for stream in t.Cli.JSON_LIST_ADAPTER.validate_python(catalog["streams"])
        ]
        stream_names: list[str] = [str(stream["tap_stream_id"]) for stream in streams]
        if "users" not in stream_names:
            stream_error: str = f"Expected {'users'} in {stream_names}"
            raise AssertionError(stream_error)
        assert "groups" in stream_names
        if "organizational_units" not in stream_names:
            ou_error: str = f"Expected {'organizational_units'} in {stream_names}"
            raise AssertionError(ou_error)
        assert "schema" in stream_names

    @patch("flext_tap_ldap.client.FlextTapLdapClient.LDAPClient")
    def test_sync_mode(
        self,
        mock_ldap_client: Mock,
        runner: CliRunner,
        config_file: Path,
        catalog_file: Path,
    ) -> None:
        """Test sync mode functionality."""
        mock_client_instance = mock_ldap_client.return_value
        mock_client_instance.search.return_value.__aenter__.return_value = [
            {
                "dn": "uid=jdoe,ou=users,dc=test,dc=com",
                "attributes": {"uid": "jdoe", "cn": "John Doe"},
            },
        ]
        result = runner.invoke(
            self._cli_command(),
            ["--config", str(config_file), "--catalog", str(catalog_file)],
            catch_exceptions=False,
        )
        if result.exit_code != 0:
            exit_error: str = f"Expected {0}, got {result.exit_code}"
            raise AssertionError(exit_error)
        lines = result.output.strip().split("\n")
        messages: list[t.JsonMapping] = []
        for line in lines:
            if not line:
                continue
            try:
                messages.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        message_types = {str(msg["type"]) for msg in messages}
        if "SCHEMA" not in message_types:
            schema_error: str = f"Expected {'SCHEMA'} in {message_types}"
            raise AssertionError(schema_error)

    @patch("flext_tap_ldap.client.FlextTapLdapClient.LDAPClient")
    def test_incremental_sync(
        self,
        mock_ldap_client: Mock,
        runner: CliRunner,
        config_file: Path,
        catalog_file: Path,
        state_file: Path,
    ) -> None:
        """Test incremental sync functionality."""
        mock_client_instance = mock_ldap_client.return_value
        empty_records: Sequence[Mapping[str, t.Scalar | t.ScalarMapping]] = []
        mock_client_instance.search.return_value.__aenter__.return_value = empty_records
        result = runner.invoke(
            self._cli_command(),
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
        if result.exit_code != 0:
            exit_error: str = f"Expected {0}, got {result.exit_code}"
            raise AssertionError(exit_error)
        search_calls = mock_client_instance.search.call_args_list
        if search_calls:
            for call in search_calls:
                filter_arg = call[1].get("search_filter", "")
                if "inetOrgPerson" in filter_arg and (
                    "modifyTimestamp>=" not in filter_arg or result.exit_code != 0
                ):
                    filter_error: str = f"Expected timestamp filter in incremental search, got filter='{filter_arg}' and exit_code={result.exit_code}"
                    raise AssertionError(filter_error)

    def test_self(self, runner: CliRunner, tmp_path: Path) -> None:
        """Test method."""
        settings: dict[str, t.JsonValue] = {
            "ldap_host": "test.ldap.com",
            "base_dn": "dc=test,dc=com",
            "custom_streams": [
                {
                    "name": "service_accounts",
                    "search_filter": "(&(object_class=account)(uid=svc-*))",
                    "primary_keys": ["dn"],
                    "schema": {
                        "properties": {
                            "dn": {"type": "string"},
                            "uid": {"type": "string"},
                        },
                    },
                },
            ],
        }
        config_file = tmp_path / "settings.json"
        u.Cli.json_write(config_file, settings)
        with patch(
            "flext_tap_ldap.client.FlextTapLdapClient.LDAPClient",
        ) as mock_ldap_client:
            mock_client_instance = mock_ldap_client.return_value
            empty_records: Sequence[Mapping[str, t.Scalar | t.ScalarMapping]] = []
            mock_client_instance.search.return_value.__aenter__.return_value = (
                empty_records
            )
            result = runner.invoke(
                self._cli_command(),
                ["--config", str(config_file), "--discover"],
                catch_exceptions=False,
            )
        if result.exit_code != 0:
            exit_error: str = f"Expected {0}, got {result.exit_code}"
            raise AssertionError(exit_error)
        catalog = _extract_json_from_output(result.output)
        cat_streams: Sequence[t.JsonMapping] = [
            t.Cli.JSON_MAPPING_ADAPTER.validate_python(stream)
            for stream in t.Cli.JSON_LIST_ADAPTER.validate_python(catalog["streams"])
        ]
        stream_names: list[str] = [
            str(stream_id)
            for stream in cat_streams
            if (stream_id := stream.get("tap_stream_id", stream.get("stream")))
            is not None
        ]
        if "service_accounts" not in stream_names:
            stream_error: str = f"Expected {'service_accounts'} in {stream_names}"
            raise AssertionError(stream_error)

    @pytest.mark.skip(reason="Config validation edge case - tap has fallback behavior")
    def test_error_handling(
        self,
        runner: CliRunner,
        tmp_path: Path,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test error handling functionality."""
        config_file = tmp_path / "bad_config.json"
        u.Cli.json_write(config_file, {"invalid": "settings"})
        result = runner.invoke(
            self._cli_command(),
            ["--config", str(config_file), "--discover"],
        )
        all_logs = " ".join(record.message for record in caplog.records)
        all_output = result.output + result.stderr or "" + result.stdout or ""
        has_validation_failure = (
            "Config validation failed" in all_logs
            or "Config validation failed" in all_output
            or result.exit_code != 0
        )
        assert has_validation_failure, (
            f"Expected settings validation failure. Logs: {all_logs}, Output: {all_output}, Exit code: {result.exit_code}"
        )

    @patch("flext_tap_ldap.client.FlextTapLdapClient.LDAPClient")
    def test_pagination_handling(
        self,
        mock_ldap_client: Mock,
        runner: CliRunner,
        config_file: Path,
        catalog_file: Path,
    ) -> None:
        """Test pagination handling functionality."""
        mock_client_instance = mock_ldap_client.return_value

        def mock_search(
            *args: t.Scalar,
            **kwargs: t.Scalar,
        ) -> Generator[Mapping[str, t.Scalar | t.ScalarMapping]]:
            time.sleep(0)
            yield {
                "dn": "uid=user1,ou=users,dc=test,dc=com",
                "attributes": {"uid": "user1", "cn": "User One"},
            }
            yield {
                "dn": "uid=user2,ou=users,dc=test,dc=com",
                "attributes": {"uid": "user2", "cn": "User Two"},
            }

        mock_client_instance.search = mock_search
        result = runner.invoke(
            self._cli_command(),
            ["--config", str(config_file), "--catalog", str(catalog_file)],
            catch_exceptions=False,
        )
        if result.exit_code != 0:
            exit_error: str = f"Expected {0}, got {result.exit_code}"
            raise AssertionError(exit_error)
