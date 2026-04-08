"""Tests for tap-ldap.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_tap_ldap import FlextTapLdapStreams, FlextTapLdapTap


def config() -> dict:
    return {
        "ldap_host": "test.ldap.com",
        "ldap_port": 389,
        "base_dn": "dc=test,dc=com",
        "bind_dn": "cn=REDACTED_LDAP_BIND_PASSWORD,dc=test,dc=com",
        "bind_password": "test_password",
        "use_tls": False,
        "page_size": 1000,
    }


def test_streams_discovery_and_records(monkeypatch) -> None:
    tap = FlextTapLdapTap()
    # Descoberta de streams via API pública
    result = tap.discover_streams(tap_instance=config())
    assert result.is_success and result.value and "streams" in result.value
    streams = result.value["streams"]
    names = {s["stream"] for s in streams}
    assert {"users", "groups", "organizational_units", "schema"}.issubset(names)
    # Mock para simular retorno de registros

    class DummyClient:
        def search(self, *_a, **_k):
            return [
                {
                    "dn": "uid=jdoe,ou=users,dc=test,dc=com",
                    "uid": "jdoe",
                    "cn": "John Doe",
                    "mail": "jdoe@test.com",
                    "objectClass": ["inetOrgPerson", "person"],
                }
            ]

    monkeypatch.setattr(
        "flext_tap_ldap.streams.FlextTapLdapClient.LDAPClient", DummyClient
    )
    tap.tap_config = {
        "connection": {
            "host": "test.ldap.com",
            "port": 389,
            "base_dn": "dc=test,dc=com",
            "bind_dn": "cn=REDACTED,dc=test,dc=com",
            "bind_password": "test_password",
        },
    }
    users_stream = FlextTapLdapStreams.UsersStream(tap)
    records = list(users_stream.get_records(None))
    assert len(records) == 1
    rec = records[0]
    assert rec["dn"] == "uid=jdoe,ou=users,dc=test,dc=com"
    assert rec["uid"] == "jdoe"
    assert tap.tap_config["connection"]["host"] == "test.ldap.com"
