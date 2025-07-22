"""Pytest configuration and fixtures for flext-tap-ldap tests.

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT.
"""
from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

import pytest
from ldap3 import MOCK_SYNC, Connection, Server

from flext_tap_ldap.client import LDAPClient

if TYPE_CHECKING:
    from collections.abc import Generator
# Set test environment
os.environ["FLEXT_ENV"] = "testing"
os.environ["FLEXT_DEBUG"] = "true"


@pytest.fixture
def mock_ldap_config() -> dict[str, Any]:
    """Mock LDAP configuration for testing."""
    return {
        "host": "test.ldap.com",
        "port": 389,
        "bind_dn": "cn=admin,dc=test,dc=com",
        "password": "test_password",
        "base_dn": "dc=test,dc=com",
        "use_ssl": False,
        "timeout": 30,
        "page_size": 100,
        "user_filter": "(object_class=inetOrgPerson)",
        "group_filter": "(object_class=groupOfNames)",
    }


@pytest.fixture
def mock_ldap_connection() -> Generator[Connection]:
    """Mock LDAP connection with test data."""
    # Create mock server and connection
    server = Server("test.ldap.com", get_info="NO_INFO")
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
    connection.unbind()  # type: ignore[no-untyped-call]


@pytest.fixture
def mock_ldap_client(mock_ldap_config: dict[str, Any]) -> LDAPClient:
    """Mock LDAP client for testing."""
    return LDAPClient(**mock_ldap_config)


@pytest.fixture
def sample_catalog() -> dict[str, Any]:
    """Sample Singer catalog for testing."""
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
    """Sample Singer state for testing."""
    return {
        "bookmarks": {
            "users": {
                "replication_key_value": "20240101000000Z",
                "replication_key": "modifyTimestamp",
            },
        },
    }


# Pytest configuration
def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers",
        "unit: mark test as unit test (fast, isolated)",
    )
    config.addinivalue_line(
        "markers",
        "integration: mark test as integration test (may require external services)",
    )
    config.addinivalue_line(
        "markers",
        "slow: mark test as slow running",
    )
    config.addinivalue_line(
        "markers",
        "ldap: mark test as LDAP-related",
    )
    config.addinivalue_line(
        "markers",
        "singer: mark test as Singer protocol-related",
    )


def pytest_collection_modifyitems(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    """Modify test collection to add markers based on test location."""
    for item in items:
        # Add unit marker to all tests in unit directory
        if "/unit/" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        # Add integration marker to all tests in integration directory
        elif "/integration/" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
            item.add_marker(pytest.mark.slow)
        # Add e2e marker to all tests in e2e directory
        elif "/e2e/" in str(item.fspath):
            item.add_marker(pytest.mark.slow)
        # Add LDAP marker to LDAP-related tests
        if "ldap" in item.name.lower():
            item.add_marker(pytest.mark.ldap)
        # Add Singer marker to Singer-related tests
        if "singer" in item.name.lower() or "tap" in item.name.lower():
            item.add_marker(pytest.mark.singer)
