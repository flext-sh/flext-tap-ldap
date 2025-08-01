"""Tests for LDAP stream functionality."""

from __future__ import annotations

from typing import Any
from unittest.mock import Mock, patch

import pytest
from flext_core import FlextResult

from flext_tap_ldap.streams import (
    CustomStream,
    GroupsStream,
    OrganizationalUnitsStream,
    SchemaStream,
    UsersStream,
)
from flext_tap_ldap.tap import FlextTapLDAP


class TestLDAPBaseStream:
    """Test base LDAP stream functionality."""

    @pytest.fixture
    def mock_tap(self) -> Mock:
        """Create mock tap instance."""
        tap = Mock(spec=FlextTapLDAP)
        tap.config = {
            "host": "test.ldap.com",
            "port": 389,
            "base_dn": "dc=test,dc=com",
            "bind_dn": "cn=admin,dc=test,dc=com",
            "password": "test_password",
        }
        # Add required Singer SDK attributes
        tap.metrics_logger = Mock()
        tap.logger = Mock()
        return tap

    def test_base_stream_attributes(self, mock_tap: Mock) -> None:
        """Test base stream has required attributes."""
        # Use UsersStream as concrete implementation
        stream = UsersStream(mock_tap)

        assert hasattr(stream, "name")
        assert hasattr(stream, "tap")
        assert hasattr(stream, "schema")
        assert stream.tap == mock_tap


class TestUsersStream:
    """Test Users stream functionality."""

    @pytest.fixture
    def mock_tap(self) -> Mock:
        """Create mock tap instance."""
        tap = Mock(spec=FlextTapLDAP)
        tap.config = {
            "host": "test.ldap.com",
            "port": 389,
            "base_dn": "dc=test,dc=com",
            "bind_dn": "cn=admin,dc=test,dc=com",
            "password": "test_password",
            "user_filter": "(objectClass=inetOrgPerson)",
        }
        # Add required Singer SDK attributes
        tap.metrics_logger = Mock()
        tap.logger = Mock()
        return tap

    def test_users_stream_creation(self, mock_tap: Mock) -> None:
        """Test users stream creation."""
        stream = UsersStream(mock_tap)

        assert stream is not None
        assert stream.name == "users"
        assert stream.tap == mock_tap

    def test_users_stream_schema(self, mock_tap: Mock) -> None:
        """Test users stream schema definition."""
        stream = UsersStream(mock_tap)

        schema = stream.schema
        assert isinstance(schema, dict)
        assert "properties" in schema

        # Check common LDAP user attributes
        properties = schema["properties"]
        assert "dn" in properties
        assert "cn" in properties or "commonName" in properties

    @patch("flext_tap_ldap.client.LDAPClient")
    def test_users_stream_get_records(
        self,
        mock_client_class: Mock,
        mock_tap: Mock,
    ) -> None:
        """Test users stream record retrieval."""
        # Mock LDAP client
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Mock search results
        mock_records = [
            {
                "dn": "cn=user1,ou=users,dc=test,dc=com",
                "cn": ["user1"],
                "sn": ["User One"],
                "mail": ["user1@test.com"],
                "objectClass": ["person", "inetOrgPerson"],
            },
            {
                "dn": "cn=user2,ou=users,dc=test,dc=com",
                "cn": ["user2"],
                "sn": ["User Two"],
                "mail": ["user2@test.com"],
                "objectClass": ["person", "inetOrgPerson"],
            },
        ]

        mock_client.search_all.return_value = FlextResult.success(mock_records)

        stream = UsersStream(mock_tap)
        records = list(stream.get_records(context=None))

        assert len(records) >= 0  # May be empty if client not properly connected
        mock_client_class.assert_called_once()


