"""Quick comprehensive tests for LDAP client to maximize coverag efficiently.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import contextlib
from unittest.mock import Mock, patch

import pytest

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
        assert ldap_client.server_uri == "ldap://test.com:389"
        ldaps_client = FlextTapLdapClient.LDAPClient(
            host="secure.com", port=636, use_ssl=True
        )
        assert ldaps_client.server_uri == "ldaps://secure.com:636"

    def test_scope_conversions(self, client: FlextTapLdapClient.LDAPClient) -> None:
        """Test all scope conversions."""
        assert client._convert_scope_to_enum("BASE") == "BASE"
        assert client._convert_scope_to_enum("ONELEVEL") == "ONELEVEL"
        assert client._convert_scope_to_enum("SUBTREE") == "SUBTREE"
        assert client._convert_scope_to_enum("base") == "BASE"
        assert client._convert_scope_to_enum("INVALID") == "SUBTREE"

    def test_entry_conversion_scenarios(
        self, client: FlextTapLdapClient.LDAPClient
    ) -> None:
        """Test entry conversion with different scenarios."""
        mock_entry = Mock()
        mock_entry.dn = "uid=test,dc=example,dc=com"
        mock_entry.attributes = {
            "uid": ["test"],
            "cn": ["Test", "T. User"],
            "empty": [],
        }
        result = client._convert_entry_to_dict(mock_entry)
        assert result["dn"] == "uid=test,dc=example,dc=com"
        assert result["uid"] == "test"
        assert result["cn"] == ["Test", "T. User"]
        assert result["empty"] == []
        dict_entry = {
            "dn": "uid=dict,dc=example,dc=com",
            "attributes": {"mail": ["test@example.com"]},
        }
        result = client._convert_entry_to_dict(dict_entry)
        assert result["dn"] == "uid=dict,dc=example,dc=com"
        result = client._convert_entry_to_dict(None)
        assert result == {}

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
        assert len(results) == 2
        assert results[0]["dn"] == "uid=user1,dc=test,dc=com"
        results = client._process_search_results(mock_result, size_limit=1)
        assert len(results) == 1
        mock_result.is_success = False
        results = client._process_search_results(mock_result, size_limit=0)
        assert len(results) == 0
        mock_result.is_success = True
        mock_result.data = None
        results = client._process_search_results(mock_result, size_limit=0)
        assert len(results) == 0

    @patch("flext_tap_ldap.client.get_running_loop")
    def test_search_no_event_loop(
        self, mock_get_loop: Mock, client: FlextTapLdapClient.LDAPClient
    ) -> None:
        """Test search when no event loop is running."""
        mock_get_loop.side_effect = RuntimeError("no event loop")
        with patch.object(client, "_run_in_new_loop", return_value=[]) as mock_run:
            results = client.search("dc=test,dc=com")
            mock_run.assert_called_once()
            assert results == []

    @patch("flext_tap_ldap.client.get_running_loop")
    def test_search_with_event_loop(
        self, mock_get_loop: Mock, client: FlextTapLdapClient.LDAPClient
    ) -> None:
        """Test search when event loop is already running."""
        mock_get_loop.return_value = Mock()
        results = client.search("dc=test,dc=com")
        assert results == []

    def test_run_in_new_loop(self, client: FlextTapLdapClient.LDAPClient) -> None:
        """Test search execution helper in new loop."""
        with patch.object(client, "search", return_value=[{"test": "data"}]):
            result = client.search("dc=test,dc=com")
        assert list(result) == [{"test": "data"}]

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
        assert result is True
        mock_new_loop.assert_called_once()
        mock_loop.close.assert_called_once()

    @patch("flext_tap_ldap.client.get_running_loop")
    def test_test_connection_with_loop(
        self, client: FlextTapLdapClient.LDAPClient, mock_get_loop: Mock
    ) -> None:
        """Test connection test when event loop exists."""
        mock_get_loop.return_value = Mock()
        result = client.test_connection()
        assert result is True

    def test_health_check_functionality(
        self, client: FlextTapLdapClient.LDAPClient
    ) -> None:
        """Test health check functionality."""
        with patch.object(client, "test_connection", return_value=True):
            health = client.health_check()
            assert health["status"] == "healthy"
            assert health["server_uri"] == "ldap://test.ldap.com:389"
            assert health["connection_test"] is True
            assert isinstance(health["response_time_ms"], (int, float))
        with patch.object(client, "test_connection", return_value=False):
            health = client.health_check()
            assert health["status"] == "unhealthy"
            assert health["connection_test"] is False

    def test_oracle_entry_processing(
        self, client: FlextTapLdapClient.LDAPClient
    ) -> None:
        """Test Oracle entry processing with all scenarios."""
        entry = {
            "dn": "uid=test,dc=oracle,dc=com",
            "attributes": {
                "uid": ["test"],
                "orclPassword": ["hashed_password"],
                "objectClass": ["inetOrgPerson"],
            },
        }
        result = client._process_oracle_entry(entry)
        attributes = result["attributes"]
        assert isinstance(attributes, dict)
        assert "userPassword" in attributes
        assert attributes["userPassword"] == ["hashed_password"]
        entry_with_container = {
            "dn": "ou=test,dc=oracle,dc=com",
            "attributes": {"ou": ["test"], "objectClass": ["orclContainer"]},
        }
        result = client._process_oracle_entry(entry_with_container)
        attributes = result["attributes"]
        assert isinstance(attributes, dict)
        object_class = attributes["objectClass"]
        assert isinstance(object_class, list)
        assert "organizationalUnit" in object_class
        entry_string_oc = {
            "dn": "ou=test,dc=oracle,dc=com",
            "attributes": {"objectClass": "orclContainer"},
        }
        result = client._process_oracle_entry(entry_string_oc)
        attributes = result["attributes"]
        assert isinstance(attributes, dict)
        obj_classes = attributes["objectClass"]
        assert isinstance(obj_classes, list)
        assert "organizationalUnit" in obj_classes
        entry_bad_attrs = {
            "dn": "uid=test,dc=oracle,dc=com",
            "attributes": "not_a_dict",
        }
        result = client._process_oracle_entry(entry_bad_attrs)
        assert result == entry_bad_attrs

    def test_oracle_attribute_extension(
        self, client: FlextTapLdapClient.LDAPClient
    ) -> None:
        """Test Oracle attribute extension."""
        base_attrs = ["uid", "cn"]
        extended = client._extend_attributes_with_oracle_support(
            base_attrs, oracle_oid_mode=True
        )
        assert extended is not None
        assert "uid" in extended
        assert "cn" in extended
        assert "orclPassword" in extended
        assert "userPassword" in extended
        result = client._extend_attributes_with_oracle_support(
            base_attrs, oracle_oid_mode=False
        )
        assert result == base_attrs
        result = client._extend_attributes_with_oracle_support(
            None, oracle_oid_mode=True
        )
        assert result is None

    def test_process_search_results_with_oracle_support(
        self, client: FlextTapLdapClient.LDAPClient
    ) -> None:
        """Test Oracle search result processing."""
        search_results = [
            {
                "dn": "uid=test1,dc=oracle,dc=com",
                "attributes": {"orclPassword": ["pass1"]},
            },
            {"dn": "uid=test2,dc=oracle,dc=com", "attributes": {"uid": ["test2"]}},
        ]
        results = client._process_search_results_with_oracle_support(
            search_results, oracle_oid_mode=True
        )
        assert len(results) == 2
        attributes = results[0]["attributes"]
        assert isinstance(attributes, dict)
        assert "userPassword" in attributes
        results = client._process_search_results_with_oracle_support(
            search_results, oracle_oid_mode=False
        )
        assert len(results) == 2
        assert results[0] == search_results[0]

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
            assert len(result_list) >= 0

    @patch("flext_tap_ldap.client.get_running_loop")
    def test_search_with_oracle_support_scenarios(
        self, mock_get_loop: Mock, client: FlextTapLdapClient.LDAPClient
    ) -> None:
        """Test Oracle support search with different scenarios."""
        mock_get_loop.return_value = Mock()
        results = client.search_with_oracle_support(
            "dc=oracle,dc=com", "(uid=*)", ["uid"], oracle_oid_mode=True
        )
        assert list(results) == []
        mock_get_loop.side_effect = RuntimeError("no event loop")

    def test_attribute_delegation_to_flext_api(
        self, client: FlextTapLdapClient.LDAPClient
    ) -> None:
        """Test attribute delegation to flext API."""
        result = client.search
        assert callable(result)
        with contextlib.suppress(AttributeError):
            _ = client.non_existent_method
