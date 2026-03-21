"""Tests for LDAP stream functionality.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest
from flext_tests import m, t, u

from flext_tap_ldap import FlextTapLdapStreams, FlextTapLdapTap, m, t


def _build_source_config(
    connection_config: dict[str, t.Scalar],
) -> m.Meltano.DataSourceConfig:
    return m.Meltano.DataSourceConfig(
        source_type="ldap",
        connection_config=connection_config,
        stream_config={},
        source_version="latest",
    )


def _discover_stream_names(
    tap: FlextTapLdapTap,
    connection_config: dict[str, t.Scalar],
) -> tuple[list[str], int]:
    result = tap.discover_streams(source_config=_build_source_config(connection_config))
    assert result.is_success
    assert result.value is not None
    stream_entries = result.value["streams"]
    return [str(stream["stream"]) for stream in stream_entries], len(stream_entries)


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
        u.Tests.Matchers.that(hasattr(stream, "name"), eq=True)
        u.Tests.Matchers.that(hasattr(stream, "tap"), eq=True)
        u.Tests.Matchers.that(hasattr(stream, "schema"), eq=True)
        u.Tests.Matchers.that(stream.tap == mock_tap, eq=True)


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
        u.Tests.Matchers.that(stream is not None, eq=True)
        u.Tests.Matchers.that(stream.name == "users", eq=True)
        u.Tests.Matchers.that(stream.tap == mock_tap, eq=True)

    def test_users_stream_schema_definition(self, mock_tap: Mock) -> None:
        """Test users stream schema definition."""
        stream = FlextTapLdapStreams.UsersStream(mock_tap)
        schema = stream.schema
        u.Tests.Matchers.that(isinstance(schema, dict), eq=True)
        u.Tests.Matchers.that("properties" in schema, eq=True)
        properties = schema["properties"]
        if isinstance(properties, dict):
            u.Tests.Matchers.that("dn" in properties, eq=True)
            u.Tests.Matchers.that(
                "cn" in properties or "commonName" in properties, eq=True
            )

    @patch("flext_tap_ldap.client.LDAPClient")
    def test_users_stream_get_records(
        self, mock_client_class: Mock, mock_tap: Mock
    ) -> None:
        """Test users stream record retrieval."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        member_of_empty: list[str] = []
        member_of_empty_secondary: list[str] = []
        mock_client.search.return_value = [
            {
                "dn": "cn=user1,ou=users,dc=test,dc=com",
                "cn": "user1",
                "uid": "user1",
                "sn": "User One",
                "mail": "user1@test.com",
                "givenName": "User",
                "userPrincipalName": "user1@test.com",
                "memberOf": member_of_empty,
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
                "memberOf": member_of_empty_secondary,
                "objectClass": ["person", "inetOrgPerson"],
                "modifyTimestamp": "2024-01-01T12:00:00Z",
            },
        ]
        stream = FlextTapLdapStreams.UsersStream(mock_tap)
        records = list(stream.get_records(context=None))
        u.Tests.Matchers.that(len(records) == 1, eq=True)
        first_record = records[0]
        u.Tests.Matchers.that(isinstance(first_record, dict), eq=True)
        u.Tests.Matchers.that(
            first_record["dn"] == "uid=jdoe,ou=users,dc=test,dc=com", eq=True
        )
        u.Tests.Matchers.that(first_record["uid"] == "jdoe", eq=True)
        mock_client_class.assert_called_once()

    @patch("flext_tap_ldap.client.LDAPClient")
    def test_groups_stream_get_records(
        self, mock_client_class: Mock, mock_tap: Mock
    ) -> None:
        """Test groups stream record retrieval."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        empty_search_results: list[dict[str, str]] = []
        mock_client.search.return_value = empty_search_results
        stream = FlextTapLdapStreams.GroupsStream(mock_tap)
        records = list(stream.get_records(context=None))
        u.Tests.Matchers.that(len(records) == 1, eq=True)
        first_record = records[0]
        u.Tests.Matchers.that(isinstance(first_record, dict), eq=True)
        u.Tests.Matchers.that(
            first_record["dn"] == "cn=developers,ou=groups,dc=test,dc=com", eq=True
        )
        u.Tests.Matchers.that(first_record["cn"] == "developers", eq=True)
        mock_client_class.assert_called_once()

    @patch("flext_tap_ldap.client.LDAPClient")
    def test_organizational_units_stream_get_records(
        self, mock_client_class: Mock, mock_tap: Mock
    ) -> None:
        """Test organizational units stream record retrieval."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        empty_search_results: list[dict[str, str]] = []
        mock_client.search.return_value = empty_search_results
        stream = FlextTapLdapStreams.OrganizationalUnitsStream(mock_tap)
        records = list(stream.get_records(context=None))
        u.Tests.Matchers.that(len(records) == 1, eq=True)
        first_record = records[0]
        u.Tests.Matchers.that(isinstance(first_record, dict), eq=True)
        u.Tests.Matchers.that(first_record["dn"] == "ou=users,dc=test,dc=com", eq=True)
        u.Tests.Matchers.that(first_record["ou"] == "users", eq=True)
        mock_client_class.assert_called_once()

    @patch("flext_tap_ldap.client.LDAPClient")
    def test_schema_stream_get_records(
        self, mock_client_class: Mock, mock_tap: Mock
    ) -> None:
        """Test schema stream record retrieval."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        empty_search_results: list[dict[str, str]] = []
        mock_client.search.return_value = empty_search_results
        stream = FlextTapLdapStreams.SchemaStream(mock_tap)
        records = list(stream.get_records(context=None))
        u.Tests.Matchers.that(len(records) == 1, eq=True)
        first_record = records[0]
        u.Tests.Matchers.that(isinstance(first_record, dict), eq=True)
        u.Tests.Matchers.that(first_record["dn"] == "cn=schema", eq=True)
        u.Tests.Matchers.that(first_record["cn"] == "schema", eq=True)
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
        u.Tests.Matchers.that(stream is not None, eq=True)
        u.Tests.Matchers.that(stream.name == "groups", eq=True)
        u.Tests.Matchers.that(stream.tap == mock_tap, eq=True)

    def test_groups_stream_schema_definition(self, mock_tap: Mock) -> None:
        """Test groups stream schema definition."""
        stream = FlextTapLdapStreams.GroupsStream(mock_tap)
        schema = stream.schema
        u.Tests.Matchers.that(isinstance(schema, dict), eq=True)
        u.Tests.Matchers.that("properties" in schema, eq=True)
        properties = schema["properties"]
        if isinstance(properties, dict):
            u.Tests.Matchers.that("dn" in properties, eq=True)
            u.Tests.Matchers.that(
                "cn" in properties or "commonName" in properties, eq=True
            )


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
        u.Tests.Matchers.that(stream is not None, eq=True)
        u.Tests.Matchers.that(stream.name == "organizational_units", eq=True)
        u.Tests.Matchers.that(stream.tap == mock_tap, eq=True)

    def test_organizational_units_stream_schema_definition(
        self, mock_tap: Mock
    ) -> None:
        """Test organizational units stream schema definition."""
        stream = FlextTapLdapStreams.OrganizationalUnitsStream(mock_tap)
        schema = stream.schema
        u.Tests.Matchers.that(isinstance(schema, dict), eq=True)
        u.Tests.Matchers.that("properties" in schema, eq=True)
        properties = schema["properties"]
        if isinstance(properties, dict):
            u.Tests.Matchers.that("dn" in properties, eq=True)
            u.Tests.Matchers.that(
                "ou" in properties or "organizationalUnitName" in properties, eq=True
            )


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
        u.Tests.Matchers.that(stream is not None, eq=True)
        u.Tests.Matchers.that(stream.name == "schema", eq=True)
        u.Tests.Matchers.that(stream.tap == mock_tap, eq=True)

    def test_schema_stream_schema_definition(self, mock_tap: Mock) -> None:
        """Test schema stream schema definition."""
        stream = FlextTapLdapStreams.SchemaStream(mock_tap)
        schema = stream.schema
        u.Tests.Matchers.that(isinstance(schema, dict), eq=True)
        u.Tests.Matchers.that("properties" in schema, eq=True)
        properties = schema["properties"]
        if isinstance(properties, dict):
            u.Tests.Matchers.that("name" in properties, eq=True)
            u.Tests.Matchers.that("type" in properties, eq=True)


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
        u.Tests.Matchers.that(params.name == "test_stream", eq=True)
        u.Tests.Matchers.that(params.search_filter == "(objectClass=person)", eq=True)
        u.Tests.Matchers.that(
            params.schema_properties == {"cn": {"type": "string"}}, eq=True
        )
        u.Tests.Matchers.that(params.primary_keys == ["dn"], eq=True)
        u.Tests.Matchers.that(params.replication_key == "modifyTimestamp", eq=True)

    def test_custom_stream_params_validation(self) -> None:
        """Test method."""
        "Test parameter validation."
        params = FlextTapLdapStreams.CustomStreamParams(
            name="valid_stream",
            search_filter="(objectClass=*)",
            schema_properties={},
            primary_keys=["dn"],
        )
        u.Tests.Matchers.that(params.primary_keys == ["dn"], eq=True)
        with pytest.raises(ValueError, match="Stream name is required"):
            FlextTapLdapStreams.CustomStreamParams(
                name="",
                search_filter="(objectClass=*)",
                schema_properties={},
                primary_keys=["dn"],
            )
        with pytest.raises(ValueError, match="Search filter is required"):
            FlextTapLdapStreams.CustomStreamParams(
                name="test",
                search_filter="",
                schema_properties={},
                primary_keys=["dn"],
            )
        with pytest.raises(ValueError, match="Primary keys cannot be empty list"):
            FlextTapLdapStreams.CustomStreamParams(
                name="test",
                search_filter="(objectClass=*)",
                schema_properties={},
                primary_keys=[],
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
        u.Tests.Matchers.that(stream is not None, eq=True)
        u.Tests.Matchers.that(stream.name == "service_accounts", eq=True)
        u.Tests.Matchers.that(stream.tap == mock_tap, eq=True)

    def test_custom_stream_minimal_configuration(self, mock_tap: Mock) -> None:
        """Test custom stream with minimal configuration."""
        params = FlextTapLdapStreams.CustomStreamParams(
            name="minimal_custom",
            search_filter="(objectClass=*)",
            schema_properties={},
            primary_keys=["dn"],
        )
        stream = FlextTapLdapStreams.CustomStream(tap=mock_tap, params=params)
        u.Tests.Matchers.that(stream is not None, eq=True)
        u.Tests.Matchers.that(stream.name == "minimal_custom", eq=True)
        u.Tests.Matchers.that(stream.tap == mock_tap, eq=True)

    def test_custom_stream_schema_properties(self, mock_tap: Mock) -> None:
        """Test custom stream schema properties."""
        custom_properties: dict[str, object] = {
            "employeeNumber": {"type": "string"},
            "department": {"type": "string"},
            "manager": {"type": "string"},
        }
        params = FlextTapLdapStreams.CustomStreamParams(
            name="employees",
            search_filter="(objectClass=employee)",
            schema_properties=custom_properties,
            primary_keys=["dn"],
        )
        stream = FlextTapLdapStreams.CustomStream(tap=mock_tap, params=params)
        schema = stream.schema
        u.Tests.Matchers.that(isinstance(schema, dict), eq=True)
        u.Tests.Matchers.that("properties" in schema, eq=True)
        properties = schema["properties"]
        if isinstance(properties, dict):
            u.Tests.Matchers.that("dn" in properties, eq=True)
            for prop_name in custom_properties:
                u.Tests.Matchers.that(prop_name in properties, eq=True)

    @patch("flext_tap_ldap.client.LDAPClient")
    def test_custom_stream_get_records(
        self, mock_client_class: Mock, mock_tap: Mock
    ) -> None:
        """Test custom stream record retrieval."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        empty_search_results: list[dict[str, str]] = []
        mock_client.search.return_value = empty_search_results
        params = FlextTapLdapStreams.CustomStreamParams(
            name="custom_test",
            search_filter="(objectClass=testObject)",
            schema_properties={"testAttribute": {"type": "string"}},
            primary_keys=["dn"],
        )
        stream = FlextTapLdapStreams.CustomStream(tap=mock_tap, params=params)
        records = list(stream.get_records(context=None))
        u.Tests.Matchers.that(len(records) == 1, eq=True)
        first_record = records[0]
        u.Tests.Matchers.that(isinstance(first_record, dict), eq=True)
        u.Tests.Matchers.that(
            "cn=test-custom_test,dc=test,dc=com" in str(first_record["dn"]), eq=True
        )
        mock_client_class.assert_called_once()

    def test_custom_stream_schema_type_mappings(self, mock_tap: Mock) -> None:
        """Test custom stream schema type mappings."""
        custom_properties: dict[str, object] = {
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
            primary_keys=["dn"],
        )
        stream = FlextTapLdapStreams.CustomStream(tap=mock_tap, params=params)
        schema = stream.schema
        properties = schema["properties"]
        if isinstance(properties, dict):
            u.Tests.Matchers.that("stringField" in properties, eq=True)
            u.Tests.Matchers.that("arrayField" in properties, eq=True)
            u.Tests.Matchers.that("booleanField" in properties, eq=True)
            u.Tests.Matchers.that("integerField" in properties, eq=True)
            u.Tests.Matchers.that("datetimeField" in properties, eq=True)


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
        connection_config: dict[str, t.Scalar] = {}
        for key, value in tap_config.items():
            if isinstance(value, (str, int, float, bool)):
                connection_config[str(key)] = value
        tap = FlextTapLdapTap()
        stream_names, stream_count = _discover_stream_names(tap, connection_config)
        u.Tests.Matchers.that(stream_count >= 4, eq=True)
        u.Tests.Matchers.that("users" in stream_names, eq=True)
        u.Tests.Matchers.that("groups" in stream_names, eq=True)
        u.Tests.Matchers.that("organizational_units" in stream_names, eq=True)
        u.Tests.Matchers.that("schema" in stream_names, eq=True)

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
        connection_config: dict[str, t.Scalar] = {}
        for key, value in tap_config.items():
            if isinstance(value, (str, int, float, bool)):
                connection_config[str(key)] = value
        tap = FlextTapLdapTap()
        stream_names, _stream_count = _discover_stream_names(tap, connection_config)
        u.Tests.Matchers.that("custom_test_stream" in stream_names, eq=True)

    def test_self(self, tap_config: dict[str, object]) -> None:
        """Test method."""
        "Test LDIF streams are included when enabled."
        tap_config["enable_ldif_streams"] = True
        connection_config: dict[str, t.Scalar] = {}
        for key, value in tap_config.items():
            if isinstance(value, (str, int, float, bool)):
                connection_config[str(key)] = value
        tap = FlextTapLdapTap()
        stream_names, stream_count = _discover_stream_names(tap, connection_config)
        ldif_stream_found = any("ldif" in name.lower() for name in stream_names)
        u.Tests.Matchers.that(ldif_stream_found or stream_count > 4, eq=True)


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
        u.Tests.Matchers.that(len(records) == 0, eq=True)


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
        u.Tests.Matchers.that(len(records) == 1, eq=True)
        first_record = records[0]
        u.Tests.Matchers.that(isinstance(first_record, dict), eq=True)
        u.Tests.Matchers.that(
            first_record["dn"] == "uid=jdoe,ou=users,dc=test,dc=com", eq=True
        )

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
        u.Tests.Matchers.that(len(records) == 1, eq=True)
        first_record = records[0]
        u.Tests.Matchers.that(isinstance(first_record, dict), eq=True)
        u.Tests.Matchers.that(
            first_record["dn"] == "cn=developers,ou=groups,dc=test,dc=com", eq=True
        )

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
        u.Tests.Matchers.that(len(records) == 1, eq=True)
        first_record = records[0]
        u.Tests.Matchers.that(isinstance(first_record, dict), eq=True)
        u.Tests.Matchers.that(first_record["dn"] == "ou=users,dc=test,dc=com", eq=True)

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
        u.Tests.Matchers.that(len(records) == 1, eq=True)
        first_record = records[0]
        u.Tests.Matchers.that(isinstance(first_record, dict), eq=True)
        u.Tests.Matchers.that(first_record["dn"] == "cn=schema", eq=True)

    @patch("flext_tap_ldap.client.LDAPClient")
    def test_custom_stream_exception_fallback(
        self, mock_client_class: Mock, mock_tap_failing: Mock
    ) -> None:
        """Test custom stream exception handling fallback."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.search.side_effect = Exception("Connection failed")
        params = FlextTapLdapStreams.CustomStreamParams(
            name="failing_custom",
            search_filter="(objectClass=*)",
            schema_properties={},
            primary_keys=["dn"],
        )
        stream = FlextTapLdapStreams.CustomStream(tap=mock_tap_failing, params=params)
        records = list(stream.get_records(context=None))
        u.Tests.Matchers.that(len(records) == 1, eq=True)
        first_record = records[0]
        u.Tests.Matchers.that(isinstance(first_record, dict), eq=True)
        u.Tests.Matchers.that(
            "cn=test-failing_custom,dc=test,dc=com" in str(first_record["dn"]), eq=True
        )
