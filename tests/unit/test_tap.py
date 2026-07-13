"""Behavioral tests for tap-ldap public contract (discovery, records, validation)."""

from __future__ import annotations

from collections.abc import (
    Mapping,
    MutableMapping,
)
from typing import TYPE_CHECKING, cast

import pytest
from flext_tests import tm

from flext_tap_ldap.client import FlextTapLdapClient
from flext_tap_ldap.streams import FlextTapLdapStreams
from flext_tap_ldap.tap import FlextTapLdapTap
from tests import c

if TYPE_CHECKING:
    from tests import m, t


class TestsFlextTapLdapTap:
    """Public-contract behavior of FlextTapLdapTap and its LDAP streams."""

    def test_discover_streams_succeeds_with_stream_catalog_payload(
        self,
        ldap_source_config: m.Meltano.DataSourceConfig,
    ) -> None:
        result = FlextTapLdapTap().discover_streams(tap_instance=ldap_source_config)

        tm.ok(result)
        tm.that(result.value, none=False)
        raw_streams = result.value["streams"]
        tm.that(raw_streams, is_=list)
        assert raw_streams
        for entry in raw_streams:
            tm.that(entry, is_=Mapping)
            tm.that(entry["stream"], is_=str)

    def test_discover_streams_exposes_standard_ldap_streams(
        self,
        ldap_source_config: m.Meltano.DataSourceConfig,
    ) -> None:
        result = FlextTapLdapTap().discover_streams(tap_instance=ldap_source_config)

        tm.ok(result)
        tm.that(result.value, none=False)
        raw_streams = result.value["streams"]
        tm.that(raw_streams, is_=list)
        stream_names = {
            stream["stream"]
            for stream in raw_streams
            if isinstance(stream, Mapping) and "stream" in stream
        }
        assert {"users", "groups", "organizational_units", "schema"}.issubset(
            stream_names,
        )

    @pytest.mark.parametrize(
        ("raw_item", "expected"),
        [
            ({"name": "audit"}, {"name": "audit"}),
            ({"name": "events"}, {"name": "events"}),
            ({"name": ""}, None),
            ({"label": "no-name"}, None),
            ("not-a-mapping", None),
            (42, None),
        ],
    )
    def test_validate_custom_stream_returns_name_only_for_valid_definitions(
        self,
        raw_item: t.JsonValue,
        expected: dict[str, str] | None,
    ) -> None:
        tm.that(FlextTapLdapTap.validate_custom_stream(raw_item), eq=expected)

    @pytest.fixture
    def users_stream(
        self,
        ldap_connection_config: dict[str, t.JsonValue],
        ldap_record_entries: list[dict[str, t.JsonValue]],
        monkeypatch: pytest.MonkeyPatch,
    ) -> FlextTapLdapStreams.UsersStream:
        tap = FlextTapLdapTap()
        tap.tap_config = cast(
            "MutableMapping[str, t.Scalar]",
            {"connection": ldap_connection_config},
        )

        class DummyClient:
            """Stand-in for the external LDAP client boundary."""

            def __init__(
                self,
                *args: t.JsonValue,
                **kwargs: t.JsonValue,
            ) -> None:
                return None

            def search(
                self,
                *_a: t.JsonValue,
                **_k: t.JsonValue,
            ) -> list[dict[str, t.JsonValue]]:
                return ldap_record_entries

        monkeypatch.setattr(FlextTapLdapClient, "LDAPClient", DummyClient)
        return FlextTapLdapStreams.UsersStream(tap)

    def test_users_stream_yields_all_directory_entries(
        self,
        users_stream: FlextTapLdapStreams.UsersStream,
        ldap_record_entries: list[dict[str, t.JsonValue]],
    ) -> None:
        records = list(users_stream.get_records(None))

        tm.that(len(records), eq=len(ldap_record_entries))

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

        tm.that(records[0][field], eq=expected)

    def test_users_stream_exposes_connection_config_via_tap(
        self,
        users_stream: FlextTapLdapStreams.UsersStream,
    ) -> None:
        tap = users_stream.tap
        tm.that(tap, is_=FlextTapLdapTap)
        tm.that(tap.tap_config, none=False)
        connection = tap.tap_config["connection"]
        tm.that(connection, is_=Mapping)
        tm.that(connection["host"], eq=c.Ldap.Tests.HOST)


__all__: list[str] = ["TestsFlextTapLdapTap"]
