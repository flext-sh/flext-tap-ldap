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
        assert tap.name == "tap-ldap"
        assert tap.config == config

    def test_discover_streams(self, config: dict[str, Any]) -> None:
        tap = TapLDAP(config=config)
        streams = tap.discover_streams()

        # Check default streams
        stream_names = [s.name for s in streams]
        assert "users" in stream_names
        assert "groups" in stream_names
        assert "organizational_units" in stream_names
        assert "schema" in stream_names
        assert len(streams) == 4

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
        assert "service_accounts" in stream_names
        assert len(streams) == 5

    def test_catalog_generation(self, config: dict[str, Any]) -> None:
        tap = TapLDAP(config=config)
        catalog = tap.catalog_dict

        assert "streams" in catalog
        assert len(catalog["streams"]) >= 4

        # Check users stream
        users_stream = next(
            s for s in catalog["streams"] if s["tap_stream_id"] == "users"
        )
        assert users_stream["replication_method"] == "INCREMENTAL"
        assert users_stream["replication_key"] == "modifyTimestamp"
        assert "inclusion" in users_stream["metadata"][0]["metadata"]

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

        assert len(records) == 1
        record = records[0]
        assert record["dn"] == "uid=jdoe,ou=users,dc=test,dc=com"
        assert record["uid"] == "jdoe"
