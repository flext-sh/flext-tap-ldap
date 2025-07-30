"""Tests for LDAP client."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from unittest.mock import AsyncMock, patch

import pytest
from flext_core import FlextResult

from flext_tap_ldap.client import LDAPClient

# Constants
EXPECTED_DATA_COUNT = 3

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
        if client._config.server != "test.ldap.com":
            msg = f"Expected {'test.ldap.com'}, got {client._config.server}"
            raise AssertionError(msg)
        assert client._config.port == 389
        if client._bind_dn != "cn=REDACTED_LDAP_BIND_PASSWORD,dc=test,dc=com":
            msg = f"Expected {'cn=REDACTED_LDAP_BIND_PASSWORD,dc=test,dc=com'}, got {client._bind_dn}"
            raise AssertionError(msg)
        assert client._password == "test_password"
        assert not client._config.use_ssl
        if client._config.timeout_seconds != 30:
            msg = f"Expected {30}, got {client._config.timeout_seconds}"
            raise AssertionError(msg)
        assert client.page_size == 1000

    def test_server_uri(self, client: LDAPClient) -> None:
        if client.server_uri != "ldap://test.ldap.com:389":
            msg = f"Expected {'ldap://test.ldap.com:389'}, got {client.server_uri}"
            raise AssertionError(msg)

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
        if ssl_client.server_uri != "ldaps://test.ldap.com:389":
            msg = f"Expected {'ldaps://test.ldap.com:389'}, got {ssl_client.server_uri}"
            raise AssertionError(msg)

    @pytest.mark.asyncio
    async def test_search_async(self, client: LDAPClient) -> None:
        """Test async search using flext-ldap infrastructure."""
        # Mock the flext-ldap client
        with patch.object(
            client._flext_api,
            "search",
            new_callable=AsyncMock,
        ) as mock_search:
            # Setup mock response

            mock_entry = {
                "dn": "uid=jdoe,ou=users,dc=test,dc=com",
                "attributes": {
                    "uid": ["jdoe"],
                    "cn": ["John Doe"],
                    "mail": ["john.doe@example.com"],
                },
            }
            mock_search.return_value = FlextResult.ok([mock_entry])

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
            if len(results) != 1:
                msg = f"Expected {1}, got {len(results)}"
                raise AssertionError(msg)
            assert results[0]["dn"] == "uid=jdoe,ou=users,dc=test,dc=com"
            if results[0]["attributes"]["uid"] != ["jdoe"]:
                msg = f"Expected {['jdoe']}, got {results[0]['attributes']['uid']}"
                raise AssertionError(msg)
            assert results[0]["attributes"]["cn"] == ["John Doe"]
            if results[0]["attributes"]["mail"] != ["john.doe@example.com"]:
                msg = f"Expected {['john.doe@example.com']}, got {results[0]['attributes']['mail']}"
                raise AssertionError(msg)

    def test_test_connection_success(self, client: LDAPClient) -> None:
        # Simple test for connection test method
        # This is currently simplified in the actual implementation
        if not (client.test_connection()):
            msg = f"Expected True, got {client.test_connection()}"
            raise AssertionError(msg)

    def test_health_check(self, client: LDAPClient) -> None:
        """Test health check functionality."""
        health_result = client.health_check()

        # Verify health check response structure
        assert isinstance(health_result, dict)
        if "status" not in health_result:
            msg = f"Expected {'status'} in {health_result}"
            raise AssertionError(msg)
        assert "server_uri" in health_result
        if "connection_test" not in health_result:
            msg = f"Expected {'connection_test'} in {health_result}"
            raise AssertionError(msg)
        assert "response_time_ms" in health_result
        if health_result["server_uri"] != "ldap://test.ldap.com:389":
            msg = f"Expected {'ldap://test.ldap.com:389'}, got {health_result['server_uri']}"
            raise AssertionError(msg)

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
        if "userPassword" not in processed_entry["attributes"]:
            msg = f"Expected {'userPassword'} in {processed_entry['attributes']}"
            raise AssertionError(msg)
        if processed_entry["attributes"]["userPassword"] != ["hashed_password"]:
            msg = f"Expected {['hashed_password']}, got {processed_entry['attributes']['userPassword']}"
            raise AssertionError(msg)
        if "organizationalUnit" not in processed_entry["attributes"]["objectClass"]:
            msg = f"Expected {'organizationalUnit'} in {processed_entry['attributes']['objectClass']}"
            raise AssertionError(msg)

        # Mock the search to return one entry and test full flow
        async def mock_async_search(
            *args: Any,
            **kwargs: Any,
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
            if len(results) != 1:
                msg = f"Expected {1}, got {len(results)}"
                raise AssertionError(msg)
            result = results[0]
            # Oracle password should be mapped to userPassword
            if "userPassword" not in result["attributes"]:
                msg = f"Expected {'userPassword'} in {result['attributes']}"
                raise AssertionError(msg)
            # Object class should include organizationalUnit
            if "organizationalUnit" not in result["attributes"]["objectClass"]:
                msg = f"Expected {'organizationalUnit'} in {result['attributes']['objectClass']}"
                raise AssertionError(msg)
