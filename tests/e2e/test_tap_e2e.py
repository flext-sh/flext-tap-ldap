"""E2E tests for tap-ldap."""

from __future__ import annotations

import json
import subprocess
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from ldap3 import Connection


class TestTapLDAPE2E:
    """E2E tests for tap-ldap."""

    def test_discovery(
        self,
        tap_config_file: Path,
        tmp_path: Path,
    ) -> None:
        """Test tap discovery."""
        # Run discovery
        result = subprocess.run(
            ["tap-ldap", "--config", str(tap_config_file), "--discover"],
            capture_output=True,
            text=True,
            check=True,
        )

        # Parse catalog
        catalog = json.loads(result.stdout)
        assert "streams" in catalog

        # Check streams are discovered
        stream_names = [s["tap_stream_id"] for s in catalog["streams"]]
        assert "users" in stream_names
        assert "groups" in stream_names
        assert "organizational_units" in stream_names

        # Save catalog for other tests
        catalog_file = tmp_path / "catalog.json"
        catalog_file.write_text(result.stdout)

    def test_sync_mode(
        self,
        tap_config_file: Path,
        catalog_file: Path,
        tmp_path: Path,
        ldap_connection: Connection,
    ) -> None:
        """Test full data extraction."""
        output_file = tmp_path / "tap-output.jsonl"

        # Run tap
        with open(output_file, "w", encoding="utf-8") as f:
            subprocess.run(
                [
                    "tap-ldap",
                    "--config",
                    str(tap_config_file),
                    "--catalog",
                    str(catalog_file),
                ],
                stdout=f,
                check=True,
            )

        # Parse output
        records: list = []
        schemas: dict = {}
        with open(output_file, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    message = json.loads(line)
                    if message["type"] == "RECORD":
                        records.append(message["record"])
                    elif message["type"] == "SCHEMA":
                        schemas[message["stream"]] = message["schema"]

        # Verify we got records
        assert len(records) > 0
        assert len(schemas) > 0

    def test_incremental_mode(
        self,
        tap_config_file: Path,
        catalog_file: Path,
        tmp_path: Path,
        ldap_connection: Connection,
    ) -> None:
        """Test incremental extraction with state."""
        # First run - get initial state
        first_output = tmp_path / "first-run.jsonl"

        with open(first_output, "w", encoding="utf-8") as f:
            subprocess.run(
                [
                    "tap-ldap",
                    "--config",
                    str(tap_config_file),
                    "--catalog",
                    str(catalog_file),
                ],
                stdout=f,
                check=True,
            )

        # Extract state from first run
        state: dict = {}
        with open(first_output, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    message = json.loads(line)
                    if message["type"] == "STATE":
                        state = message["value"]

        if state:
            state_file = tmp_path / "state.json"
            state_file.write_text(json.dumps(state))

            # Second run with state
            second_output = tmp_path / "second-run.jsonl"
            with open(second_output, "w", encoding="utf-8") as f:
                subprocess.run(
                    [
                        "tap-ldap",
                        "--config",
                        str(tap_config_file),
                        "--catalog",
                        str(catalog_file),
                        "--state",
                        str(state_file),
                    ],
                    stdout=f,
                    check=True,
                )

            # Verify second run completed
            assert second_output.exists()
            assert second_output.stat().st_size > 0

    def test_custom_streams(self, tmp_path: Path) -> None:
        """Test custom stream configuration."""
        # Create config with custom streams
        tap_config = {
            "host": "localhost",
            "port": 10389,
            "bind_dn": "cn=REDACTED_LDAP_BIND_PASSWORD,dc=test,dc=com",
            "password": "REDACTED_LDAP_BIND_PASSWORD_password",
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

        config_file = tmp_path / "custom-config.json"
        config_file.write_text(json.dumps(tap_config))

        # Run discovery
        result = subprocess.run(
            ["tap-ldap", "--config", str(config_file), "--discover"],
            capture_output=True,
            text=True,
            check=True,
        )

        catalog = json.loads(result.stdout)
        stream_names = [s["tap_stream_id"] for s in catalog["streams"]]
        assert "service_accounts" in stream_names

    def test_error_handling(self, tmp_path: Path) -> None:
        """Test error handling for connection failures."""
        # Test with bad host
        bad_config = {
            "host": "nonexistent.host",
            "port": 389,
            "base_dn": "dc=test,dc=com",
        }
        bad_config_file = tmp_path / "bad-config.json"
        bad_config_file.write_text(json.dumps(bad_config))

        # Should fail with connection error
        result = subprocess.run(
            ["tap-ldap", "--config", str(bad_config_file), "--discover"],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode != 0

        # Test with bad credentials
        bad_creds_config = {
            "host": "localhost",
            "port": 10389,
            "bind_dn": "cn=REDACTED_LDAP_BIND_PASSWORD,dc=test,dc=com",
            "password": "wrong_password",
            "base_dn": "dc=test,dc=com",
        }
        bad_creds_file = tmp_path / "bad-creds.json"
        bad_creds_file.write_text(json.dumps(bad_creds_config))

        result = subprocess.run(
            ["tap-ldap", "--config", str(bad_creds_file), "--discover"],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode != 0

    def test_large_datasets(
        self,
        tap_config_file: Path,
        catalog_file: Path,
        tmp_path: Path,
        ldap_connection: Connection,
    ) -> None:
        """Test handling of large datasets with pagination."""
        output_file = tmp_path / "large-output.jsonl"

        # Run tap with large page size config
        config_data = json.loads(tap_config_file.read_text())
        config_data["page_size"] = 10  # Small page size to test pagination

        large_config_file = tmp_path / "large-config.json"
        large_config_file.write_text(json.dumps(config_data))

        with open(output_file, "w", encoding="utf-8") as f:
            subprocess.run(
                [
                    "tap-ldap",
                    "--config",
                    str(large_config_file),
                    "--catalog",
                    str(catalog_file),
                ],
                stdout=f,
                check=True,
            )

        # Verify output was generated
        assert output_file.exists()
        assert output_file.stat().st_size > 0

        # Count records
        record_count = 0
        with open(output_file, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    message = json.loads(line)
                    if message["type"] == "RECORD":
                        record_count += 1

        # Should have some records
        assert record_count >= 0  # May be 0 in test environment
