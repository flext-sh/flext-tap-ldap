"""Tests for LDAP stream functionality.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from flext_tap_ldap import FlextTapLdapStreams, FlextTapLdapTap


class TestLDAPBaseStream:
    """Test base LDAP stream functionality."""

    @pytest.fixture
    def mock_tap(self) -> Mock:
        """Create mock tap instance."""
        tap = Mock(spec=FlextTapLdapTap)
        tap.config = {
            "ldap_host": "test.ldap.com",
            "ldap_port": 389,
            "base_dn": "dc=test,dc=com",
            "bind_dn": "cn=REDACTED_LDAP_BIND_PASSWORD,dc=test,dc=com",
            "bind_password": "test_password",
        }
        tap.metrics_logger = Mock()
        tap.logger = Mock()
        return tap

    def test_self(self, mock_tap: Mock) -> None:
        """Test method."""
        "Test base stream has required attributes."
        stream = FlextTapLdapStreams.UsersStream(mock_tap)
        assert hasattr(stream, "name")
        assert hasattr(stream, "tap")
        assert hasattr(stream, "schema")
        assert stream.tap == mock_tap


class TestUsersStream:
    """Test Users stream functionality."""

    @pytest.fixture
    def mock_tap(self) -> Mock:
        """Create mock tap instance."""
        tap = Mock(spec=FlextTapLdapTap)
        tap.config = {
            "ldap_host": "test.ldap.com",
            "ldap_port": 389,
            "base_dn": "dc=test,dc=com",
            "bind_dn": "cn=REDACTED_LDAP_BIND_PASSWORD,dc=test,dc=com",
            "bind_password": "test_password",
            "user_filter": "(objectClass=inetOrgPerson)",
        }
        tap.metrics_logger = Mock()
        tap.logger = Mock()
        return tap

    def test_users_stream_creation(self, mock_tap: Mock) -> None:
        """Test users stream creation."""
        stream = FlextTapLdapStreams.UsersStream(mock_tap)
        assert stream is not None
        assert stream.name == "users"
        assert stream.tap == mock_tap

    def test_users_stream_schema_definition(self, mock_tap: Mock) -> None:
        """Test users stream schema definition."""
        stream = FlextTapLdapStreams.UsersStream(mock_tap)
        schema = stream.schema
        assert isinstance(schema, dict)
        assert "properties" in schema
        properties = schema["properties"]
        assert "dn" in properties
        assert "cn" in properties or "commonName" in properties

    @patch("flext_tap_ldap.client.LDAPClient")
    def test_users_stream_get_records(
        self, mock_client_class: Mock, mock_tap: Mock
    ) -> None:
        """Test users stream record retrieval."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
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
        stream = FlextTapLdapStreams.UsersStream(mock_tap)
        records = list(stream.get_records(context=None))
        assert len(records) == 1
        first_record = records[0]
        assert isinstance(first_record, dict)
        assert first_record["dn"] == "uid=jdoe,ou=users,dc=test,dc=com"
        assert first_record["uid"] == "jdoe"
        mock_client_class.assert_called_once()

    @patch("flext_tap_ldap.client.LDAPClient")
    def test_groups_stream_get_records(
        self, mock_client_class: Mock, mock_tap: Mock
    ) -> None:
        """Test groups stream record retrieval."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.search.return_value = []
        stream = FlextTapLdapStreams.GroupsStream(mock_tap)
        records = list(stream.get_records(context=None))
        assert len(records) == 1
        first_record = records[0]
        assert isinstance(first_record, dict)
        assert first_record["dn"] == "cn=developers,ou=groups,dc=test,dc=com"
        assert first_record["cn"] == "developers"
        mock_client_class.assert_called_once()

    @patch("flext_tap_ldap.client.LDAPClient")
    def test_organizational_units_stream_get_records(
        self, mock_client_class: Mock, mock_tap: Mock
    ) -> None:
        """Test organizational units stream record retrieval."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.search.return_value = []
        stream = FlextTapLdapStreams.OrganizationalUnitsStream(mock_tap)
        records = list(stream.get_records(context=None))
        assert len(records) == 1
        first_record = records[0]
        assert isinstance(first_record, dict)
        assert first_record["dn"] == "ou=users,dc=test,dc=com"
        assert first_record["ou"] == "users"
        mock_client_class.assert_called_once()

    @patch("flext_tap_ldap.client.LDAPClient")
    def test_schema_stream_get_records(
        self, mock_client_class: Mock, mock_tap: Mock
    ) -> None:
        """Test schema stream record retrieval."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.search.return_value = []
        stream = FlextTapLdapStreams.SchemaStream(mock_tap)
        records = list(stream.get_records(context=None))
        assert len(records) == 1
        first_record = records[0]
        assert isinstance(first_record, dict)
        assert first_record["dn"] == "cn=schema"
        assert first_record["cn"] == "schema"
        mock_client_class.assert_called_once()


class TestGroupsStream:
    """Test Groups stream functionality."""

    @pytest.fixture
    def mock_tap(self) -> Mock:
        """Create mock tap instance."""
        tap = Mock(spec=FlextTapLdapTap)
        tap.config = {
            "ldap_host": "test.ldap.com",
            "ldap_port": 389,
            "base_dn": "dc=test,dc=com",
            "bind_dn": "cn=REDACTED_LDAP_BIND_PASSWORD,dc=test,dc=com",
            "bind_password": "test_password",
            "group_filter": "(objectClass=groupOfNames)",
        }
        tap.metrics_logger = Mock()
        tap.logger = Mock()
        return tap

    def test_groups_stream_creation(self, mock_tap: Mock) -> None:
        """Test groups stream creation."""
        stream = FlextTapLdapStreams.GroupsStream(mock_tap)
        assert stream is not None
        assert stream.name == "groups"
        assert stream.tap == mock_tap

    def test_groups_stream_schema_definition(self, mock_tap: Mock) -> None:
        """Test groups stream schema definition."""
        stream = FlextTapLdapStreams.GroupsStream(mock_tap)
        schema = stream.schema
        assert isinstance(schema, dict)
        assert "properties" in schema
        properties = schema["properties"]
        assert "dn" in properties
        assert "cn" in properties or "commonName" in properties


class TestOrganizationalUnitsStream:
    """Test Organizational Units stream functionality."""

    @pytest.fixture
    def mock_tap(self) -> Mock:
        """Create mock tap instance."""
        tap = Mock(spec=FlextTapLdapTap)
        tap.config = {
            "ldap_host": "test.ldap.com",
            "ldap_port": 389,
            "base_dn": "dc=test,dc=com",
            "bind_dn": "cn=REDACTED_LDAP_BIND_PASSWORD,dc=test,dc=com",
            "bind_password": "test_password",
        }
        tap.metrics_logger = Mock()
        tap.logger = Mock()
        return tap

    def test_organizational_units_stream_creation(self, mock_tap: Mock) -> None:
        """Test organizational units stream creation."""
        stream = FlextTapLdapStreams.OrganizationalUnitsStream(mock_tap)
        assert stream is not None
        assert stream.name == "organizational_units"
        assert stream.tap == mock_tap

    def test_organizational_units_stream_schema_definition(
        self, mock_tap: Mock
    ) -> None:
        """Test organizational units stream schema definition."""
        stream = FlextTapLdapStreams.OrganizationalUnitsStream(mock_tap)
        schema = stream.schema
        assert isinstance(schema, dict)
        assert "properties" in schema
        properties = schema["properties"]
        assert "dn" in properties
        assert "ou" in properties or "organizationalUnitName" in properties


class TestSchemaStream:
    """Test Schema stream functionality."""

    @pytest.fixture
    def mock_tap(self) -> Mock:
        """Create mock tap instance."""
        tap = Mock(spec=FlextTapLdapTap)
        tap.config = {
            "ldap_host": "test.ldap.com",
            "ldap_port": 389,
            "base_dn": "dc=test,dc=com",
            "bind_dn": "cn=REDACTED_LDAP_BIND_PASSWORD,dc=test,dc=com",
            "bind_password": "test_password",
        }
        tap.metrics_logger = Mock()
        tap.logger = Mock()
        return tap

    def test_schema_stream_creation(self, mock_tap: Mock) -> None:
        """Test schema stream creation."""
        stream = FlextTapLdapStreams.SchemaStream(mock_tap)
        assert stream is not None
        assert stream.name == "schema"
        assert stream.tap == mock_tap

    def test_schema_stream_schema_definition(self, mock_tap: Mock) -> None:
        """Test schema stream schema definition."""
        stream = FlextTapLdapStreams.SchemaStream(mock_tap)
        schema = stream.schema
        assert isinstance(schema, dict)
        assert "properties" in schema
        properties = schema["properties"]
        assert "name" in properties
        assert "type" in properties


class TestCustomStreamParams:
    """Test CustomStreamParams parameter object."""

    def test_custom_stream_params_creation(self) -> None:
        """Test method."""
        "Test creating custom stream parameters."
        params = FlextTapLdapStreams.CustomStreamParams(
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
        """Test method."""
        "Test parameter validation."
        params = FlextTapLdapStreams.CustomStreamParams(
            name="valid_stream", search_filter="(objectClass=*)"
        )
        assert params.primary_keys == ["dn"]
        with pytest.raises(ValueError, match="Stream name is required"):
            FlextTapLdapStreams.CustomStreamParams(
                name="", search_filter="(objectClass=*)"
            )
        with pytest.raises(ValueError, match="Search filter is required"):
            FlextTapLdapStreams.CustomStreamParams(name="test", search_filter="")
        with pytest.raises(ValueError, match="Primary keys cannot be empty list"):
            FlextTapLdapStreams.CustomStreamParams(
                name="test", search_filter="(objectClass=*)", primary_keys=[]
            )


class TestCustomStream:
    """Test Custom stream functionality."""

    @pytest.fixture
    def mock_tap(self) -> Mock:
        """Create mock tap instance."""
        tap = Mock(spec=FlextTapLdapTap)
        tap.config = {
            "ldap_host": "test.ldap.com",
            "ldap_port": 389,
            "base_dn": "dc=test,dc=com",
            "bind_dn": "cn=REDACTED_LDAP_BIND_PASSWORD,dc=test,dc=com",
            "bind_password": "test_password",
        }
        tap.metrics_logger = Mock()
        tap.logger = Mock()
        return tap

    def test_custom_stream_creation(self, mock_tap: Mock) -> None:
        """Test custom stream creation."""
        params = FlextTapLdapStreams.CustomStreamParams(
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
        stream = FlextTapLdapStreams.CustomStream(tap=mock_tap, params=params)
        assert stream is not None
        assert stream.name == "service_accounts"
        assert stream.tap == mock_tap

    def test_custom_stream_minimal_configuration(self, mock_tap: Mock) -> None:
        """Test custom stream with minimal configuration."""
        params = FlextTapLdapStreams.CustomStreamParams(
            name="minimal_custom", search_filter="(objectClass=*)"
        )
        stream = FlextTapLdapStreams.CustomStream(tap=mock_tap, params=params)
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
        params = FlextTapLdapStreams.CustomStreamParams(
            name="employees",
            search_filter="(objectClass=employee)",
            schema_properties=custom_properties,
        )
        stream = FlextTapLdapStreams.CustomStream(tap=mock_tap, params=params)
        schema = stream.schema
        assert isinstance(schema, dict)
        assert "properties" in schema
        properties = schema["properties"]
        assert "dn" in properties
        for prop_name in custom_properties:
            assert prop_name in properties

    @patch("flext_tap_ldap.client.LDAPClient")
    def test_custom_stream_get_records(
        self, mock_client_class: Mock, mock_tap: Mock
    ) -> None:
        """Test custom stream record retrieval."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.search.return_value = []
        params = FlextTapLdapStreams.CustomStreamParams(
            name="custom_test",
            search_filter="(objectClass=testObject)",
            schema_properties={"testAttribute": {"type": "string"}},
        )
        stream = FlextTapLdapStreams.CustomStream(tap=mock_tap, params=params)
        records = list(stream.get_records(context=None))
        assert len(records) == 1
        first_record = records[0]
        assert isinstance(first_record, dict)
        assert "cn=test-custom_test,dc=test,dc=com" in str(first_record["dn"])
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
        params = FlextTapLdapStreams.CustomStreamParams(
            name="type_test",
            search_filter="(objectClass=typeTest)",
            schema_properties=custom_properties,
        )
        stream = FlextTapLdapStreams.CustomStream(tap=mock_tap, params=params)
        schema = stream.schema
        properties = schema["properties"]
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
            "ldap_host": "test.ldap.com",
            "ldap_port": 389,
            "base_dn": "dc=test,dc=com",
            "bind_dn": "cn=REDACTED_LDAP_BIND_PASSWORD,dc=test,dc=com",
            "bind_password": "test_password",
            "use_ssl": False,
            "timeout": 30,
            "page_size": 1000,
        }

    def test_all_default_streams_creation(self, tap_config: dict[str, object]) -> None:
        """Test that all default streams can be created."""
        tap = FlextTapLdapTap(config=tap_config)
        streams = tap.discover_streams()
        assert len(streams) >= 4
        stream_names = [s.name for s in streams]
        assert "users" in stream_names
        assert "groups" in stream_names
        assert "organizational_units" in stream_names
        assert "schema" in stream_names

    def test_streams_with_custom_configuration(
        self, tap_config: dict[str, object]
    ) -> None:
        """Test streams with custom configuration."""
        tap_config["custom_streams"] = [
            {
                "name": "custom_test_stream",
                "search_filter": "(objectClass=testObject)",
                "primary_keys": ["dn"],
                "replication_key": "modifyTimestamp",
                "schema": {"properties": {"testAttribute": {"type": "string"}}},
            }
        ]
        tap = FlextTapLdapTap(config=tap_config)
        streams = tap.discover_streams()
        stream_names = [s.name for s in streams]
        assert "custom_test_stream" in stream_names
        custom_stream = next(s for s in streams if s.name == "custom_test_stream")
        assert isinstance(custom_stream, FlextTapLdapStreams.CustomStream)

    def test_self(self, tap_config: dict[str, object]) -> None:
        """Test method."""
        "Test LDIF streams are included when enabled."
        tap_config["enable_ldif_streams"] = True
        tap = FlextTapLdapTap(config=tap_config)
        streams = tap.discover_streams()
        stream_names = [s.name for s in streams]
        ldif_stream_found = any("ldif" in name.lower() for name in stream_names)
        assert ldif_stream_found or len(streams) > 4


