"""Behavioral tests for FlextTapLdapClient.LDAPClient public contract.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import asyncio
from collections.abc import Sequence
from unittest.mock import Mock

import pytest

import flext_tap_ldap.client as client_module
from flext_ldap import FlextLdap
from flext_tap_ldap import c, m
from flext_tap_ldap.client import FlextTapLdapClient
from tests.typings import t

__all__: tuple[str, ...] = ("TestsFlextTapLdapClient",)


def _backend_result(*, success: bool, entries: Sequence[t.Entry] | None) -> Mock:
    """Shape a FlextLdap search result (external boundary response)."""
    result = Mock()
    result.success = success
    if entries is None:
        result.value = None
    else:
        result.value.entries = list(entries)
    return result


class TestsFlextTapLdapClient:
    """Public-contract behavior of the testing-convenience LDAP client."""

    @pytest.fixture
    def make_client(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> t.ClientFactory:
        """Build a client whose external FlextLdap boundary returns a fixed result."""

        def _make(
            *,
            search_result: Mock | None = None,
            search_error: Exception | None = None,
            host: str = "test.ldap.com",
            port: int = 389,
            use_ssl: bool = False,
            page_size: int = c.TapLdap.DEFAULT_PAGE_SIZE,
            bind_dn: str = "",
            password: str = "",
            timeout: int = c.TapLdap.DEFAULT_SEARCH_TIMEOUT,
        ) -> FlextTapLdapClient.LDAPClient:
            backend = Mock(spec=FlextLdap)
            if search_error is not None:
                backend.search.side_effect = search_error
            else:
                backend.search.return_value = (
                    search_result
                    if search_result is not None
                    else _backend_result(success=True, entries=[])
                )
            monkeypatch.setattr(client_module, "FlextLdap", lambda: backend)
            return FlextTapLdapClient.LDAPClient(
                host=host,
                port=port,
                use_ssl=use_ssl,
                page_size=page_size,
                bind_dn=bind_dn,
                password=password,
                timeout=timeout,
            )

        return _make

    @pytest.mark.parametrize(
        ("host", "port", "use_ssl", "expected"),
        [
            ("test.ldap.com", 389, False, "ldap://test.ldap.com:389"),
            ("secure.com", 636, True, "ldaps://secure.com:636"),
            ("host", 1389, False, "ldap://host:1389"),
        ],
    )
    def test_server_uri_reflects_host_port_and_ssl(
        self,
        make_client: t.ClientFactory,
        host: str,
        port: int,
        use_ssl: bool,
        expected: str,
    ) -> None:
        """server_uri renders the scheme, host and port from public state."""
        client = make_client(host=host, port=port, use_ssl=use_ssl)

        assert client.server_uri == expected

    def test_convenience_kwargs_populate_public_connection_fields(
        self,
        make_client: t.ClientFactory,
    ) -> None:
        """Convenience keyword construction exposes connection state publicly."""
        client = make_client(
            host="h.example.com",
            port=636,
            use_ssl=True,
            bind_dn="cn=admin,dc=t,dc=com",
            password="secret",
            timeout=45,
            page_size=250,
        )

        assert client.host == "h.example.com"
        assert client.port == 636
        assert client.use_ssl is True
        assert client.bind_dn == "cn=admin,dc=t,dc=com"
        assert client.password == "secret"
        assert client.timeout == 45
        assert client.page_size == 250

    def test_settings_model_populates_public_connection_fields(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """A ConnectionConfig model is mirrored onto the public fields."""
        monkeypatch.setattr(client_module, "FlextLdap", lambda: Mock(spec=FlextLdap))
        settings = m.Ldap.ConnectionConfig(
            host="model.example.com",
            port=389,
            bind_dn="cn=svc",
            bind_password="pw",
            use_ssl=False,
            timeout=15,
        )

        client = FlextTapLdapClient.LDAPClient(settings=settings, page_size=500)

        assert client.host == "model.example.com"
        assert client.port == 389
        assert client.bind_dn == "cn=svc"
        assert client.password == "pw"
        assert client.use_ssl is False
        assert client.timeout == 15
        assert client.page_size == 500
        assert client.config is settings

    def test_default_construction_uses_default_port_and_page_size(
        self,
        make_client: t.ClientFactory,
    ) -> None:
        """Omitted connection kwargs fall back to documented defaults."""
        client = make_client(host="only-host", port=c.Ldap.PORT)

        assert client.port == c.Ldap.PORT
        assert client.page_size == c.TapLdap.DEFAULT_PAGE_SIZE

    def test_search_returns_normalized_entry_mappings(
        self,
        make_client: t.ClientFactory,
    ) -> None:
        """Search returns the backend entries normalized into JSON mappings."""
        client = make_client(
            search_result=_backend_result(
                success=True,
                entries=[{"dn": "uid=test,dc=test,dc=com", "cn": "test"}],
            ),
        )

        results = client.search(
            base_dn="dc=test,dc=com",
            search_filter="(uid=*)",
            attributes=["uid", "cn"],
        )

        assert results == [{"dn": "uid=test,dc=test,dc=com", "cn": "test"}]

    @pytest.mark.parametrize(
        ("success", "entries"),
        [
            (False, [{"dn": "uid=ignored,dc=test,dc=com"}]),
            (True, None),
        ],
    )
    def test_search_returns_empty_when_backend_has_no_usable_result(
        self,
        make_client: t.ClientFactory,
        success: bool,
        entries: list[t.Entry] | None,
    ) -> None:
        """Search yields an empty list when the backend reports no data."""
        client = make_client(
            search_result=_backend_result(success=success, entries=entries),
        )

        assert client.search(base_dn="dc=test,dc=com") == []

    def test_search_raises_runtime_error_when_backend_search_fails(
        self,
        make_client: t.ClientFactory,
    ) -> None:
        """A backend failure surfaces as a RuntimeError, never a silent value."""
        client = make_client(search_error=ValueError("backend exploded"))

        with pytest.raises(RuntimeError, match="LDAP search failed"):
            client.search(base_dn="dc=test,dc=com")

    def test_health_check_reports_healthy_when_connection_succeeds(
        self,
        make_client: t.ClientFactory,
    ) -> None:
        """health_check reflects a successful backend probe as healthy."""
        client = make_client(
            search_result=_backend_result(success=True, entries=[]),
        )

        health = client.health_check()

        assert health["status"] == c.HealthStatus.HEALTHY.value
        assert health["connection_test"] is True
        assert health["server_uri"] == "ldap://test.ldap.com:389"
        assert isinstance(health["response_time_ms"], float)

    def test_health_check_reports_unhealthy_when_connection_fails(
        self,
        make_client: t.ClientFactory,
    ) -> None:
        """health_check reflects a failed backend probe as unhealthy."""
        client = make_client(
            search_result=_backend_result(success=False, entries=None),
        )

        health = client.health_check()

        assert health["status"] == c.HealthStatus.UNHEALTHY.value
        assert health["connection_test"] is False

    @pytest.mark.parametrize("backend_success", [True, False])
    def test_test_connection_returns_backend_success_flag(
        self,
        make_client: t.ClientFactory,
        backend_success: bool,
    ) -> None:
        """test_connection returns the backend probe's success flag."""
        client = make_client(
            search_result=_backend_result(success=backend_success, entries=None),
        )

        assert client.test_connection() is backend_success

    def test_test_connection_returns_false_when_backend_raises(
        self,
        make_client: t.ClientFactory,
    ) -> None:
        """test_connection degrades a backend exception to False."""
        client = make_client(search_error=RuntimeError("no route to host"))

        assert client.test_connection() is False

    def test_oracle_search_enriches_entries_in_oid_mode(
        self,
        make_client: t.ClientFactory,
    ) -> None:
        """Oracle OID mode maps orclPassword onto userPassword in the results."""
        client = make_client(
            search_result=_backend_result(
                success=True,
                entries=[
                    {
                        "dn": "uid=test,dc=oracle,dc=com",
                        "attributes": {"orclPassword": ["secret"]},
                    },
                ],
            ),
        )

        results = client.search_with_oracle_support(
            base_dn="dc=oracle,dc=com",
            search_filter="(uid=test)",
            attributes=["uid"],
            oracle_oid_mode=True,
        )

        attributes = results[0]["attributes"]
        assert isinstance(attributes, dict)
        assert attributes["userPassword"] == ["secret"]

    def test_oracle_search_passthrough_without_oid_mode(
        self,
        make_client: t.ClientFactory,
    ) -> None:
        """Without OID mode the entries are returned without Oracle enrichment."""
        client = make_client(
            search_result=_backend_result(
                success=True,
                entries=[
                    {
                        "dn": "uid=test,dc=oracle,dc=com",
                        "attributes": {"orclPassword": ["secret"]},
                    },
                ],
            ),
        )

        results = client.search_with_oracle_support(
            base_dn="dc=oracle,dc=com",
            search_filter="(uid=test)",
            attributes=["uid"],
            oracle_oid_mode=False,
        )

        attributes = results[0]["attributes"]
        assert isinstance(attributes, dict)
        assert "userPassword" not in attributes

    def test_oracle_search_returns_empty_inside_running_event_loop(
        self,
        make_client: t.ClientFactory,
    ) -> None:
        """Oracle search refuses to run inside an active event loop and returns []."""
        client = make_client(
            search_result=_backend_result(
                success=True,
                entries=[{"dn": "uid=test,dc=oracle,dc=com"}],
            ),
        )

        async def run() -> t.SequenceOf[t.JsonMapping]:
            return client.search_with_oracle_support(
                base_dn="dc=oracle,dc=com",
                search_filter="(uid=*)",
                oracle_oid_mode=True,
            )

        assert asyncio.run(run()) == []