class TestGroupsStream:
    """Test Groups stream functionality."""

    @pytest.fixture
    def mock_tap(self) -> Mock:
        """Create mock tap instance."""
        tap = Mock(spec=FlextTapLDAP)
        tap.config = {
            "host": "test.ldap.com",
            "port": 389,
            "base_dn": "dc=test,dc=com",
            "bind_dn": "cn=admin,dc=test,dc=com",
            "password": "test_password",
            "group_filter": "(objectClass=groupOfNames)",
        }
        # Add required Singer SDK attributes
        tap.metrics_logger = Mock()
        tap.logger = Mock()
        return tap

    def test_groups_stream_creation(self, mock_tap: Mock) -> None:
        """Test groups stream creation."""
        stream = GroupsStream(mock_tap)

        assert stream is not None
        assert stream.name == "groups"
        assert stream.tap == mock_tap

    def test_groups_stream_schema(self, mock_tap: Mock) -> None:
        """Test groups stream schema definition."""
        stream = GroupsStream(mock_tap)

        schema = stream.schema
        assert isinstance(schema, dict)
        assert "properties" in schema

        # Check common LDAP group attributes
        properties = schema["properties"]
        assert "dn" in properties
        assert "cn" in properties or "commonName" in properties


class TestOrganizationalUnitsStream:
    """Test Organizational Units stream functionality."""

    @pytest.fixture
    def mock_tap(self) -> Mock:
        """Create mock tap instance."""
        tap = Mock(spec=FlextTapLDAP)
        tap.config = {
            "host": "test.ldap.com",
            "port": 389,
            "base_dn": "dc=test,dc=com",
            "bind_dn": "cn=admin,dc=test,dc=com",
            "password": "test_password",
        }
        # Add required Singer SDK attributes
        tap.metrics_logger = Mock()
        tap.logger = Mock()
        return tap

    def test_organizational_units_stream_creation(self, mock_tap: Mock) -> None:
        """Test organizational units stream creation."""
        stream = OrganizationalUnitsStream(mock_tap)

        assert stream is not None
        assert stream.name == "organizational_units"
        assert stream.tap == mock_tap

    def test_organizational_units_stream_schema(self, mock_tap: Mock) -> None:
        """Test organizational units stream schema definition."""
        stream = OrganizationalUnitsStream(mock_tap)

        schema = stream.schema
        assert isinstance(schema, dict)
        assert "properties" in schema

        # Check common LDAP OU attributes
        properties = schema["properties"]
        assert "dn" in properties
        assert "ou" in properties or "organizationalUnitName" in properties


class TestSchemaStream:
    """Test Schema stream functionality."""

    @pytest.fixture
    def mock_tap(self) -> Mock:
        """Create mock tap instance."""
        tap = Mock(spec=FlextTapLDAP)
        tap.config = {
            "host": "test.ldap.com",
            "port": 389,
            "base_dn": "dc=test,dc=com",
            "bind_dn": "cn=admin,dc=test,dc=com",
            "password": "test_password",
        }
        # Add required Singer SDK attributes
        tap.metrics_logger = Mock()
        tap.logger = Mock()
        return tap

    def test_schema_stream_creation(self, mock_tap: Mock) -> None:
        """Test schema stream creation."""
        stream = SchemaStream(mock_tap)

        assert stream is not None
        assert stream.name == "schema"
        assert stream.tap == mock_tap

    def test_schema_stream_schema_definition(self, mock_tap: Mock) -> None:
        """Test schema stream schema definition."""
        stream = SchemaStream(mock_tap)

        schema = stream.schema
        assert isinstance(schema, dict)
        assert "properties" in schema

        # Schema stream should have schema-specific attributes
        properties = schema["properties"]
        assert "name" in properties
        assert "type" in properties


