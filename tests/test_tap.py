"""Tests for tap-ldap.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations
from flext_core import FlextTypes as t

from unittest.mock import MagicMock, patch

import pytest

from flext_tap_ldap import FlextTapLdapTap


class TestFlextTapLdapTapUnit:
    """Unit tests for FlextTapLdapTap."""

    @pytest.fixture
    def config(self) -> dict[str, t.GeneralValueType]:
        """Create a test configuration fixture."""
        return {
            "ldap_host": "test.ldap.com",
            "ldap_port": 389,
            "base_dn": "dc=test,dc=com",
            "bind_dn": "cn=REDACTED_LDAP_BIND_PASSWORD,dc=test,dc=com",
            "bind_password": "test_password",
            "use_tls": False,
            "page_size": 1000,
        }

    def test_tap_initialization(self, config: dict[str, t.GeneralValueType]) -> None:
        """Test tap initialization."""
        tap = FlextTapLdapTap(config=config)
        if tap.name != "tap-ldap":
            msg: str = f"Expected {'tap-ldap'}, got {tap.name}"
            raise AssertionError(msg)
        assert tap.config == config

    def test_stream_discovery(self, config: dict[str, t.GeneralValueType]) -> None:
        """Test stream discovery."""
        tap = FlextTapLdapTap(config=config)
        streams = tap.discover_streams()

        # Check default streams
        stream_names = [s.name for s in streams]
        if "users" not in stream_names:
            stream_error: str = f"Expected {'users'} in {stream_names}"
            raise AssertionError(stream_error)
        assert "groups" in stream_names
        if "organizational_units" not in stream_names:
            ou_error: str = f"Expected {'organizational_units'} in {stream_names}"
            raise AssertionError(ou_error)
        assert "schema" in stream_names
        if len(streams) != 4:
            count_error: str = f"Expected {4}, got {len(streams)}"
            raise AssertionError(count_error)

    def test_custom_streams_configuration(self, config: dict[str, t.GeneralValueType]) -> None:
        """Test custom streams configuration."""
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

        tap = FlextTapLdapTap(config=config)
        streams = tap.discover_streams()

        stream_names = [s.name for s in streams]
        if "service_accounts" not in stream_names:
            stream_error: str = f"Expected {'service_accounts'} in {stream_names}"
            raise AssertionError(stream_error)
        if len(streams) != 5:
            count_error: str = f"Expected {5}, got {len(streams)}"
            raise AssertionError(count_error)

    def test_catalog_generation(self, config: dict[str, t.GeneralValueType]) -> None:
        """Test catalog generation and metadata."""
        tap = FlextTapLdapTap(config=config)
        catalog = tap.catalog_dict

        if "streams" not in catalog:
            catalog_error: str = f"Expected {'streams'} in {catalog}"
            raise AssertionError(catalog_error)
        if len(catalog["streams"]) < 4:
            count_error: str = f"Expected {len(catalog['streams'])} >= {4}"
            raise AssertionError(count_error)

        # Check users stream
        users_stream = next(
            s for s in catalog["streams"] if s["tap_stream_id"] == "users"
        )
        if users_stream["replication_method"] != "INCREMENTAL":
            replication_error: str = (
                f"Expected {'INCREMENTAL'}, got {users_stream['replication_method']}"
            )
            raise AssertionError(replication_error)
        assert users_stream["replication_key"] == "modifyTimestamp"
        if "inclusion" not in users_stream["metadata"][0]["metadata"]:
            metadata_error: str = (
                f"Expected {'inclusion'} in {users_stream['metadata'][0]['metadata']}"
            )
            raise AssertionError(metadata_error)

    @patch("flext_tap_ldap.client.LDAPClient")
    def test_stream_records(
        self,
        mock_client_class: MagicMock,
        config: dict[str, t.GeneralValueType],
    ) -> None:
        """Test streaming records from LDAP."""
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

        tap = FlextTapLdapTap(config=config)
        streams = tap.discover_streams()
        users_stream = next(s for s in streams if s.name == "users")

        # Singer SDK get_records returns tuples (record, context) or just records
        # We need to handle both cases
        raw_records = list(users_stream.get_records(None))
        records: list[dict[str, t.GeneralValueType]] = []
        for item in raw_records:
            if isinstance(item, tuple):
                record, _context = item
                records.append(record)
            else:
                records.append(item)

        if len(records) != 1:
            count_error: str = f"Expected {1}, got {len(records)}"
            raise AssertionError(count_error)
        record = records[0]
        if record["dn"] != "uid=jdoe,ou=users,dc=test,dc=com":
            record_error: str = (
                f"Expected {'uid=jdoe,ou=users,dc=test,dc=com'}, got {record['dn']}"
            )
            raise AssertionError(record_error)
        assert record["uid"] == "jdoe"
