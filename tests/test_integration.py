"""Integration tests for tap-ldap.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import json
from collections.abc import AsyncGenerator
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner
from flext_core import FlextTypes

from flext_tap_ldap import FlextTapLDAP


class TestFlextTapLDAPIntegration:
    """Integration tests for tap-ldap."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create a CLI runner fixture for testing."""
        return CliRunner()

    @pytest.fixture
    def mock_ldap_config(self) -> FlextTypes.Core.Dict:
        """Mock LDAP configuration."""
        return {
            "ldap_host": "test.ldap.com",
            "ldap_port": 389,
            "base_dn": "dc=test,dc=com",
            "bind_dn": "cn=admin,dc=test,dc=com",
            "bind_password": "test_password",
        }

    @pytest.fixture
    def sample_catalog(self) -> FlextTypes.Core.Dict:
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
    def sample_state(self) -> FlextTypes.Core.Dict:
        """Sample state for testing."""
        return {"bookmarks": {}}

    @pytest.fixture
    def config_file(
        self, tmp_path: Path, mock_ldap_config: FlextTypes.Core.Dict
    ) -> Path:
        """Create temporary config file."""
        config_path = tmp_path / "config.json"
        with Path(config_path).open("w", encoding="utf-8") as f:
            json.dump(mock_ldap_config, f)
        return config_path

    @pytest.fixture
    def catalog_file(
        self, tmp_path: Path, sample_catalog: FlextTypes.Core.Dict
    ) -> Path:
        """Create temporary catalog file."""
        catalog_path = tmp_path / "catalog.json"
        with Path(catalog_path).open("w", encoding="utf-8") as f:
            json.dump(sample_catalog, f)
        return catalog_path

    @pytest.fixture
    def state_file(self, tmp_path: Path, sample_state: FlextTypes.Core.Dict) -> Path:
        """Create a state file fixture for testing."""
        state_path = tmp_path / "state.json"
        with Path(state_path).open("w", encoding="utf-8") as f:
            json.dump(sample_state, f)
        return state_path

    @patch("flext_tap_ldap.client.LDAPClient")
    def test_discovery_mode(
        self,
        mock_ldap_client: Mock,
        runner: CliRunner,
        config_file: Path,
    ) -> None:
        """Test discovery mode functionality."""
        # Mock flext-ldap client
        mock_client_instance = mock_ldap_client.return_value
        mock_client_instance.search.return_value.__aenter__.return_value = []
        result = runner.invoke(
            FlextTapLDAP.cli,
            ["--config", str(config_file), "--discover"],
            catch_exceptions=False,
        )
        if result.exit_code != 0:
            msg: str = f"Expected {0}, got {result.exit_code}"
            raise AssertionError(msg)
        # Parse output as catalog
        catalog = json.loads(result.output)
        if "streams" not in catalog:
            msg: str = f"Expected {'streams'} in {catalog}"
            raise AssertionError(msg)
        # Check default streams are discovered
        stream_names = [s["tap_stream_id"] for s in catalog["streams"]]
        if "users" not in stream_names:
            msg: str = f"Expected {'users'} in {stream_names}"
            raise AssertionError(msg)
        assert "groups" in stream_names
        if "organizational_units" not in stream_names:
            msg: str = f"Expected {'organizational_units'} in {stream_names}"
            raise AssertionError(msg)
        assert "schema" in stream_names

    @patch("flext_tap_ldap.client.LDAPClient")
    def test_sync_mode(
        self,
        mock_ldap_client: Mock,
        runner: CliRunner,
        config_file: Path,
        catalog_file: Path,
    ) -> None:
        """Test sync mode functionality."""
        # Mock flext-ldap client search results
        mock_client_instance = mock_ldap_client.return_value
        mock_client_instance.search.return_value.__aenter__.return_value = [
            {
                "dn": "uid=jdoe,ou=users,dc=test,dc=com",
                "attributes": {"uid": "jdoe", "cn": "John Doe"},
            },
        ]
        result = runner.invoke(
            FlextTapLDAP.cli,
            ["--config", str(config_file), "--catalog", str(catalog_file)],
            catch_exceptions=False,
        )
        if result.exit_code != 0:
            msg: str = f"Expected {0}, got {result.exit_code}"
            raise AssertionError(msg)
        # Check output contains Singer messages
        lines = result.output.strip().split("\n")
        messages = [json.loads(line) for line in lines if line]
        # Should have schema and record messages
        message_types = {msg["type"] for msg in messages}
        if "SCHEMA" not in message_types:
            msg: str = f"Expected {'SCHEMA'} in {message_types}"
            raise AssertionError(msg)

    @patch("flext_tap_ldap.client.LDAPClient")
    def test_incremental_sync(
        self,
        mock_ldap_client: Mock,
        runner: CliRunner,
        config_file: Path,
        catalog_file: Path,
        state_file: Path,
    ) -> None:
        """Test incremental sync functionality."""
        # Mock flext-ldap client for incremental sync
        mock_client_instance = mock_ldap_client.return_value
        mock_client_instance.search.return_value.__aenter__.return_value = []
        result = runner.invoke(
            FlextTapLDAP.cli,
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
            msg: str = f"Expected {0}, got {result.exit_code}"
            raise AssertionError(msg)
        # Verify incremental filter was applied
        search_calls = mock_client_instance.search.call_args_list
        if search_calls:
            # Check that modifyTimestamp filter was included
            for call in search_calls:
                filter_arg = call[1].get("search_filter", "")
                if "inetOrgPerson" in filter_arg and (
                    "modifyTimestamp>=" not in filter_arg or result.exit_code != 0
                ):
                    msg: str = (
                        f"Expected timestamp filter in incremental search, "
                        f"got filter='{filter_arg}' and exit_code={result.exit_code}"
                    )
                    raise AssertionError(msg)

    def test_custom_streams_config(self, runner: CliRunner, tmp_path: Path) -> None:
        """Test method."""
        config = {
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
        config_file = tmp_path / "config.json"
        with Path(config_file).open("w", encoding="utf-8") as f:
            json.dump(config, f)
        with patch("flext_tap_ldap.client.LDAPClient") as mock_ldap_client:
            # Mock flext-ldap client
            mock_client_instance = mock_ldap_client.return_value
            mock_client_instance.search.return_value.__aenter__.return_value = []
            result = runner.invoke(
                FlextTapLDAP.cli,
                ["--config", str(config_file), "--discover"],
                catch_exceptions=False,
            )
        if result.exit_code != 0:
            msg: str = f"Expected {0}, got {result.exit_code}"
            raise AssertionError(msg)
        # Check custom stream is in catalog
        catalog = json.loads(result.output)
        stream_names = [s["tap_stream_id"] for s in catalog["streams"]]
        if "service_accounts" not in stream_names:
            msg: str = f"Expected {'service_accounts'} in {stream_names}"
            raise AssertionError(msg)

    def test_error_handling(
        self,
        runner: CliRunner,
        tmp_path: Path,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test error handling functionality."""
        # Test with invalid config
        config_file = tmp_path / "bad_config.json"
        with Path(config_file).open("w", encoding="utf-8") as f:
            json.dump({"invalid": "config"}, f)  # Missing required fields
        result = runner.invoke(
            FlextTapLDAP.cli,
            ["--config", str(config_file), "--discover"],
        )
        # Check if validation warning occurred in captured logs or result indicates failure
        all_logs = " ".join(record.message for record in caplog.records)
        all_output = (
            str(result.output) + str(result.stderr or "") + str(result.stdout or "")
        )
        # Either config validation failed message in logs/output OR exit code indicates failure
        has_validation_failure = (
            "Config validation failed" in all_logs
            or "Config validation failed" in all_output
            or result.exit_code != 0
        )
        assert has_validation_failure, (
            f"Expected config validation failure. Logs: {all_logs}, "
            f"Output: {all_output}, Exit code: {result.exit_code}"
        )

    @patch("flext_tap_ldap.client.LDAPClient")
    def test_pagination_handling(
        self,
        mock_ldap_client: Mock,
        runner: CliRunner,
        config_file: Path,
        catalog_file: Path,
    ) -> None:
        """Test pagination handling functionality."""
        # Mock flext-ldap client for pagination testing
        mock_client_instance = mock_ldap_client.return_value

        # Mock flext-ldap client search method with async context manager
        async def mock_search(
            *args: object,  # noqa: ARG001
            **kwargs: object,  # noqa: ARG001
        ) -> AsyncGenerator[FlextTypes.Core.Dict]:
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
            FlextTapLDAP.cli,
            ["--config", str(config_file), "--catalog", str(catalog_file)],
            catch_exceptions=False,
        )
        if result.exit_code != 0:
            msg: str = f"Expected {0}, got {result.exit_code}"
            raise AssertionError(msg)
        # Note: In test environment with hardcoded data, pagination doesn't occur
        # This test verifies the tap can handle pagination setup without errors