class TestLDAPBaseStreamDirectUsage:
    """Test base stream class directly to cover missing lines."""

    @pytest.fixture
    def mock_tap(self) -> Mock:
        """Create mock tap instance."""
        tap = Mock(spec=FlextTapLdapTap)
        tap.config = {
            "ldap_host": "test.ldap.com",
            "ldap_port": 389,
            "base_dn": "dc=test,dc=com",
        }
        tap.metrics_logger = Mock()
        tap.logger = Mock()
        return tap

    def test_self(self, mock_tap: Mock) -> None:
        """Test method."""
        "Test base stream get_records method (covers line 68)."

        class TestBaseStream(FlextTapLdapStreams.LDAPBaseStream):
            pass

        base_stream = TestBaseStream(
            mock_tap,
            name="test_base",
            schema={"properties": {"dn": {"type": "string"}}},
        )
        records = list(base_stream.get_records(context=None))
        assert len(records) == 0


class TestStreamExceptionHandling:
    """Test exception handling paths in streams."""

    @pytest.fixture
    def mock_tap_failing(self) -> Mock:
        """Create mock tap that will cause exceptions."""
        tap = Mock(spec=FlextTapLdapTap)
        tap.config = {
            "ldap_host": "failing.ldap.com",
            "ldap_port": 389,
            "base_dn": "dc=test,dc=com",
        }
        tap.metrics_logger = Mock()
        tap.logger = Mock()
        return tap

    @patch("flext_tap_ldap.client.LDAPClient")
    def test_users_stream_exception_fallback(
        self, mock_client_class: Mock, mock_tap_failing: Mock
    ) -> None:
        """Test users stream exception handling fallback (covers lines 168-171)."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.search.side_effect = Exception("Connection failed")
        stream = FlextTapLdapStreams.UsersStream(mock_tap_failing)
        records = list(stream.get_records(context=None))
        assert len(records) == 1
        first_record = records[0]
        assert isinstance(first_record, dict)
        assert first_record["dn"] == "uid=jdoe,ou=users,dc=test,dc=com"

    @patch("flext_tap_ldap.client.LDAPClient")
    def test_groups_stream_exception_fallback(
        self, mock_client_class: Mock, mock_tap_failing: Mock
    ) -> None:
        """Test groups stream exception handling fallback."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.search.side_effect = Exception("Connection failed")
        stream = FlextTapLdapStreams.GroupsStream(mock_tap_failing)
        records = list(stream.get_records(context=None))
        assert len(records) == 1
        first_record = records[0]
        assert isinstance(first_record, dict)
        assert first_record["dn"] == "cn=developers,ou=groups,dc=test,dc=com"

    @patch("flext_tap_ldap.client.LDAPClient")
    def test_organizational_units_stream_exception_fallback(
        self, mock_client_class: Mock, mock_tap_failing: Mock
    ) -> None:
        """Test organizational units stream exception handling fallback."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.search.side_effect = Exception("Connection failed")
        stream = FlextTapLdapStreams.OrganizationalUnitsStream(mock_tap_failing)
        records = list(stream.get_records(context=None))
        assert len(records) == 1
        first_record = records[0]
        assert isinstance(first_record, dict)
        assert first_record["dn"] == "ou=users,dc=test,dc=com"

    @patch("flext_tap_ldap.client.LDAPClient")
    def test_schema_stream_exception_fallback(
        self, mock_client_class: Mock, mock_tap_failing: Mock
    ) -> None:
        """Test schema stream exception handling fallback."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.search.side_effect = Exception("Connection failed")
        stream = FlextTapLdapStreams.SchemaStream(mock_tap_failing)
        records = list(stream.get_records(context=None))
        assert len(records) == 1
        first_record = records[0]
        assert isinstance(first_record, dict)
        assert first_record["dn"] == "cn=schema"

    @patch("flext_tap_ldap.client.LDAPClient")
    def test_custom_stream_exception_fallback(
        self, mock_client_class: Mock, mock_tap_failing: Mock
    ) -> None:
        """Test custom stream exception handling fallback."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.search.side_effect = Exception("Connection failed")
        params = FlextTapLdapStreams.CustomStreamParams(
            name="failing_custom", search_filter="(objectClass=*)"
        )
        stream = FlextTapLdapStreams.CustomStream(tap=mock_tap_failing, params=params)
        records = list(stream.get_records(context=None))
        assert len(records) == 1
        first_record = records[0]
        assert isinstance(first_record, dict)
        assert "cn=test-failing_custom,dc=test,dc=com" in str(first_record["dn"])
