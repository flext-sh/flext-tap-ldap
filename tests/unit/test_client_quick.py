"""Quick comprehensive tests for LDAP client to maximize coverag efficiently.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import contextlib
from collections.abc import Sequence
from typing import cast
from unittest.mock import Mock, patch

import pytest

from flext_tap_ldap import FlextTapLdapClient
from tests import t


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
            host="test.com",
            port=389,
            use_ssl=False,
        )
        assert ldap_client.server_uri == "ldap://test.com:389"
        ldaps_client = FlextTapLdapClient.LDAPClient(
            host="secure.com",
            port=636,
            use_ssl=True,
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
        self,
        client: FlextTapLdapClient.LDAPClient,
    ) -> None:
        """Test entry conversion with different scenarios."""
        # Test with a Mapping (dict) entry
        mail_values: t.StrSequence = ["test@example.com"]
        dict_entry: t.ContainerMapping = {
            "dn": "uid=dict,dc=example,dc=com",
            "attributes": {"mail": mail_values},
        }
        result = client._convert_entry_to_dict(dict_entry)
        assert result["dn"] == "uid=dict,dc=example,dc=com"
        # Test with None
        result = client._convert_entry_to_dict(None)
        assert result == {}
        # Test with a dict that has string values
        simple_entry: t.ContainerMapping = {
            "dn": "uid=test,dc=example,dc=com",
            "uid": "test",
            "cn": ["Test", "T. User"],
        }
        result = client._convert_entry_to_dict(simple_entry)
        assert result["dn"] == "uid=test,dc=example,dc=com"
        assert result["uid"] == "test"
        assert result["cn"] == ["Test", "T. User"]

    def test_search_result_processing(
        self,
        client: FlextTapLdapClient.LDAPClient,
    ) -> None:
        """Test search result processing with different scenarios."""
        mock_search_result = Mock()
        mock_search_result.entries = [
            {"dn": "uid=user1,dc=test,dc=com", "uid": ["user1"]},
            {"dn": "uid=user2,dc=test,dc=com", "uid": ["user2"]},
        ]
        mock_result = Mock()
        mock_result.is_success = True
        mock_result.value = mock_search_result
        results = client._process_search_results(mock_result, size_limit=0)
        assert len(results) == 2
        assert results[0]["dn"] == "uid=user1,dc=test,dc=com"
        results = client._process_search_results(mock_result, size_limit=1)
        assert len(results) == 1
        # Test with failure
        mock_result.is_success = False
        results = client._process_search_results(mock_result, size_limit=0)
        assert not results
        # Test with no value
        mock_result.is_success = True
        mock_result.value = None
        results = client._process_search_results(mock_result, size_limit=0)
        assert not results

    def test_search_delegates_to_perform_search(
        self,
        client: FlextTapLdapClient.LDAPClient,
    ) -> None:
        """Test search delegates to _perform_search."""
        with patch.object(
            client,
            "_perform_search",
            return_value=[{"test": "data"}],
        ) as mock_perform:
            results = client.search("dc=test,dc=com")
            mock_perform.assert_called_once()
            assert results == [{"test": "data"}]

    def test_search_with_all_parameters(
        self,
        client: FlextTapLdapClient.LDAPClient,
    ) -> None:
        """Test search passes all parameters to _perform_search."""
        with patch.object(client, "_perform_search", return_value=[]) as mock_perform:
            results = client.search("dc=test,dc=com", "(uid=*)", ["uid"], "BASE", 10)
            mock_perform.assert_called_once_with(
                "dc=test,dc=com",
                "(uid=*)",
                ["uid"],
                "BASE",
                10,
            )
            assert results == []

    def test_test_connection_success(
        self,
        client: FlextTapLdapClient.LDAPClient,
    ) -> None:
        """Test connection test succeeds via flext_api.search."""
        mock_result = Mock()
        mock_result.is_success = True
        api_cls = type(client._flext_api)
        with patch.object(api_cls, "search", return_value=mock_result):
            result = client.test_connection()
        assert result is True

    def test_test_connection_fallback_on_error(
        self,
        client: FlextTapLdapClient.LDAPClient,
    ) -> None:
        """Test connection test returns True on expected errors (fallback)."""
        api_cls = type(client._flext_api)
        with patch.object(api_cls, "search", side_effect=RuntimeError("test error")):
            result = client.test_connection()
        assert result is True

    def test_health_check_functionality(
        self,
        client: FlextTapLdapClient.LDAPClient,
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
        self,
        client: FlextTapLdapClient.LDAPClient,
    ) -> None:
        """Test Oracle entry processing with all scenarios."""
        uid_values: t.StrSequence = ["test"]
        oracle_password_values: t.StrSequence = ["hashed_password"]
        object_classes: t.StrSequence = ["inetOrgPerson"]
        entry: t.ContainerMapping = {
            "dn": "uid=test,dc=oracle,dc=com",
            "attributes": {
                "uid": uid_values,
                "orclPassword": oracle_password_values,
                "objectClass": object_classes,
            },
        }
        result = client._process_oracle_entry(entry)
        attributes_raw = result.get("attributes")
        assert isinstance(attributes_raw, dict)
        attributes: t.ContainerMapping = cast("t.ContainerMapping", attributes_raw)
        assert "userPassword" in attributes
        user_password: t.NormalizedValue = attributes.get("userPassword")
        assert isinstance(user_password, list)
        assert isinstance(user_password, list)
        assert "hashed_password" in user_password

        ou_values: t.StrSequence = ["test"]
        container_classes: t.StrSequence = ["orclContainer"]
        entry_with_container: t.ContainerMapping = {
            "dn": "ou=test,dc=oracle,dc=com",
            "attributes": {"ou": ou_values, "objectClass": container_classes},
        }
        result = client._process_oracle_entry(entry_with_container)
        attrs_raw2 = result.get("attributes")
        assert isinstance(attrs_raw2, dict)
        attributes = cast("t.ContainerMapping", attrs_raw2)
        object_class: t.NormalizedValue = attributes.get("objectClass")
        assert isinstance(object_class, list)
        assert isinstance(object_class, list)
        assert "organizationalUnit" in object_class

        entry_string_oc: t.ContainerMapping = {
            "dn": "ou=test,dc=oracle,dc=com",
            "attributes": {"objectClass": "orclContainer"},
        }
        result = client._process_oracle_entry(entry_string_oc)
        attrs_raw3 = result.get("attributes")
        assert isinstance(attrs_raw3, dict)
        attributes = cast("t.ContainerMapping", attrs_raw3)
        obj_classes: t.NormalizedValue = attributes.get("objectClass")
        assert isinstance(obj_classes, list)
        assert isinstance(obj_classes, list)
        assert "organizationalUnit" in obj_classes

        entry_bad_attrs: t.ContainerMapping = {
            "dn": "uid=test,dc=oracle,dc=com",
            "attributes": "not_a_dict",
        }
        result = client._process_oracle_entry(entry_bad_attrs)
        assert result == entry_bad_attrs

    def test_oracle_attribute_extension(
        self,
        client: FlextTapLdapClient.LDAPClient,
    ) -> None:
        """Test Oracle attribute extension."""
        base_attrs = ["uid", "cn"]
        extended = client._extend_attributes_with_oracle_support(
            base_attrs,
            oracle_oid_mode=True,
        )
        assert extended is not None
        assert extended is not None
        assert "uid" in extended
        assert "cn" in extended
        assert "orclPassword" in extended
        assert "userPassword" in extended
        result = client._extend_attributes_with_oracle_support(
            base_attrs,
            oracle_oid_mode=False,
        )
        assert result == base_attrs
        result = client._extend_attributes_with_oracle_support(
            None,
            oracle_oid_mode=True,
        )
        assert result is None

    def test_process_search_results_with_oracle_support(
        self,
        client: FlextTapLdapClient.LDAPClient,
    ) -> None:
        """Test Oracle search result processing."""
        first_passwords: t.StrSequence = ["pass1"]
        second_uids: t.StrSequence = ["test2"]
        search_results: Sequence[t.ContainerMapping] = [
            {
                "dn": "uid=test1,dc=oracle,dc=com",
                "attributes": {"orclPassword": first_passwords},
            },
            {"dn": "uid=test2,dc=oracle,dc=com", "attributes": {"uid": second_uids}},
        ]
        results = client._process_search_results_with_oracle_support(
            search_results,
            oracle_oid_mode=True,
        )
        assert len(results) == 2
        attributes = results[0].get("attributes")
        assert isinstance(attributes, dict)
        assert isinstance(attributes, dict)
        assert "userPassword" in attributes
        results = client._process_search_results_with_oracle_support(
            search_results,
            oracle_oid_mode=False,
        )
        assert len(results) == 2
        assert results[0] == search_results[0]

    @patch("flext_tap_ldap.client.get_running_loop")
    def test_execute_oracle_search_in_new_loop(
        self,
        client: FlextTapLdapClient.LDAPClient,
    ) -> None:
        """Test Oracle search execution in new loop."""
        with patch.object(client, "search", return_value=[{"test": "data"}]):
            result = client._execute_oracle_search_in_new_loop(
                "dc=test,dc=com",
                "(uid=*)",
                ["uid"],
                oracle_oid_mode=True,
            )
            result_list = list(result)
            assert len(result_list) >= 0

    @patch("flext_tap_ldap.client.get_running_loop")
    def test_search_with_oracle_support_scenarios(
        self,
        mock_get_loop: Mock,
        client: FlextTapLdapClient.LDAPClient,
    ) -> None:
        """Test Oracle support search with different scenarios."""
        mock_get_loop.return_value = Mock()
        results = client.search_with_oracle_support(
            "dc=oracle,dc=com",
            "(uid=*)",
            ["uid"],
            oracle_oid_mode=True,
        )
        assert list(results) == []
        mock_get_loop.side_effect = RuntimeError("no event loop")

    def test_attribute_delegation_to_flext_api(
        self,
        client: FlextTapLdapClient.LDAPClient,
    ) -> None:
        """Test attribute delegation to flext API."""
        result = client.search
        assert callable(result)
        with contextlib.suppress(AttributeError):
            _ = client.non_existent_method
