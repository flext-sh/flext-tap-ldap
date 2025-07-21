"""Tests for LDAP client."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from ldap3.core.exceptions import LDAPException

from flext_tap_ldap.client import LDAPClient


class TestLDAPClient:
    """Unit tests for LDAPClient."""

    @pytest.fixture
    def client(self) -> LDAPClient:
        return LDAPClient(
            host="test.ldap.com",
            port=389,
            bind_dn="cn=admin,dc=test,dc=com",
            password="test_password",
            use_ssl=False,
            timeout=30,
            page_size=1000,
        )

    def test_client_initialization(self, client: LDAPClient) -> None:
        assert client.host == "test.ldap.com"
        assert client.port == 389
        assert client.bind_dn == "cn=admin,dc=test,dc=com"
        assert client.password == "test_password"
        assert not client.use_ssl
        assert client.timeout == 30
        assert client.page_size == 1000

    def test_server_uri(self, client: LDAPClient) -> None:
        assert client.server_uri == "ldap://test.ldap.com:389"

        # Test with SSL
        client.use_ssl = True
        assert client.server_uri == "ldaps://test.ldap.com:389"

    @patch("flext_tap_ldap.client.Connection")
    def test_get_connection(
        self,
        mock_connection_class: MagicMock,
        client: LDAPClient,
    ) -> None:
        mock_connection = MagicMock()
        mock_connection.bound = True
        mock_connection_class.return_value = mock_connection

        with client.get_connection() as conn:
            assert conn == mock_connection

        # Verify connection was created correctly
        mock_connection_class.assert_called_once()

        # Verify unbind was called
        mock_connection.unbind.assert_called_once()

    @patch("flext_tap_ldap.client.Connection")
    @patch("flext_tap_ldap.client.Server")
    def test_search(
        self,
        _mock_server_class: MagicMock,  # noqa: PT019
        mock_connection_class: MagicMock,
        client: LDAPClient,
    ) -> None:
        # Setup mocks
        mock_entry = MagicMock()
        mock_entry.entry_dn = "uid=jdoe,ou=users,dc=test,dc=com"

        # Mock attribute access
        mock_attr = MagicMock()
        mock_attr.key = "uid"
        mock_attr.values = ["jdoe"]

        mock_entry.__iter__ = MagicMock(return_value=iter([mock_attr]))

        mock_connection = MagicMock()
        mock_connection.bound = True
        mock_connection.entries = [mock_entry]
        mock_connection.result = {"controls": {}}
        mock_connection_class.return_value = mock_connection

        # Perform search
        results = list(
            client.search(
                base_dn="dc=test,dc=com",
                search_filter="(uid=jdoe)",
                attributes=["uid", "cn", "mail"],
            ),
        )

        # Verify results
        assert len(results) == 1
        assert results[0]["dn"] == "uid=jdoe,ou=users,dc=test,dc=com"
        assert results[0]["attributes"]["uid"] == "jdoe"

        # Verify search was called correctly
        mock_connection.search.assert_called_with(
            search_base="dc=test,dc=com",
            search_filter="(uid=jdoe)",
            search_scope="SUBTREE",  # SUBTREE scope string
            attributes=["uid", "cn", "mail"],
            paged_size=1000,
        )

    @patch("flext_tap_ldap.client.Connection")
    @patch("flext_tap_ldap.client.Server")
    def test_test_connection_success(
        self,
        _mock_server_class: MagicMock,  # noqa: PT019
        mock_connection_class: MagicMock,
        client: LDAPClient,
    ) -> None:
        mock_connection = MagicMock()
        mock_connection.bound = True
        mock_connection.result = {"result": 0}
        mock_connection_class.return_value = mock_connection

        assert client.test_connection() is True

    @patch("flext_tap_ldap.client.Connection")
    @patch("flext_tap_ldap.client.Server")
    def test_test_connection_failure(
        self,
        _mock_server_class: MagicMock,  # noqa: PT019
        mock_connection_class: MagicMock,
        client: LDAPClient,
    ) -> None:
        mock_connection_class.side_effect = LDAPException("Connection failed")

        assert client.test_connection() is False
