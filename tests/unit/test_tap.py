"""Tests for tap-ldap using canonical test namespace patterns."""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping
from typing import cast

import pytest

from flext_tap_ldap import FlextTapLdapClient, FlextTapLdapStreams, FlextTapLdapTap
from tests import c, m, t


class TestFlextTapLdapTap:
    def test_discover_streams_returns_expected_names(
        self,
        ldap_source_config: m.Meltano.DataSourceConfig,
    ) -> None:
        tap = FlextTapLdapTap()
        result = tap.discover_streams(tap_instance=ldap_source_config)

        assert result.success
        assert result.value is not None
        raw_streams = result.value["streams"]
        assert isinstance(raw_streams, list)
        stream_names = {
            stream["stream"]
            for stream in raw_streams
            if isinstance(stream, Mapping) and "stream" in stream
        }
        assert {"users", "groups", "organizational_units", "schema"}.issubset(
            stream_names,
        )

    @pytest.fixture
    def users_stream(
        self,
        ldap_connection_config: dict[str, object],
        ldap_record_entries: list[dict[str, object]],
        monkeypatch: pytest.MonkeyPatch,
    ) -> FlextTapLdapStreams.UsersStream:
        tap = FlextTapLdapTap()
        tap.tap_config = cast(
            "MutableMapping[str, t.Scalar]",
            {"connection": ldap_connection_config},
        )

        class DummyClient:
            def __init__(self, *args: object, **kwargs: object) -> None:
                return None

            def search(self, *_a: object, **_k: object) -> list[dict[str, object]]:
                return ldap_record_entries

        monkeypatch.setattr(FlextTapLdapClient, "LDAPClient", DummyClient)
        return FlextTapLdapStreams.UsersStream(tap)

    @pytest.mark.parametrize(
        ("field", "expected"),
        [
            ("dn", "uid=jdoe,ou=users,dc=test,dc=com"),
            ("uid", "jdoe"),
            ("cn", "John Doe"),
            ("mail", "jdoe@test.com"),
        ],
    )
    def test_users_stream_get_records_maps_expected_fields(
        self,
        users_stream: FlextTapLdapStreams.UsersStream,
        field: str,
        expected: str,
    ) -> None:
        records = list(users_stream.get_records(None))

        assert len(records) == 1
        assert records[0][field] == expected
        assert users_stream.tap.tap_config is not None
        assert users_stream.tap.tap_config["connection"] is not None
        assert (
            users_stream.tap.tap_config["connection"]["host"] == c.Ldap.Tests.Fake.HOST
        )
