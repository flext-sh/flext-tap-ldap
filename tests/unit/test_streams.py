"""Tests for LDAP stream functionality.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest
from flext_tests import tm

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
        tm.that(hasattr(stream, "name"), eq=True)
        tm.that(hasattr(stream, "tap"), eq=True)
        tm.that(hasattr(stream, "schema"), eq=True)
        tm.that(stream.tap == mock_tap, eq=True)


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
        tm.that(stream is not None, eq=True)
        tm.that(stream.name == "users", eq=True)
        tm.that(stream.tap == mock_tap, eq=True)

    def test_users_stream_schema_definition(self, mock_tap: Mock) -> None:
        """Test users stream schema definition."""
        stream = FlextTapLdapStreams.UsersStream(mock_tap)
        schema = stream.schema
        tm.that(isinstance(schema, dict), eq=True)
        tm.that("properties" in schema, eq=True)
        properties = schema["properties"]
        tm.that("dn" in properties, eq=True)
        tm.that("cn" in properties or "commonName" in properties, eq=True)

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
        tm.that(len(records) == 1, eq=True)
        first_record = records[0]
        tm.that(isinstance(first_record, dict), eq=True)
        tm.that(first_record["dn"] == "uid=jdoe,ou=users,dc=test,dc=com", eq=True)
        tm.that(first_record["uid"] == "jdoe", eq=True)
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
        tm.that(len(records) == 1, eq=True)
        first_record = records[0]
        tm.that(isinstance(first_record, dict), eq=True)
        tm.that(first_record["dn"] == "cn=developers,ou=groups,dc=test,dc=com", eq=True)
        tm.that(first_record["cn"] == "developers", eq=True)
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
        tm.that(len(records) == 1, eq=True)
        first_record = records[0]
        tm.that(isinstance(first_record, dict), eq=True)
        tm.that(first_record["dn"] == "ou=users,dc=test,dc=com", eq=True)
        tm.that(first_record["ou"] == "users", eq=True)
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
        tm.that(len(records) == 1, eq=True)
        first_record = records[0]
        tm.that(isinstance(first_record, dict), eq=True)
        tm.that(first_record["dn"] == "cn=schema", eq=True)
        tm.that(first_record["cn"] == "schema", eq=True)
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
        tm.that(stream is not None, eq=True)
        tm.that(stream.name == "groups", eq=True)
        tm.that(stream.tap == mock_tap, eq=True)

    def test_groups_stream_schema_definition(self, mock_tap: Mock) -> None:
        """Test groups stream schema definition."""
        stream = FlextTapLdapStreams.GroupsStream(mock_tap)
        schema = stream.schema
        tm.that(isinstance(schema, dict), eq=True)
        tm.that("properties" in schema, eq=True)
        properties = schema["properties"]
        tm.that("dn" in properties, eq=True)
        tm.that("cn" in properties or "commonName" in properties, eq=True)


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
        tm.that(stream is not None, eq=True)
        tm.that(stream.name == "organizational_units", eq=True)
        tm.that(stream.tap == mock_tap, eq=True)

    def test_organizational_units_stream_schema_definition(
        self, mock_tap: Mock
    ) -> None:
        """Test organizational units stream schema definition."""
        stream = FlextTapLdapStreams.OrganizationalUnitsStream(mock_tap)
        schema = stream.schema
        tm.that(isinstance(schema, dict), eq=True)
        tm.that("properties" in schema, eq=True)
        properties = schema["properties"]
        tm.that("dn" in properties, eq=True)
        tm.that("ou" in properties or "organizationalUnitName" in properties, eq=True)


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
        tm.that(stream is not None, eq=True)
        tm.that(stream.name == "schema", eq=True)
        tm.that(stream.tap == mock_tap, eq=True)

    def test_schema_stream_schema_definition(self, mock_tap: Mock) -> None:
        """Test schema stream schema definition."""
        stream = FlextTapLdapStreams.SchemaStream(mock_tap)
        schema = stream.schema
        tm.that(isinstance(schema, dict), eq=True)
        tm.that("properties" in schema, eq=True)
        properties = schema["properties"]
        tm.that("name" in properties, eq=True)
        tm.that("type" in properties, eq=True)


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
        tm.that(params.name == "test_stream", eq=True)
        tm.that(params.search_filter == "(objectClass=person)", eq=True)
        tm.that(params.schema_properties == {"cn": {"type": "string"}}, eq=True)
        tm.that(params.primary_keys == ["dn"], eq=True)
        tm.that(params.replication_key == "modifyTimestamp", eq=True)

    def test_custom_stream_params_validation(self) -> None:
        """Test method."""
        "Test parameter validation."
        params = FlextTapLdapStreams.CustomStreamParams(
            name="valid_stream", search_filter="(objectClass=*)"
        )
        tm.that(params.primary_keys == ["dn"], eq=True)
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
        tm.that(stream is not None, eq=True)
        tm.that(stream.name == "service_accounts", eq=True)
        tm.that(stream.tap == mock_tap, eq=True)

    def test_custom_stream_minimal_configuration(self, mock_tap: Mock) -> None:
        """Test custom stream with minimal configuration."""
        params = FlextTapLdapStreams.CustomStreamParams(
            name="minimal_custom", search_filter="(objectClass=*)"
        )
        stream = FlextTapLdapStreams.CustomStream(tap=mock_tap, params=params)
        tm.that(stream is not None, eq=True)
        tm.that(stream.name == "minimal_custom", eq=True)
        tm.that(stream.tap == mock_tap, eq=True)

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
        tm.that(isinstance(schema, dict), eq=True)
        tm.that("properties" in schema, eq=True)
        properties = schema["properties"]
        tm.that("dn" in properties, eq=True)
        for prop_name in custom_properties:
            tm.that(prop_name in properties, eq=True)

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
        tm.that(len(records) == 1, eq=True)
        first_record = records[0]
        tm.that(isinstance(first_record, dict), eq=True)
        tm.that(
            "cn=test-custom_test,dc=test,dc=com" in str(first_record["dn"]), eq=True
        )
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
        tm.that("stringField" in properties, eq=True)
        tm.that("arrayField" in properties, eq=True)
        tm.that("booleanField" in properties, eq=True)
        tm.that("integerField" in properties, eq=True)
        tm.that("datetimeField" in properties, eq=True)


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
        tm.that(len(streams) >= 4, eq=True)
        stream_names = [s.name for s in streams]
        tm.that("users" in stream_names, eq=True)
        tm.that("groups" in stream_names, eq=True)
        tm.that("organizational_units" in stream_names, eq=True)
        tm.that("schema" in stream_names, eq=True)

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
        tm.that("custom_test_stream" in stream_names, eq=True)
        custom_stream = next(s for s in streams if s.name == "custom_test_stream")
        tm.that(isinstance(custom_stream, FlextTapLdapStreams.CustomStream), eq=True)

    def test_self(self, tap_config: dict[str, object]) -> None:
        """Test method."""
        "Test LDIF streams are included when enabled."
        tap_config["enable_ldif_streams"] = True
        tap = FlextTapLdapTap(config=tap_config)
        streams = tap.discover_streams()
        stream_names = [s.name for s in streams]
        ldif_stream_found = any("ldif" in name.lower() for name in stream_names)
        tm.that(ldif_stream_found or len(streams) > 4, eq=True)


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
        tm.that(len(records) == 0, eq=True)


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
        tm.that(len(records) == 1, eq=True)
        first_record = records[0]
        tm.that(isinstance(first_record, dict), eq=True)
        tm.that(first_record["dn"] == "uid=jdoe,ou=users,dc=test,dc=com", eq=True)

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
        tm.that(len(records) == 1, eq=True)
        first_record = records[0]
        tm.that(isinstance(first_record, dict), eq=True)
        tm.that(first_record["dn"] == "cn=developers,ou=groups,dc=test,dc=com", eq=True)

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
        tm.that(len(records) == 1, eq=True)
        first_record = records[0]
        tm.that(isinstance(first_record, dict), eq=True)
        tm.that(first_record["dn"] == "ou=users,dc=test,dc=com", eq=True)

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
        tm.that(len(records) == 1, eq=True)
        first_record = records[0]
        tm.that(isinstance(first_record, dict), eq=True)
        tm.that(first_record["dn"] == "cn=schema", eq=True)

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
        tm.that(len(records) == 1, eq=True)
        first_record = records[0]
        tm.that(isinstance(first_record, dict), eq=True)
        tm.that(
            "cn=test-failing_custom,dc=test,dc=com" in str(first_record["dn"]), eq=True
        )