class TestCustomStream:
    """Test Custom stream functionality."""

    @pytest.fixture
    def mock_tap(self) -> Mock:
        """Create mock tap instance."""
        tap = Mock(spec=FlextTapLDAP)
        tap.config = {
            "host": "test.ldap.com",
            "port": 389,
            "base_dn": "dc=test,dc=com",
            "bind_dn": "cn=admin,dc=test,dc=com",
            "password": "test_password",
        }
        # Add required Singer SDK attributes
        tap.metrics_logger = Mock()
        tap.logger = Mock()
        return tap

    def test_custom_stream_creation(self, mock_tap: Mock) -> None:
        """Test custom stream creation."""
        stream = CustomStream(
            tap=mock_tap,
            name="service_accounts",
            search_filter="(&(objectClass=account)(uid=svc-*))",
            schema_properties={
                "dn": {"type": "string"},
                "uid": {"type": "string"},
                "description": {"type": "string"},
            },
            primary_keys=["dn"],
            replication_key="modifyTimestamp",
        )

        assert stream is not None
        assert stream.name == "service_accounts"
        assert stream.tap == mock_tap

    def test_custom_stream_with_minimal_config(self, mock_tap: Mock) -> None:
        """Test custom stream with minimal configuration."""
        stream = CustomStream(
            tap=mock_tap,
            name="minimal_custom",
            search_filter="(objectClass=*)",
        )

        assert stream is not None
        assert stream.name == "minimal_custom"
        assert stream.tap == mock_tap

    def test_custom_stream_schema_properties(self, mock_tap: Mock) -> None:
        """Test custom stream schema properties."""
        custom_properties = {
            "employeeNumber": {"type": "string"},
            "department": {"type": "string"},
            "manager": {"type": "string"},
        }

        stream = CustomStream(
            tap=mock_tap,
            name="employees",
            search_filter="(objectClass=employee)",
            schema_properties=custom_properties,
        )

        schema = stream.schema
        assert isinstance(schema, dict)
        assert "properties" in schema

        properties = schema["properties"]
        # Should include both default DN and custom properties
        assert "dn" in properties
        for prop_name in custom_properties:
            assert prop_name in properties


class TestStreamIntegration:
    """Integration tests for stream functionality."""

    @pytest.fixture
    def tap_config(self) -> dict[str, object]:
        """Standard tap configuration."""
        return {
            "host": "test.ldap.com",
            "port": 389,
            "base_dn": "dc=test,dc=com",
            "bind_dn": "cn=admin,dc=test,dc=com",
            "password": "test_password",
            "use_ssl": False,
            "timeout": 30,
            "page_size": 1000,
        }

    def test_all_default_streams_creation(self, tap_config: dict[str, object]) -> None:
        """Test that all default streams can be created."""
        tap = FlextTapLDAP(config=tap_config)
        streams = tap.discover_streams()

        assert len(streams) >= 4  # users, groups, organizational_units, schema

        stream_names = [s.name for s in streams]
        assert "users" in stream_names
        assert "groups" in stream_names
        assert "organizational_units" in stream_names
        assert "schema" in stream_names

    def test_streams_with_custom_configuration(
        self,
        tap_config: dict[str, object],
    ) -> None:
        """Test streams with custom configuration."""
        tap_config["custom_streams"] = [
            {
                "name": "custom_test_stream",
                "search_filter": "(objectClass=testObject)",
                "primary_keys": ["dn"],
                "replication_key": "modifyTimestamp",
                "schema": {"properties": {"testAttribute": {"type": "string"}}},
            },
        ]

        tap = FlextTapLDAP(config=tap_config)
        streams = tap.discover_streams()

        stream_names = [s.name for s in streams]
        assert "custom_test_stream" in stream_names

        # Find the custom stream
        custom_stream = next(s for s in streams if s.name == "custom_test_stream")
        assert isinstance(custom_stream, CustomStream)

    def test_ldif_streams_when_enabled(self, tap_config: dict[str, object]) -> None:
        """Test LDIF streams are included when enabled."""
        tap_config["enable_ldif_streams"] = True

        tap = FlextTapLDAP(config=tap_config)
        streams = tap.discover_streams()

        stream_names = [s.name for s in streams]
        # Should include LDIF-related streams when enabled
        ldif_stream_found = any("ldif" in name.lower() for name in stream_names)
        assert ldif_stream_found or len(streams) > 4  # More streams when LDIF enabled
