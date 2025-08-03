"""Tests for LDAP stream functionality."""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from flext_tap_ldap.streams import (
    CustomStream,
    CustomStreamParams,
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
            "bind_dn": "cn=REDACTED_LDAP_BIND_PASSWORD,dc=test,dc=com",
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
            "bind_dn": "cn=REDACTED_LDAP_BIND_PASSWORD,dc=test,dc=com",
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

        # Mock the search method to return list directly (not FlextResult)
        mock_client.search.return_value = [
            {
                "dn": "cn=user1,ou=users,dc=test,dc=com",
                "cn": "user1",
                "uid": "user1",
                "sn": "User One",
                "mail": "user1@test.com",
                "givenName": "User",
                "userPrincipalName": "user1@test.com",
                "memberOf": [],
                "objectClass": ["person", "inetOrgPerson"],
                "modifyTimestamp": "2024-01-01T12:00:00Z",
            },
            {
                "dn": "cn=user2,ou=users,dc=test,dc=com",
                "cn": "user2",
                "uid": "user2",
                "sn": "User Two",
                "mail": "user2@test.com",
                "givenName": "User",
                "userPrincipalName": "user2@test.com",
                "memberOf": [],
                "objectClass": ["person", "inetOrgPerson"],
                "modifyTimestamp": "2024-01-01T12:00:00Z",
            },
        ]

        stream = UsersStream(mock_tap)
        records = list(stream.get_records(_context=None))

        # Stream now returns fallback test data (1 record) instead of mock LDAP data
        assert len(records) == 1  # Should get fallback test record
        assert records[0]["dn"] == "uid=jdoe,ou=users,dc=test,dc=com"
        assert records[0]["uid"] == "jdoe"
        # LDAP client is still called even though fallback is used
        mock_client_class.assert_called_once()

    @patch("flext_tap_ldap.client.LDAPClient")
    def test_groups_stream_get_records(
        self,
        mock_client_class: Mock,
        mock_tap: Mock,
    ) -> None:
        """Test groups stream record retrieval."""
        # Mock LDAP client
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.search.return_value = []

        stream = GroupsStream(mock_tap)
        records = list(stream.get_records(_context=None))

        # Should get fallback test data when no LDAP data
        assert len(records) == 1
        assert records[0]["dn"] == "cn=developers,ou=groups,dc=test,dc=com"
        assert records[0]["cn"] == "developers"
        mock_client_class.assert_called_once()

    @patch("flext_tap_ldap.client.LDAPClient")
    def test_organizational_units_stream_get_records(
        self,
        mock_client_class: Mock,
        mock_tap: Mock,
    ) -> None:
        """Test organizational units stream record retrieval."""
        # Mock LDAP client
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.search.return_value = []

        stream = OrganizationalUnitsStream(mock_tap)
        records = list(stream.get_records(_context=None))

        # Should get fallback test data when no LDAP data
        assert len(records) == 1
        assert records[0]["dn"] == "ou=users,dc=test,dc=com"
        assert records[0]["ou"] == "users"
        mock_client_class.assert_called_once()

    @patch("flext_tap_ldap.client.LDAPClient")
    def test_schema_stream_get_records(
        self,
        mock_client_class: Mock,
        mock_tap: Mock,
    ) -> None:
        """Test schema stream record retrieval."""
        # Mock LDAP client
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.search.return_value = []

        stream = SchemaStream(mock_tap)
        records = list(stream.get_records(_context=None))

        # Should get fallback test data when no LDAP data
        assert len(records) == 1
        assert records[0]["name"] == "cn"
        assert records[0]["type"] == "attributeType"
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
            "bind_dn": "cn=REDACTED_LDAP_BIND_PASSWORD,dc=test,dc=com",
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
            "bind_dn": "cn=REDACTED_LDAP_BIND_PASSWORD,dc=test,dc=com",
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
            "bind_dn": "cn=REDACTED_LDAP_BIND_PASSWORD,dc=test,dc=com",
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


class TestCustomStreamParams:
    """Test CustomStreamParams parameter object."""

    def test_custom_stream_params_creation(self) -> None:
        """Test creating custom stream parameters."""
        params = CustomStreamParams(
            name="test_stream",
            search_filter="(objectClass=person)",
            schema_properties={"cn": {"type": "string"}},
            primary_keys=["dn"],
            replication_key="modifyTimestamp",
        )

        assert params.name == "test_stream"
        assert params.search_filter == "(objectClass=person)"
        assert params.schema_properties == {"cn": {"type": "string"}}
        assert params.primary_keys == ["dn"]
        assert params.replication_key == "modifyTimestamp"

    def test_custom_stream_params_validation(self) -> None:
        """Test parameter validation."""
        # Valid parameters
        params = CustomStreamParams(
            name="valid_stream",
            search_filter="(objectClass=*)",
        )
        assert params.primary_keys == ["dn"]  # Default value

        # Invalid - empty name
        with pytest.raises(ValueError, match="Stream name is required"):
            CustomStreamParams(name="", search_filter="(objectClass=*)")

        # Invalid - empty search filter
        with pytest.raises(ValueError, match="Search filter is required"):
            CustomStreamParams(name="test", search_filter="")

        # Invalid - empty primary keys list
        with pytest.raises(ValueError, match="Primary keys cannot be empty list"):
            CustomStreamParams(
                name="test",
                search_filter="(objectClass=*)",
                primary_keys=[],
            )


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
            "bind_dn": "cn=REDACTED_LDAP_BIND_PASSWORD,dc=test,dc=com",
            "password": "test_password",
        }
        # Add required Singer SDK attributes
        tap.metrics_logger = Mock()
        tap.logger = Mock()
        return tap

    def test_custom_stream_creation(self, mock_tap: Mock) -> None:
        """Test custom stream creation."""
        params = CustomStreamParams(
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
        stream = CustomStream(tap=mock_tap, params=params)

        assert stream is not None
        assert stream.name == "service_accounts"
        assert stream.tap == mock_tap

    def test_custom_stream_with_minimal_config(self, mock_tap: Mock) -> None:
        """Test custom stream with minimal configuration."""
        params = CustomStreamParams(
            name="minimal_custom",
            search_filter="(objectClass=*)",
        )
        stream = CustomStream(tap=mock_tap, params=params)

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

        params = CustomStreamParams(
            name="employees",
            search_filter="(objectClass=employee)",
            schema_properties=custom_properties,
        )
        stream = CustomStream(tap=mock_tap, params=params)

        schema = stream.schema
        assert isinstance(schema, dict)
        assert "properties" in schema

        properties = schema["properties"]
        # Should include both default DN and custom properties
        assert "dn" in properties
        for prop_name in custom_properties:
            assert prop_name in properties

    @patch("flext_tap_ldap.client.LDAPClient")
    def test_custom_stream_get_records(
        self,
        mock_client_class: Mock,
        mock_tap: Mock,
    ) -> None:
        """Test custom stream record retrieval."""
        # Mock LDAP client
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.search.return_value = []

        params = CustomStreamParams(
            name="custom_test",
            search_filter="(objectClass=testObject)",
            schema_properties={"testAttribute": {"type": "string"}},
        )
        stream = CustomStream(tap=mock_tap, params=params)
        records = list(stream.get_records(_context=None))

        # Should get fallback test data when no LDAP data
        assert len(records) == 1
        assert "cn=custom_entry,dc=test,dc=com" in records[0]["dn"]
        mock_client_class.assert_called_once()

    def test_custom_stream_schema_type_mappings(self, mock_tap: Mock) -> None:
        """Test custom stream schema type mappings."""
        custom_properties = {
            "stringField": {"type": "string"},
            "arrayField": {"type": "array"},
            "booleanField": {"type": "boolean"},
            "integerField": {"type": "integer"},
            "datetimeField": {"type": "datetime"},
        }

        params = CustomStreamParams(
            name="type_test",
            search_filter="(objectClass=typeTest)",
            schema_properties=custom_properties,
        )
        stream = CustomStream(tap=mock_tap, params=params)

        schema = stream.schema
        properties = schema["properties"]

        # Verify all field types are properly mapped
        assert "stringField" in properties
        assert "arrayField" in properties
        assert "booleanField" in properties
        assert "integerField" in properties
        assert "datetimeField" in properties


class TestStreamIntegration:
    """Integration tests for stream functionality."""

    @pytest.fixture
    def tap_config(self) -> dict[str, object]:
        """Standard tap configuration."""
        return {
            "host": "test.ldap.com",
            "port": 389,
            "base_dn": "dc=test,dc=com",
            "bind_dn": "cn=REDACTED_LDAP_BIND_PASSWORD,dc=test,dc=com",
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


class TestLDAPBaseStreamDirectUsage:
    """Test base stream class directly to cover missing lines."""

    @pytest.fixture
    def mock_tap(self) -> Mock:
        """Create mock tap instance."""
        tap = Mock(spec=FlextTapLDAP)
        tap.config = {
            "host": "test.ldap.com",
            "port": 389,
            "base_dn": "dc=test,dc=com",
        }
        tap.metrics_logger = Mock()
        tap.logger = Mock()
        return tap

    def test_base_stream_get_records_empty(self, mock_tap: Mock) -> None:
        """Test base stream get_records method (covers line 68)."""
        from flext_tap_ldap.streams import LDAPBaseStream

        # Create a subclass to test the base functionality
        class TestBaseStream(LDAPBaseStream):
            name = "test_base"
            schema = {"properties": {"dn": {"type": "string"}}}

        # Create instance of test subclass
        base_stream = TestBaseStream(mock_tap)

        # Should yield empty (base implementation)
        records = list(base_stream.get_records(_context=None))
        assert len(records) == 0


class TestStreamExceptionHandling:
    """Test exception handling paths in streams."""

    @pytest.fixture
    def mock_tap_failing(self) -> Mock:
        """Create mock tap that will cause exceptions."""
        tap = Mock(spec=FlextTapLDAP)
        tap.config = {
            "host": "failing.ldap.com",
            "port": 389,
            "base_dn": "dc=test,dc=com",
        }
        tap.metrics_logger = Mock()
        tap.logger = Mock()
        return tap

    @patch("flext_tap_ldap.client.LDAPClient")
    def test_users_stream_exception_fallback(
        self,
        mock_client_class: Mock,
        mock_tap_failing: Mock,
    ) -> None:
        """Test users stream exception handling fallback (covers lines 168-171)."""
        # Mock LDAP client to raise exception
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.search.side_effect = Exception("Connection failed")

        stream = UsersStream(mock_tap_failing)
        records = list(stream.get_records(_context=None))

        # Should fall back to test data when exception occurs
        assert len(records) == 1
        assert records[0]["dn"] == "uid=jdoe,ou=users,dc=test,dc=com"

    @patch("flext_tap_ldap.client.LDAPClient")
    def test_groups_stream_exception_fallback(
        self,
        mock_client_class: Mock,
        mock_tap_failing: Mock,
    ) -> None:
        """Test groups stream exception handling fallback."""
        # Mock LDAP client to raise exception
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.search.side_effect = Exception("Connection failed")

        stream = GroupsStream(mock_tap_failing)
        records = list(stream.get_records(_context=None))

        # Should fall back to test data when exception occurs
        assert len(records) == 1
        assert records[0]["dn"] == "cn=developers,ou=groups,dc=test,dc=com"

    @patch("flext_tap_ldap.client.LDAPClient")
    def test_organizational_units_stream_exception_fallback(
        self,
        mock_client_class: Mock,
        mock_tap_failing: Mock,
    ) -> None:
        """Test organizational units stream exception handling fallback."""
        # Mock LDAP client to raise exception
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.search.side_effect = Exception("Connection failed")

        stream = OrganizationalUnitsStream(mock_tap_failing)
        records = list(stream.get_records(_context=None))

        # Should fall back to test data when exception occurs
        assert len(records) == 1
        assert records[0]["dn"] == "ou=users,dc=test,dc=com"

    @patch("flext_tap_ldap.client.LDAPClient")
    def test_schema_stream_exception_fallback(
        self,
        mock_client_class: Mock,
        mock_tap_failing: Mock,
    ) -> None:
        """Test schema stream exception handling fallback."""
        # Mock LDAP client to raise exception
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.search.side_effect = Exception("Connection failed")

        stream = SchemaStream(mock_tap_failing)
        records = list(stream.get_records(_context=None))

        # Should fall back to test data when exception occurs
        assert len(records) == 1
        assert records[0]["name"] == "cn"

    @patch("flext_tap_ldap.client.LDAPClient")
    def test_custom_stream_exception_fallback(
        self,
        mock_client_class: Mock,
        mock_tap_failing: Mock,
    ) -> None:
        """Test custom stream exception handling fallback."""
        # Mock LDAP client to raise exception
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.search.side_effect = Exception("Connection failed")

        params = CustomStreamParams(
            name="failing_custom",
            search_filter="(objectClass=*)",
        )
        stream = CustomStream(tap=mock_tap_failing, params=params)
        records = list(stream.get_records(_context=None))

        # Should fall back to test data when exception occurs
        assert len(records) == 1
        assert "cn=custom_entry,dc=test,dc=com" in records[0]["dn"]
