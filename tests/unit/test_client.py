"""Coverage boost tests to push client.py to 80%+ coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from flext_tap_ldap.client import FlextTapLdapClient
from tests.utilities import u


class TestsFlextTapLdapClient:
    """Tests designed to cover remaining gaps in client.py."""

    @pytest.fixture
    def client(self) -> FlextTapLdapClient.LDAPClient:
        """Create a test LDAP client fixture."""
        return FlextTapLdapClient.LDAPClient(
            host="test.ldap.com",
            port=389,
            bind_dn="cn=REDACTED_LDAP_BIND_PASSWORD,dc=test,dc=com",
            bind_password="test_password",
            use_ssl=False,
            timeout=30,
            page_size=1000,
        )

    def test_server_uri_property(self, client: FlextTapLdapClient.LDAPClient) -> None:
        """Server URI is exposed through the public property."""
        assert client.server_uri == "ldap://test.ldap.com:389"
        ssl_client = FlextTapLdapClient.LDAPClient(
            host="secure.com",
            port=636,
            use_ssl=True,
        )
        assert ssl_client.server_uri == "ldaps://secure.com:636"

    def test_search_method_coverage(
        self,
        client: FlextTapLdapClient.LDAPClient,
    ) -> None:
        """Search returns normalized public results."""
        search_result = Mock()
        search_result.success = True
        search_result.value = Mock(entries=[{"dn": "uid=test,dc=test,dc=com"}])
        api_cls = type(client._flext_api)
        with patch.object(api_cls, "search", return_value=search_result):
            results = client.search(
                base_dn="dc=test,dc=com",
                search_filter="(uid=*)",
                attributes=["uid", "cn"],
                scope="SUBTREE",
                size_limit=100,
            )
        assert results == [{"dn": "uid=test,dc=test,dc=com"}]

    def test_health_check_coverage(self, client: FlextTapLdapClient.LDAPClient) -> None:
        """Test health_check method to cover lines 264-270."""
        with patch.object(client, "test_connection", return_value=True) as mock_test:
            health = client.health_check()
            mock_test.assert_called_once()
            assert health["status"] == "healthy"
            assert health["server_uri"] == "ldap://test.ldap.com:389"
            assert health["connection_test"] is True
            assert "response_time_ms" in health
            assert isinstance(health["response_time_ms"], (int, float))
        with patch.object(client, "test_connection", return_value=False):
            health = client.health_check()
            assert health["status"] == "unhealthy"
            assert health["connection_test"] is False

    @patch("flext_tap_ldap.client.get_running_loop")
    def test_search_with_oracle_support_no_loop(
        self,
        mock_get_loop: Mock,
        client: FlextTapLdapClient.LDAPClient,
    ) -> None:
        """Oracle search enriches results when no loop is active."""
        mock_get_loop.side_effect = RuntimeError("no event loop")
        with patch.object(
            client,
            "search",
            return_value=[
                {
                    "dn": "uid=test,dc=oracle,dc=com",
                    "attributes": {"orclPassword": ["secret"]},
                },
            ],
        ):
            results = client.search_with_oracle_support(
                base_dn="dc=oracle,dc=com",
                search_filter="(uid=test)",
                attributes=["uid"],
                oracle_oid_mode=True,
            )
        assert isinstance(results[0].get("attributes"), dict)
        oracle_attributes = results[0].get("attributes")
        assert isinstance(oracle_attributes, dict)
        assert "userPassword" in oracle_attributes

    def test_execute_oracle_search_in_new_loop_comprehensive(
        self,
        client: FlextTapLdapClient.LDAPClient,
    ) -> None:
        """Oracle helper loop delegates to canonical utility behavior."""
        with (
            patch.object(
                client,
                "search",
                return_value=[
                    {
                        "dn": "uid=test,dc=oracle,dc=com",
                        "attributes": {"orclPassword": ["secret"]},
                    },
                ],
            ) as mock_search,
        ):
            result = client._execute_oracle_search_in_new_loop(
                base_dn="dc=oracle,dc=com",
                search_filter="(uid=*)",
                attributes=["uid"],
                oracle_oid_mode=True,
            )
            mock_search.assert_called_once_with("dc=oracle,dc=com", "(uid=*)", ["uid"])
            result_list = list(result)
            assert result_list == u.TapLdap.ClientSupport.process_oracle_search_results(
                [
                    {
                        "dn": "uid=test,dc=oracle,dc=com",
                        "attributes": {"orclPassword": ["secret"]},
                    },
                ],
                oracle_oid_mode=True,
            )

    @patch("flext_tap_ldap.client.get_running_loop")
    def test_search_with_oracle_support_with_loop(
        self,
        mock_get_loop: Mock,
        client: FlextTapLdapClient.LDAPClient,
    ) -> None:
        """Test oracle support search with existing loop (covers lines 381-385)."""
        mock_get_loop.return_value = Mock()
        results = client.search_with_oracle_support(
            "dc=oracle,dc=com",
            "(uid=*)",
            oracle_oid_mode=True,
        )
        assert results == []
