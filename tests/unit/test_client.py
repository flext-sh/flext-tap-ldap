"""Coverage boost tests to push client.py to 80%+ coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest
from flext_tests import tm

from flext_tap_ldap import FlextTapLdapClient


class TestLDAPClientCoverageBoost:
    """Tests designed to cover remaining gaps in client.py."""

    @pytest.fixture
    def client(self) -> FlextTapLdapClient.LDAPClient:
        """Create a test LDAP client fixture."""
        return FlextTapLdapClient.LDAPClient(
            host="test.ldap.com",
            port=389,
            bind_dn="cn=REDACTED_LDAP_BIND_PASSWORD,dc=test,dc=com",
            password="test_password",
            use_ssl=False,
            timeout=30,
            page_size=1000,
        )

    def test_build_server_uri(self, client: FlextTapLdapClient.LDAPClient) -> None:
        """Test _build_server_uri method directly."""
        uri = client._build_server_uri()
        tm.that(uri == "ldap://test.ldap.com:389", eq=True)
        ssl_client = FlextTapLdapClient.LDAPClient(
            host="secure.com", port=636, use_ssl=True
        )
        ssl_uri = ssl_client._build_server_uri()
        tm.that(ssl_uri == "ldaps://secure.com:636", eq=True)

    @patch("flext_tap_ldap.client.get_running_loop")
    def test_search_method_coverage(
        self, mock_get_loop: Mock, client: FlextTapLdapClient.LDAPClient
    ) -> None:
        """Test search method to cover lines 199-214."""
        mock_get_loop.side_effect = RuntimeError("no event loop")
        with patch.object(
            client, "_run_in_new_loop", return_value=[{"test": "data"}]
        ) as mock_run:
            results = client.search(
                base_dn="dc=test,dc=com",
                search_filter="(uid=*)",
                attributes=["uid", "cn"],
                scope="SUBTREE",
                size_limit=100,
            )
            mock_run.assert_called_once()
            tm.that(results == [{"test": "data"}], eq=True)
            mock_run.call_args[0][0]
        mock_get_loop.side_effect = None
        mock_get_loop.return_value = Mock()
        results = client.search("dc=test,dc=com")
        tm.that(results == [], eq=True)

    def test_health_check_coverage(self, client: FlextTapLdapClient.LDAPClient) -> None:
        """Test health_check method to cover lines 264-270."""
        with patch.object(client, "test_connection", return_value=True) as mock_test:
            health = client.health_check()
            mock_test.assert_called_once()
            tm.that(health["status"] == "healthy", eq=True)
            tm.that(health["server_uri"] == "ldap://test.ldap.com:389", eq=True)
            tm.that(health["connection_test"] is True, eq=True)
            tm.that("response_time_ms" in health, eq=True)
            tm.that(isinstance(health["response_time_ms"], (int, float)), eq=True)
        with patch.object(client, "test_connection", return_value=False):
            health = client.health_check()
            tm.that(health["status"] == "unhealthy", eq=True)
            tm.that(health["connection_test"] is False, eq=True)

    @patch("flext_tap_ldap.client.get_running_loop")
    def test_search_with_oracle_support_no_loop(
        self, mock_get_loop: Mock, client: FlextTapLdapClient.LDAPClient
    ) -> None:
        """Test oracle support search without event loop."""
        mock_get_loop.side_effect = RuntimeError("no event loop")
        with patch.object(
            client,
            "_execute_oracle_search_in_new_loop",
            return_value=iter([{"oracle": "data"}]),
        ) as mock_exec:
            results = client.search_with_oracle_support(
                base_dn="dc=oracle,dc=com",
                search_filter="(uid=test)",
                attributes=["uid", "orclPassword"],
                oracle_oid_mode=True,
            )
            mock_exec.assert_called_once()
            tm.that(list(results) == [{"oracle": "data"}], eq=True)

    def test_execute_oracle_search_in_new_loop_comprehensive(
        self, client: FlextTapLdapClient.LDAPClient
    ) -> None:
        """Test Oracle search execution to cover lines 350-361."""
        with (
            patch.object(
                client, "search", return_value=[{"test": "entry"}]
            ) as mock_search,
            patch.object(
                client,
                "_process_search_results_with_oracle_support",
                return_value=[{"processed": "entry"}],
            ) as mock_process,
        ):
            result = client._execute_oracle_search_in_new_loop(
                base_dn="dc=oracle,dc=com",
                search_filter="(uid=*)",
                attributes=["uid"],
                oracle_oid_mode=True,
            )
            mock_search.assert_called_once_with("dc=oracle,dc=com", "(uid=*)", ["uid"])
            mock_process.assert_called_once_with(
                [{"test": "entry"}], oracle_oid_mode=True
            )
            result_list = list(result)
            tm.that(result_list == [{"processed": "entry"}], eq=True)

    @patch("flext_tap_ldap.client.get_running_loop")
    def test_search_with_oracle_support_with_loop(
        self, mock_get_loop: Mock, client: FlextTapLdapClient.LDAPClient
    ) -> None:
        """Test oracle support search with existing loop (covers lines 381-385)."""
        mock_get_loop.return_value = Mock()
        results = client.search_with_oracle_support(
            "dc=oracle,dc=com", "(uid=*)", oracle_oid_mode=True
        )
        tm.that(results == [], eq=True)
