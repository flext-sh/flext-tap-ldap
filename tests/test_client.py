"""Tests for LDAP client."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from unittest.mock import AsyncMock, patch

import pytest

from flext_tap_ldap.client import LDAPClient

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator


class TestLDAPClient:
    """Unit tests for LDAPClient."""

    @pytest.fixture
    def client(self) -> LDAPClient:
        return LDAPClient(
            host="test.ldap.com",
            port=389,
            bind_dn="cn=REDACTED_LDAP_BIND_PASSWORD,dc=test,dc=com",
            password="test_password",
            use_ssl=False,
            timeout=30,
            page_size=1000,
        )

    def test_client_initialization(self, client: LDAPClient) -> None:
        # Test initialization of flext-ldap wrapper client
        assert client._config.server == "test.ldap.com"
        assert client._config.port == 389
        assert client._bind_dn == "cn=REDACTED_LDAP_BIND_PASSWORD,dc=test,dc=com"
        assert client._password == "test_password"
        assert not client._config.use_ssl
        assert client._config.timeout_seconds == 30
        assert client.page_size == 1000

    def test_server_uri(self, client: LDAPClient) -> None:
        assert client.server_uri == "ldap://test.ldap.com:389"

        # Test with SSL by creating a new client with SSL enabled
        ssl_client = LDAPClient(
            host="test.ldap.com",
            port=389,
            bind_dn="cn=REDACTED_LDAP_BIND_PASSWORD,dc=test,dc=com",
            password="test_password",
            use_ssl=True,
            timeout=30,
            page_size=1000,
        )
        assert ssl_client.server_uri == "ldaps://test.ldap.com:389"

    @pytest.mark.asyncio
    async def test_search_async(self, client: LDAPClient) -> None:
        """Test async search using flext-ldap infrastructure."""
        # Mock the flext-ldap client
        with patch.object(
            client._flext_client, "search", new_callable=AsyncMock,
        ) as mock_search:
            # Setup mock response
            from flext_core.domain.shared_types import ServiceResult

            mock_entry = {
                "dn": "uid=jdoe,ou=users,dc=test,dc=com",
                "attributes": {
                    "uid": ["jdoe"],
                    "cn": ["John Doe"],
                    "mail": ["john.doe@example.com"],
                },
            }
            mock_search.return_value = ServiceResult.ok([mock_entry])

            # Perform search using async list comprehension for performance
            results: list[dict[str, Any]] = [
                result
                async for result in client.search(
                    base_dn="dc=test,dc=com",
                    search_filter="(uid=jdoe)",
                    attributes=["uid", "cn", "mail"],
                )
            ]

            # Verify results
            assert len(results) == 1
            assert results[0]["dn"] == "uid=jdoe,ou=users,dc=test,dc=com"
            assert results[0]["attributes"]["uid"] == ["jdoe"]
            assert results[0]["attributes"]["cn"] == ["John Doe"]
            assert results[0]["attributes"]["mail"] == ["john.doe@example.com"]

    def test_test_connection_success(self, client: LDAPClient) -> None:
        # Simple test for connection test method
        # This is currently simplified in the actual implementation
        assert client.test_connection() is True

    def test_health_check(self, client: LDAPClient) -> None:
        """Test health check functionality."""
        health_result = client.health_check()

        # Verify health check response structure
        assert isinstance(health_result, dict)
        assert "status" in health_result
        assert "server_uri" in health_result
        assert "connection_test" in health_result
        assert "response_time_ms" in health_result
        assert health_result["server_uri"] == "ldap://test.ldap.com:389"

    def test_search_with_oracle_support(self, client: LDAPClient) -> None:
        """Test search with Oracle OID support."""
        # Test the Oracle processing logic directly with mock data
        mock_entry = {
            "dn": "uid=jdoe,ou=users,dc=oracle,dc=com",
            "attributes": {
                "uid": ["jdoe"],
                "orclPassword": ["hashed_password"],
                "objectClass": ["orclContainer"],
            },
        }

        # Test Oracle-specific processing directly
        processed_entry = client._process_oracle_entry(mock_entry)

        # Verify Oracle-specific processing occurred
        assert "userPassword" in processed_entry["attributes"]
        assert processed_entry["attributes"]["userPassword"] == ["hashed_password"]
        assert "organizationalUnit" in processed_entry["attributes"]["objectClass"]

        # Mock the search to return one entry and test full flow
        async def mock_async_search(
            *args: Any, **kwargs: Any,
        ) -> AsyncGenerator[dict[str, Any]]:
            yield mock_entry

        with patch.object(client, "search", mock_async_search):
            results = list(
                client.search_with_oracle_support(
                    base_dn="dc=oracle,dc=com",
                    search_filter="(uid=jdoe)",
                    oracle_oid_mode=True,
                ),
            )

            # Verify Oracle-specific processing occurred
            assert len(results) == 1
            result = results[0]
            # Oracle password should be mapped to userPassword
            assert "userPassword" in result["attributes"]
            # Object class should include organizationalUnit
            assert "organizationalUnit" in result["attributes"]["objectClass"]
