"""Pytest configuration and fixtures for tap-ldap tests."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest
from ldap3 import MOCK_SYNC, Connection, Server
from tap_ldap.client import LDAPClient

if TYPE_CHECKING:
    from collections.abc import Generator


@pytest.fixture
def mock_ldap_config() -> dict[str, Any]:
    """Provide test LDAP configuration."""
    return {
        "host": "test.ldap.com",
        "port": 389,
        "bind_dn": "cn=REDACTED_LDAP_BIND_PASSWORD,dc=test,dc=com",
        "password": "test_password",
        "base_dn": "dc=test,dc=com",
        "use_ssl": False,
        "timeout": 30,
        "page_size": 100,
        "user_filter": "(objectClass=inetOrgPerson)",
        "group_filter": "(objectClass=groupOfNames)",
    }


@pytest.fixture
def mock_ldap_connection() -> Generator[Connection]:
    """Create mock LDAP connection with test data."""
    # Create mock server and connection
    server = Server("test.ldap.com", get_info=MOCK_SYNC)
    connection = Connection(server, client_strategy=MOCK_SYNC, auto_bind=True)

    # Add test entries
    connection.entries.clear()

    # Add base DN
    connection.strategy.add_entry(
        "dc=test,dc=com",
        {
            "objectClass": ["domain", "top"],
            "dc": "test",
        },
    )

    # Add OUs
    connection.strategy.add_entry(
        "ou=users,dc=test,dc=com",
        {
            "objectClass": ["organizationalUnit", "top"],
            "ou": "users",
        },
    )

    connection.strategy.add_entry(
        "ou=groups,dc=test,dc=com",
        {
            "objectClass": ["organizationalUnit", "top"],
            "ou": "groups",
        },
    )

    # Add users
    connection.strategy.add_entry(
        "uid=jdoe,ou=users,dc=test,dc=com",
        {
            "objectClass": ["inetOrgPerson", "organizationalPerson", "person", "top"],
            "uid": "jdoe",
            "cn": "John Doe",
            "sn": "Doe",
            "givenName": "John",
            "mail": "jdoe@test.com",
            "userPassword": "{SSHA}encrypted",
            "createTimestamp": "20230101120000Z",
            "modifyTimestamp": "20240101120000Z",
        },
    )

    connection.strategy.add_entry(
        "uid=asmith,ou=users,dc=test,dc=com",
        {
            "objectClass": ["inetOrgPerson", "organizationalPerson", "person", "top"],
            "uid": "asmith",
            "cn": "Alice Smith",
            "sn": "Smith",
            "givenName": "Alice",
            "mail": "asmith@test.com",
            "memberOf": ["cn=developers,ou=groups,dc=test,dc=com"],
            "createTimestamp": "20230201120000Z",
            "modifyTimestamp": "20240201120000Z",
        },
    )

    # Add groups
    connection.strategy.add_entry(
        "cn=developers,ou=groups,dc=test,dc=com",
        {
            "objectClass": ["groupOfNames", "top"],
            "cn": "developers",
            "description": "Development team",
            "member": [
                "uid=asmith,ou=users,dc=test,dc=com",
                "uid=jdoe,ou=users,dc=test,dc=com",
            ],
            "createTimestamp": "20230101120000Z",
            "modifyTimestamp": "20240101120000Z",
        },
    )

    yield connection

    connection.unbind()


@pytest.fixture
def mock_ldap_client(mock_ldap_config: dict[str, Any]) -> LDAPClient:
    """Create mock LDAP client."""
    return LDAPClient(**mock_ldap_config)


@pytest.fixture
def sample_catalog() -> dict[str, Any]:
    """Provide sample Singer catalog."""
    return {
        "streams": [
            {
                "tap_stream_id": "users",
                "replication_method": "INCREMENTAL",
                "replication_key": "modifyTimestamp",
                "schema": {
                    "properties": {
                        "dn": {"type": "string"},
                        "uid": {"type": "string"},
                        "cn": {"type": "string"},
                        "mail": {"type": ["string", "null"]},
                        "modifyTimestamp": {"type": "string", "format": "date-time"},
                    },
                },
                "metadata": [
                    {
                        "breadcrumb": [],
                        "metadata": {
                            "inclusion": "available",
                            "selected": True,
                            "replication-method": "INCREMENTAL",
                            "replication-key": "modifyTimestamp",
                        },
                    },
                ],
            },
            {
                "tap_stream_id": "groups",
                "replication_method": "FULL_TABLE",
                "schema": {
                    "properties": {
                        "dn": {"type": "string"},
                        "cn": {"type": "string"},
                        "member": {"type": "array", "items": {"type": "string"}},
                    },
                },
                "metadata": [
                    {
                        "breadcrumb": [],
                        "metadata": {
                            "inclusion": "available",
                            "selected": True,
                            "replication-method": "FULL_TABLE",
                        },
                    },
                ],
            },
        ],
    }


@pytest.fixture
def sample_state() -> dict[str, Any]:
    """Provide sample Singer state."""
    return {
        "bookmarks": {
            "users": {
                "replication_key_value": "20240101000000Z",
                "replication_key": "modifyTimestamp",
            },
        },
    }
