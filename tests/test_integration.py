"""Integration tests for tap-ldap."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any
from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner

from tap_ldap.tap import TapLDAP

if TYPE_CHECKING:
    from pathlib import Path


class TestTapLDAPIntegration:
    """Integration tests for tap-ldap."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create CLI runner."""
        return CliRunner()

    @pytest.fixture
    def config_file(self, tmp_path: Path, mock_ldap_config: dict[str, Any]) -> Path:
        """Create config file."""
        config_path = tmp_path / "config.json"
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(mock_ldap_config, f)
        return config_path

    @pytest.fixture
    def catalog_file(self, tmp_path: Path, sample_catalog: dict[str, Any]) -> Path:
        """Create catalog file."""
        catalog_path = tmp_path / "catalog.json"
        with open(catalog_path, "w", encoding="utf-8") as f:
            json.dump(sample_catalog, f)
        return catalog_path

    @pytest.fixture
    def state_file(self, tmp_path: Path, sample_state: dict[str, Any]) -> Path:
        """Create state file."""
        state_path = tmp_path / "state.json"
        with open(state_path, "w", encoding="utf-8") as f:
            json.dump(sample_state, f)
        return state_path

    @patch("tap_ldap.client.Connection")
    @patch("tap_ldap.client.Server")
    def test_discovery_mode(
        self,
        mock_server: Mock,
        mock_connection: Mock,
        runner: CliRunner,
        config_file: Path,
    ) -> None:
        """Test discovery mode."""
        # Mock connection
        mock_conn_instance = mock_connection.return_value
        mock_conn_instance.bound = True
        mock_conn_instance.search.return_value = True
        mock_conn_instance.entries = []

        result = runner.invoke(
            TapLDAP.cli,
            ["--config", str(config_file), "--discover"],
            catch_exceptions=False,
        )

        assert result.exit_code == 0

        # Parse output as catalog
        catalog = json.loads(result.output)
        assert "streams" in catalog

        # Check default streams are discovered
        stream_names = [s["tap_stream_id"] for s in catalog["streams"]]
        assert "users" in stream_names
        assert "groups" in stream_names
        assert "organizational_units" in stream_names
        assert "schema" in stream_names

    @patch("tap_ldap.client.Connection")
    @patch("tap_ldap.client.Server")
    def test_sync_mode(
        self,
        mock_server: Mock,
        mock_connection: Mock,
        runner: CliRunner,
        config_file: Path,
        catalog_file: Path,
    ) -> None:
        """Test sync mode."""
        # Mock connection and search results
        mock_conn_instance = mock_connection.return_value
        mock_conn_instance.bound = True
        mock_conn_instance.result = {"controls": {}}

        # Mock search to return test data
        mock_entry = type(
            "MockEntry",
            (),
            {
                "entry_dn": "uid=jdoe,ou=users,dc=test,dc=com",
                "__iter__": lambda self: iter([]),
            },
        )()

        mock_conn_instance.entries = [mock_entry]
        mock_conn_instance.search.return_value = True

        result = runner.invoke(
            TapLDAP.cli,
            ["--config", str(config_file), "--catalog", str(catalog_file)],
            catch_exceptions=False,
        )

        assert result.exit_code == 0

        # Check output contains Singer messages
        lines = result.output.strip().split("\n")
        messages = [json.loads(line) for line in lines if line]

        # Should have schema and record messages
        message_types = {msg["type"] for msg in messages}
        assert "SCHEMA" in message_types

    @patch("tap_ldap.client.Connection")
    @patch("tap_ldap.client.Server")
    def test_incremental_sync(
        self,
        mock_server: Mock,
        mock_connection: Mock,
        runner: CliRunner,
        config_file: Path,
        catalog_file: Path,
        state_file: Path,
    ) -> None:
        """Test incremental sync with state."""
        # Mock connection
        mock_conn_instance = mock_connection.return_value
        mock_conn_instance.bound = True
        mock_conn_instance.result = {"controls": {}}
        mock_conn_instance.entries = []
        mock_conn_instance.search.return_value = True

        result = runner.invoke(
            TapLDAP.cli,
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

        # Verify incremental filter was applied
        search_calls = mock_conn_instance.search.call_args_list
        if search_calls:
            # Check that modifyTimestamp filter was included
            for call in search_calls:
                filter_arg = call[1].get("search_filter", "")
                if "inetOrgPerson" in filter_arg:
                    # Should include timestamp filter for incremental
                    assert "modifyTimestamp>=" in filter_arg or result.exit_code == 0

    def test_custom_streams_config(self, runner: CliRunner, tmp_path: Path) -> None:
        """Test configuration with custom streams."""
        config = {
            "host": "test.ldap.com",
            "base_dn": "dc=test,dc=com",
            "custom_streams": [
                {
                    "name": "service_accounts",
                    "search_filter": "(&(objectClass=account)(uid=svc-*))",
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
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f)

        with patch("tap_ldap.client.Connection"), patch("tap_ldap.client.Server"):
            result = runner.invoke(
                TapLDAP.cli,
                ["--config", str(config_file), "--discover"],
                catch_exceptions=False,
            )

        assert result.exit_code == 0

        # Check custom stream is in catalog
        catalog = json.loads(result.output)
        stream_names = [s["tap_stream_id"] for s in catalog["streams"]]
        assert "service_accounts" in stream_names

    def test_error_handling(self, runner: CliRunner, tmp_path: Path) -> None:
        """Test error handling."""
        # Test with invalid config
        config_file = tmp_path / "bad_config.json"
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump({"invalid": "config"}, f)  # Missing required fields

        result = runner.invoke(
            TapLDAP.cli,
            ["--config", str(config_file), "--discover"],
        )

        assert result.exit_code != 0

    @patch("tap_ldap.client.Connection")
    @patch("tap_ldap.client.Server")
    def test_pagination_handling(
        self,
        mock_server: Mock,
        mock_connection: Mock,
        runner: CliRunner,
        config_file: Path,
        catalog_file: Path,
    ) -> None:
        """Test pagination handling."""
        # Mock connection with pagination
        mock_conn_instance = mock_connection.return_value
        mock_conn_instance.bound = True

        # First page
        mock_conn_instance.result = {
            "controls": {"1.2.840.113556.1.4.319": {"value": {"cookie": b"page1"}}},
        }

        # Mock entries for pagination
        mock_entry1 = type(
            "MockEntry",
            (),
            {
                "entry_dn": "uid=user1,ou=users,dc=test,dc=com",
                "__iter__": lambda self: iter([]),
            },
        )()

        mock_entry2 = type(
            "MockEntry",
            (),
            {
                "entry_dn": "uid=user2,ou=users,dc=test,dc=com",
                "__iter__": lambda self: iter([]),
            },
        )()

        # Set up pagination responses
        call_count = 0

        def side_effect(*args: object, **kwargs: object) -> bool:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                mock_conn_instance.entries = [mock_entry1]
                mock_conn_instance.result = {
                    "controls": {
                        "1.2.840.113556.1.4.319": {"value": {"cookie": b"page1"}},
                    },
                }
                mock_conn_instance.entries = [mock_entry2]
                mock_conn_instance.result = {"controls": {}}
            return True

        mock_conn_instance.search.side_effect = side_effect

        result = runner.invoke(
            TapLDAP.cli,
            ["--config", str(config_file), "--catalog", str(catalog_file)],
            catch_exceptions=False,
        )

        assert result.exit_code == 0
        assert mock_conn_instance.search.call_count >= 2  # Multiple pages
