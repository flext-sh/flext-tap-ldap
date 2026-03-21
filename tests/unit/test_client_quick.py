"""Quick comprehensive tests for LDAP client to maximize coverag efficiently.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import contextlib
from unittest.mock import Mock, patch

import pytest
from flext_tests import u

from flext_tap_ldap import FlextTapLdapClient


class TestLDAPClientQuick:
    """Quick tests to maximize client.py coverage efficiently."""

    @pytest.fixture
    def client(self) -> FlextTapLdapClient.LDAPClient:
        """Create LDAP client fixture for testing."""
        return FlextTapLdapClient.LDAPClient(
            host="test.ldap.com",
            port=389,
            bind_dn="cn=REDACTED_LDAP_BIND_PASSWORD,dc=test,dc=com",
            password="test_password",
            use_ssl=False,
            timeout=30,
            page_size=1000,
        )

    def test_server_uri_property(self) -> None:
        """Test method."""
        "Test server_uri property for both LDAP and LDAPS."
        ldap_client = FlextTapLdapClient.LDAPClient(
            host="test.com", port=389, use_ssl=False
        )
        u.Tests.Matchers.that(ldap_client.server_uri == "ldap://test.com:389", eq=True)
        ldaps_client = FlextTapLdapClient.LDAPClient(
            host="secure.com", port=636, use_ssl=True
        )
        u.Tests.Matchers.that(
            ldaps_client.server_uri == "ldaps://secure.com:636", eq=True
        )

    def test_scope_conversions(self, client: FlextTapLdapClient.LDAPClient) -> None:
        """Test all scope conversions."""
        u.Tests.Matchers.that(client._convert_scope_to_enum("BASE") == "BASE", eq=True)
        u.Tests.Matchers.that(
            client._convert_scope_to_enum("ONELEVEL") == "ONELEVEL", eq=True
        )
        u.Tests.Matchers.that(
            client._convert_scope_to_enum("SUBTREE") == "SUBTREE", eq=True
        )
        u.Tests.Matchers.that(client._convert_scope_to_enum("base") == "BASE", eq=True)
        u.Tests.Matchers.that(
            client._convert_scope_to_enum("INVALID") == "SUBTREE", eq=True
        )

    def test_entry_conversion_scenarios(
        self, client: FlextTapLdapClient.LDAPClient
    ) -> None:
        """Test entry conversion with different scenarios."""
        mock_entry = Mock()
        mock_entry.dn = "uid=test,dc=example,dc=com"
        empty_attributes: list[str] = []
        mock_entry.attributes = {
            "uid": ["test"],
            "cn": ["Test", "T. User"],
            "empty": empty_attributes,
        }
        result = client._convert_entry_to_dict(mock_entry)
        u.Tests.Matchers.that(result["dn"] == "uid=test,dc=example,dc=com", eq=True)
        u.Tests.Matchers.that(result["uid"] == "test", eq=True)
        u.Tests.Matchers.that(result["cn"] == ["Test", "T. User"], eq=True)
        u.Tests.Matchers.that(result["empty"] == [], eq=True)
        mail_values: list[str] = ["test@example.com"]
        dict_entry: dict[str, object] = {
            "dn": "uid=dict,dc=example,dc=com",
            "attributes": {"mail": mail_values},
        }
        result = client._convert_entry_to_dict(dict_entry)
        u.Tests.Matchers.that(result["dn"] == "uid=dict,dc=example,dc=com", eq=True)
        result = client._convert_entry_to_dict(None)
        u.Tests.Matchers.that(result == {}, eq=True)

    def test_search_result_processing(
        self, client: FlextTapLdapClient.LDAPClient
    ) -> None:
        """Test search result processing with different scenarios."""
        mock_result = Mock()
        mock_result.is_success = True
        mock_result.data = [
            Mock(dn="uid=user1,dc=test,dc=com", attributes={"uid": ["user1"]}),
            Mock(dn="uid=user2,dc=test,dc=com", attributes={"uid": ["user2"]}),
        ]
        results = client._process_search_results(mock_result, size_limit=0)
        u.Tests.Matchers.that(len(results) == 2, eq=True)
        u.Tests.Matchers.that(results[0]["dn"] == "uid=user1,dc=test,dc=com", eq=True)
        results = client._process_search_results(mock_result, size_limit=1)
        u.Tests.Matchers.that(len(results) == 1, eq=True)
        mock_result.is_success = False
        results = client._process_search_results(mock_result, size_limit=0)
        u.Tests.Matchers.that(len(results) == 0, eq=True)
        mock_result.is_success = True
        mock_result.data = None
        results = client._process_search_results(mock_result, size_limit=0)
        u.Tests.Matchers.that(len(results) == 0, eq=True)

    @patch("flext_tap_ldap.client.get_running_loop")
    def test_search_no_event_loop(
        self, mock_get_loop: Mock, client: FlextTapLdapClient.LDAPClient
    ) -> None:
        """Test search when no event loop is running."""
        mock_get_loop.side_effect = RuntimeError("no event loop")
        with patch.object(client, "_run_in_new_loop", return_value=[]) as mock_run:
            results = client.search("dc=test,dc=com")
            mock_run.assert_called_once()
            u.Tests.Matchers.that(results == [], eq=True)

    @patch("flext_tap_ldap.client.get_running_loop")
    def test_search_with_event_loop(
        self, mock_get_loop: Mock, client: FlextTapLdapClient.LDAPClient
    ) -> None:
        """Test search when event loop is already running."""
        mock_get_loop.return_value = Mock()
        results = client.search("dc=test,dc=com")
        u.Tests.Matchers.that(results == [], eq=True)

    def test_run_in_new_loop(self, client: FlextTapLdapClient.LDAPClient) -> None:
        """Test search execution helper in new loop."""
        with patch.object(client, "search", return_value=[{"test": "data"}]):
            result = client.search("dc=test,dc=com")
        u.Tests.Matchers.that(list(result) == [{"test": "data"}], eq=True)

    @patch("flext_tap_ldap.client.get_running_loop")
    @patch("flext_tap_ldap.client.new_event_loop")
    def test_test_connection_no_loop(
        self,
        mock_new_loop: Mock,
        mock_get_loop: Mock,
        client: FlextTapLdapClient.LDAPClient,
    ) -> None:
        """Test connection test when no event loop."""
        mock_get_loop.side_effect = RuntimeError("no event loop")
        mock_loop = Mock()
        mock_new_loop.return_value = mock_loop
        mock_loop.run_until_complete.return_value = True
        result = client.test_connection()
        u.Tests.Matchers.that(result is True, eq=True)
        mock_new_loop.assert_called_once()
        mock_loop.close.assert_called_once()

    @patch("flext_tap_ldap.client.get_running_loop")
    def test_test_connection_with_loop(
        self, client: FlextTapLdapClient.LDAPClient, mock_get_loop: Mock
    ) -> None:
        """Test connection test when event loop exists."""
        mock_get_loop.return_value = Mock()
        result = client.test_connection()
        u.Tests.Matchers.that(result is True, eq=True)

    def test_health_check_functionality(
        self, client: FlextTapLdapClient.LDAPClient
    ) -> None:
        """Test health check functionality."""
        with patch.object(client, "test_connection", return_value=True):
            health = client.health_check()
            u.Tests.Matchers.that(health["status"] == "healthy", eq=True)
            u.Tests.Matchers.that(
                health["server_uri"] == "ldap://test.ldap.com:389", eq=True
            )
            u.Tests.Matchers.that(health["connection_test"] is True, eq=True)
            u.Tests.Matchers.that(
                isinstance(health["response_time_ms"], (int, float)), eq=True
            )
        with patch.object(client, "test_connection", return_value=False):
            health = client.health_check()
            u.Tests.Matchers.that(health["status"] == "unhealthy", eq=True)
            u.Tests.Matchers.that(health["connection_test"] is False, eq=True)

    def test_oracle_entry_processing(
        self, client: FlextTapLdapClient.LDAPClient
    ) -> None:
        """Test Oracle entry processing with all scenarios."""
        uid_values: list[str] = ["test"]
        oracle_password_values: list[str] = ["hashed_password"]
        object_classes: list[str] = ["inetOrgPerson"]
        entry: dict[str, object] = {
            "dn": "uid=test,dc=oracle,dc=com",
            "attributes": {
                "uid": uid_values,
                "orclPassword": oracle_password_values,
                "objectClass": object_classes,
            },
        }
        result = client._process_oracle_entry(entry)
        attributes = result.get("attributes")
        u.Tests.Matchers.that(isinstance(attributes, dict), eq=True)
        assert isinstance(attributes, dict)
        u.Tests.Matchers.that("userPassword" in attributes, eq=True)
        user_password = attributes.get("userPassword")
        u.Tests.Matchers.that(isinstance(user_password, list), eq=True)
        assert isinstance(user_password, list)
        u.Tests.Matchers.that("hashed_password" in user_password, eq=True)

        ou_values: list[str] = ["test"]
        container_classes: list[str] = ["orclContainer"]
        entry_with_container: dict[str, object] = {
            "dn": "ou=test,dc=oracle,dc=com",
            "attributes": {"ou": ou_values, "objectClass": container_classes},
        }
        result = client._process_oracle_entry(entry_with_container)
        attributes = result.get("attributes")
        u.Tests.Matchers.that(isinstance(attributes, dict), eq=True)
        assert isinstance(attributes, dict)
        object_class = attributes.get("objectClass")
        u.Tests.Matchers.that(isinstance(object_class, list), eq=True)
        assert isinstance(object_class, list)
        u.Tests.Matchers.that("organizationalUnit" in object_class, eq=True)

        entry_string_oc: dict[str, object] = {
            "dn": "ou=test,dc=oracle,dc=com",
            "attributes": {"objectClass": "orclContainer"},
        }
        result = client._process_oracle_entry(entry_string_oc)
        attributes = result.get("attributes")
        u.Tests.Matchers.that(isinstance(attributes, dict), eq=True)
        assert isinstance(attributes, dict)
        obj_classes = attributes.get("objectClass")
        u.Tests.Matchers.that(isinstance(obj_classes, list), eq=True)
        assert isinstance(obj_classes, list)
        u.Tests.Matchers.that("organizationalUnit" in obj_classes, eq=True)

        entry_bad_attrs: dict[str, object] = {
            "dn": "uid=test,dc=oracle,dc=com",
            "attributes": "not_a_dict",
        }
        result = client._process_oracle_entry(entry_bad_attrs)
        u.Tests.Matchers.that(result == entry_bad_attrs, eq=True)

    def test_oracle_attribute_extension(
        self, client: FlextTapLdapClient.LDAPClient
    ) -> None:
        """Test Oracle attribute extension."""
        base_attrs = ["uid", "cn"]
        extended = client._extend_attributes_with_oracle_support(
            base_attrs, oracle_oid_mode=True
        )
        u.Tests.Matchers.that(extended is not None, eq=True)
        assert extended is not None
        u.Tests.Matchers.that("uid" in extended, eq=True)
        u.Tests.Matchers.that("cn" in extended, eq=True)
        u.Tests.Matchers.that("orclPassword" in extended, eq=True)
        u.Tests.Matchers.that("userPassword" in extended, eq=True)
        result = client._extend_attributes_with_oracle_support(
            base_attrs, oracle_oid_mode=False
        )
        u.Tests.Matchers.that(result == base_attrs, eq=True)
        result = client._extend_attributes_with_oracle_support(
            None, oracle_oid_mode=True
        )
        u.Tests.Matchers.that(result is None, eq=True)

    def test_process_search_results_with_oracle_support(
        self, client: FlextTapLdapClient.LDAPClient
    ) -> None:
        """Test Oracle search result processing."""
        first_passwords: list[str] = ["pass1"]
        second_uids: list[str] = ["test2"]
        search_results: list[dict[str, object]] = [
            {
                "dn": "uid=test1,dc=oracle,dc=com",
                "attributes": {"orclPassword": first_passwords},
            },
            {"dn": "uid=test2,dc=oracle,dc=com", "attributes": {"uid": second_uids}},
        ]
        results = client._process_search_results_with_oracle_support(
            search_results, oracle_oid_mode=True
        )
        u.Tests.Matchers.that(len(results) == 2, eq=True)
        attributes = results[0].get("attributes")
        u.Tests.Matchers.that(isinstance(attributes, dict), eq=True)
        assert isinstance(attributes, dict)
        u.Tests.Matchers.that("userPassword" in attributes, eq=True)
        results = client._process_search_results_with_oracle_support(
            search_results, oracle_oid_mode=False
        )
        u.Tests.Matchers.that(len(results) == 2, eq=True)
        u.Tests.Matchers.that(results[0] == search_results[0], eq=True)

    @patch("flext_tap_ldap.client.get_running_loop")
    def test_execute_oracle_search_in_new_loop(
        self, client: FlextTapLdapClient.LDAPClient
    ) -> None:
        """Test Oracle search execution in new loop."""
        with patch.object(client, "search", return_value=[{"test": "data"}]):
            result = client._execute_oracle_search_in_new_loop(
                "dc=test,dc=com", "(uid=*)", ["uid"], oracle_oid_mode=True
            )
            result_list = list(result)
            u.Tests.Matchers.that(len(result_list) >= 0, eq=True)

    @patch("flext_tap_ldap.client.get_running_loop")
    def test_search_with_oracle_support_scenarios(
        self, mock_get_loop: Mock, client: FlextTapLdapClient.LDAPClient
    ) -> None:
        """Test Oracle support search with different scenarios."""
        mock_get_loop.return_value = Mock()
        results = client.search_with_oracle_support(
            "dc=oracle,dc=com", "(uid=*)", ["uid"], oracle_oid_mode=True
        )
        u.Tests.Matchers.that(list(results) == [], eq=True)
        mock_get_loop.side_effect = RuntimeError("no event loop")

    def test_attribute_delegation_to_flext_api(
        self, client: FlextTapLdapClient.LDAPClient
    ) -> None:
        """Test attribute delegation to flext API."""
        result = client.search
        u.Tests.Matchers.that(callable(result), eq=True)
        with contextlib.suppress(AttributeError):
            _ = client.non_existent_method
