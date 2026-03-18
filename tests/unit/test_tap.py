"""Tests for tap-ldap.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from flext_tests import tm

from flext_tap_ldap import FlextTapLdapStreams, FlextTapLdapTap, m, t


def _build_source_config(
    connection_config: dict[str, t.Scalar],
) -> m.Meltano.DataSourceConfig:
    return m.Meltano.DataSourceConfig(
        source_type="ldap",
        connection_config=connection_config,
        stream_config={},
        source_version="latest",
    )


def _discover_stream_names(
    tap: FlextTapLdapTap,
    connection_config: dict[str, t.Scalar],
) -> tuple[list[str], int]:
    result = tap.discover_streams(source_config=_build_source_config(connection_config))
    assert result.is_success
    assert result.value is not None
    stream_entries = result.value["streams"]
    stream_names = [str(stream["stream"]) for stream in stream_entries]
    return stream_names, len(stream_entries)


class TestFlextTapLdapTapUnit:
    """Unit tests for FlextTapLdapTap."""

    @pytest.fixture
    def config(self) -> dict[str, t.Scalar]:
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

    def test_tap_initialization(self, config: dict[str, t.Scalar]) -> None:
        """Test tap initialization."""
        tap = FlextTapLdapTap()
        if tap.name != "FlextMeltanoTapAbstractions-ldap":
            msg: str = f"Expected {'FlextMeltanoTapAbstractions-ldap'}, got {tap.name}"
            raise AssertionError(msg)
        stream_names, stream_count = _discover_stream_names(tap, config)
        tm.that(stream_count >= 4, eq=True)
        tm.that("users" in stream_names, eq=True)

    def test_stream_discovery(self, config: dict[str, t.Scalar]) -> None:
        """Test stream discovery."""
        tap = FlextTapLdapTap()
        stream_names, stream_count = _discover_stream_names(tap, config)
        if "users" not in stream_names:
            stream_error: str = f"Expected {'users'} in {stream_names}"
            raise AssertionError(stream_error)
        tm.that("groups" in stream_names, eq=True)
        if "organizational_units" not in stream_names:
            ou_error: str = f"Expected {'organizational_units'} in {stream_names}"
            raise AssertionError(ou_error)
        tm.that("schema" in stream_names, eq=True)
        if stream_count != 4:
            count_error: str = f"Expected {4}, got {stream_count}"
            raise AssertionError(count_error)

    def test_custom_streams_configuration(self, config: dict[str, t.Scalar]) -> None:
        """Test custom streams configuration."""
        config["custom_streams"] = "configured"
        tap = FlextTapLdapTap()
        stream_names, stream_count = _discover_stream_names(tap, config)
        if "users" not in stream_names:
            stream_error: str = f"Expected {'users'} in {stream_names}"
            raise AssertionError(stream_error)
        if stream_count < 4:
            count_error: str = f"Expected >= {4}, got {stream_count}"
            raise AssertionError(count_error)

    def test_catalog_generation(self, config: dict[str, t.Scalar]) -> None:
        """Test catalog generation and metadata."""
        tap = FlextTapLdapTap()
        result = tap.discover_streams(source_config=_build_source_config(config))
        assert result.is_success
        assert result.value is not None
        catalog = result.value
        if "streams" not in catalog:
            catalog_error: str = f"Expected {'streams'} in {catalog}"
            raise AssertionError(catalog_error)
        streams = catalog["streams"]
        if len(streams) < 4:
            count_error: str = f"Expected {len(streams)} >= {4}"
            raise AssertionError(count_error)
        users_stream = next(s for s in streams if s["stream"] == "users")
        tm.that(users_stream["stream"] == "users", eq=True)

    @patch("flext_tap_ldap.client.LDAPClient")
    def test_stream_records(
        self,
        mock_client_class: MagicMock,
        config: dict[str, t.Scalar],
    ) -> None:
        """Test streaming records from LDAP."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.search.return_value = [
            {
                "dn": "uid=jdoe,ou=users,dc=test,dc=com",
                "attributes": {
                    "uid": "jdoe",
                    "cn": "John Doe",
                    "mail": "jdoe@test.com",
                    "objectClass": ["inetOrgPerson", "person"],
                },
            }
        ]

        tap = FlextTapLdapTap()
        users_stream = FlextTapLdapStreams.UsersStream(tap)
        raw_records = list(users_stream.get_records(None))
        records: list[dict[str, object]] = [
            item for item in raw_records if isinstance(item, dict)
        ]
        if len(records) != 1:
            count_error: str = f"Expected {1}, got {len(records)}"
            raise AssertionError(count_error)
        record = records[0]
        tm.that(str(record["dn"]) == "uid=jdoe,ou=users,dc=test,dc=com", eq=True)
        tm.that(str(record["uid"]) == "jdoe", eq=True)
        tm.that(config["ldap_host"] == "test.ldap.com", eq=True)
