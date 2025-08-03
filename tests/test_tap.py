"""Tests for tap-ldap."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

# MIGRATED: from singer_sdk.testing import get_tap_test_class -> use flext_meltano
from flext_meltano import get_tap_test_class

from flext_tap_ldap.tap import FlextTapLDAP

# Basic tap tests
TestFlextTapLDAP = get_tap_test_class(
    tap_class=FlextTapLDAP,
    config={
        "host": "test.ldap.com",
        "port": 389,
        "base_dn": "dc=test,dc=com",
        "bind_dn": "cn=REDACTED_LDAP_BIND_PASSWORD,dc=test,dc=com",
        "password": "test_password",
    },
)


class TestFlextTapLDAPUnit:
    """Unit tests for FlextTapLDAP."""

    @pytest.fixture
    def config(self) -> dict[str, object]:
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

    def test_tap_initialization(self, config: dict[str, object]) -> None:
        tap = FlextTapLDAP(config=config)
        if tap.name != "tap-ldap":
            msg = f"Expected {'tap-ldap'}, got {tap.name}"
            raise AssertionError(msg)
        assert tap.config == config

    def test_discover_streams(self, config: dict[str, object]) -> None:
        tap = FlextTapLDAP(config=config)
        streams = tap.discover_streams()

        # Check default streams
        stream_names = [s.name for s in streams]
        if "users" not in stream_names:
            msg = f"Expected {'users'} in {stream_names}"
            raise AssertionError(msg)
        assert "groups" in stream_names
        if "organizational_units" not in stream_names:
            msg = f"Expected {'organizational_units'} in {stream_names}"
            raise AssertionError(msg)
        assert "schema" in stream_names
        if len(streams) != 4:
            msg = f"Expected {4}, got {len(streams)}"
            raise AssertionError(msg)

    def test_discover_custom_streams(self, config: dict[str, object]) -> None:
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

        tap = FlextTapLDAP(config=config)
        streams = tap.discover_streams()

        stream_names = [s.name for s in streams]
        if "service_accounts" not in stream_names:
            msg = f"Expected {'service_accounts'} in {stream_names}"
            raise AssertionError(msg)
        if len(streams) != 5:
            msg = f"Expected {5}, got {len(streams)}"
            raise AssertionError(msg)

    def test_catalog_generation(self, config: dict[str, object]) -> None:
        tap = FlextTapLDAP(config=config)
        catalog = tap.catalog_dict

        if "streams" not in catalog:
            msg = f"Expected {'streams'} in {catalog}"
            raise AssertionError(msg)
        if len(catalog["streams"]) < 4:
            msg = f"Expected {len(catalog['streams'])} >= {4}"
            raise AssertionError(msg)

        # Check users stream
        users_stream = next(
            s for s in catalog["streams"] if s["tap_stream_id"] == "users"
        )
        if users_stream["replication_method"] != "INCREMENTAL":
            msg = f"Expected {'INCREMENTAL'}, got {users_stream['replication_method']}"
            raise AssertionError(msg)
        assert users_stream["replication_key"] == "modifyTimestamp"
        if "inclusion" not in users_stream["metadata"][0]["metadata"]:
            msg = f"Expected {'inclusion'} in {users_stream['metadata'][0]['metadata']}"
            raise AssertionError(msg)

    @patch("flext_tap_ldap.client.LDAPClient")
    def test_stream_records(
        self,
        mock_client_class: MagicMock,
        config: dict[str, object],
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

        tap = FlextTapLDAP(config=config)
        streams = tap.discover_streams()
        users_stream = next(s for s in streams if s.name == "users")

        # Singer SDK get_records returns tuples (record, context) or just records
        # We need to handle both cases
        raw_records = list(users_stream.get_records(None))
        records: list[dict[str, object]] = []
        for item in raw_records:
            if isinstance(item, tuple):
                record, _context = item
                records.append(record)
            else:
                records.append(item)

        if len(records) != 1:
            msg = f"Expected {1}, got {len(records)}"
            raise AssertionError(msg)
        record = records[0]
        if record["dn"] != "uid=jdoe,ou=users,dc=test,dc=com":
            msg = f"Expected {'uid=jdoe,ou=users,dc=test,dc=com'}, got {record['dn']}"
            raise AssertionError(msg)
        assert record["uid"] == "jdoe"
