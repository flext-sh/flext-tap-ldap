"""Tests for tap-ldap."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pytest
# MIGRATED: from singer_sdk.testing import get_tap_test_class -> use flext_meltano
from flext_meltano import get_tap_test_class

from flext_tap_ldap.tap import TapLDAP

# Basic tap tests
TestTapLDAP = get_tap_test_class(
    tap_class=TapLDAP,
    config={
        "host": "test.ldap.com",
        "port": 389,
        "base_dn": "dc=test,dc=com",
        "bind_dn": "cn=REDACTED_LDAP_BIND_PASSWORD,dc=test,dc=com",
        "password": "test_password",
    },
)


class TestTapLDAPUnit:
    """Unit tests for TapLDAP."""

    @pytest.fixture
    def config(self) -> dict[str, Any]:
        return {
            "host": "test.ldap.com",
            "port": 389,
            "base_dn": "dc=test,dc=com",
            "bind_dn": "cn=REDACTED_LDAP_BIND_PASSWORD,dc=test,dc=com",
            "password": "test_password",
            "use_ssl": False,
            "timeout": 30,
            "page_size": 1000,
        }

    def test_tap_initialization(self, config: dict[str, Any]) -> None:
        tap = TapLDAP(config=config)
        if tap.name != "tap-ldap":
            raise AssertionError(f"Expected {"tap-ldap"}, got {tap.name}")
        assert tap.config == config

    def test_discover_streams(self, config: dict[str, Any]) -> None:
        tap = TapLDAP(config=config)
        streams = tap.discover_streams()

        # Check default streams
        stream_names = [s.name for s in streams]
        if "users" not in stream_names:
            raise AssertionError(f"Expected {"users"} in {stream_names}")
        assert "groups" in stream_names
        if "organizational_units" not in stream_names:
            raise AssertionError(f"Expected {"organizational_units"} in {stream_names}")
        assert "schema" in stream_names
        if len(streams) != 4:
            raise AssertionError(f"Expected {4}, got {len(streams)}")

    def test_discover_custom_streams(self, config: dict[str, Any]) -> None:
        config["custom_streams"] = [
            {
                "name": "service_accounts",
                "search_filter": "(&(object_class=account)(uid=svc-*))",
                "primary_keys": ["dn"],
                "replication_key": "modifyTimestamp",
                "schema": {
                    "properties": {
                        "dn": {"type": "string"},
                        "uid": {"type": "string"},
                    },
                },
            },
        ]

        tap = TapLDAP(config=config)
        streams = tap.discover_streams()

        stream_names = [s.name for s in streams]
        if "service_accounts" not in stream_names:
            raise AssertionError(f"Expected {"service_accounts"} in {stream_names}")
        if len(streams) != 5:
            raise AssertionError(f"Expected {5}, got {len(streams)}")

    def test_catalog_generation(self, config: dict[str, Any]) -> None:
        tap = TapLDAP(config=config)
        catalog = tap.catalog_dict

        if "streams" not in catalog:

            raise AssertionError(f"Expected {"streams"} in {catalog}")
        if len(catalog["streams"]) < 4:
            raise AssertionError(f"Expected {len(catalog["streams"])} >= {4}")

        # Check users stream
        users_stream = next(
            s for s in catalog["streams"] if s["tap_stream_id"] == "users"
        )
        if users_stream["replication_method"] != "INCREMENTAL":
            raise AssertionError(f"Expected {"INCREMENTAL"}, got {users_stream["replication_method"]}")
        assert users_stream["replication_key"] == "modifyTimestamp"
        if "inclusion" not in users_stream["metadata"][0]["metadata"]:
            raise AssertionError(f"Expected {"inclusion"} in {users_stream["metadata"][0]["metadata"]}")

    @patch("flext_tap_ldap.client.LDAPClient")
    def test_stream_records(
        self, mock_client_class: MagicMock, config: dict[str, Any],
    ) -> None:
        # Mock LDAP client
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        # Mock search results
        mock_client.search.return_value = [
            {
                "dn": "uid=jdoe,ou=users,dc=test,dc=com",
                "attributes": {
                    "uid": "jdoe",
                    "cn": "John Doe",
                    "mail": "jdoe@test.com",
                    "objectClass": ["inetOrgPerson", "person"],
                },
            },
        ]

        tap = TapLDAP(config=config)
        streams = tap.discover_streams()
        users_stream = next(s for s in streams if s.name == "users")

        # Singer SDK get_records returns tuples (record, context) or just records
        # We need to handle both cases
        raw_records = list(users_stream.get_records(None))
        records: list[dict[str, Any]] = []
        for item in raw_records:
            if isinstance(item, tuple):
                record, _context = item
                records.append(record)
            else:
                records.append(item)

        if len(records) != 1:

            raise AssertionError(f"Expected {1}, got {len(records)}")
        record = records[0]
        if record["dn"] != "uid=jdoe,ou=users,dc=test,dc=com":
            raise AssertionError(f"Expected {"uid=jdoe,ou=users,dc=test,dc=com"}, got {record["dn"]}")
        assert record["uid"] == "jdoe"
