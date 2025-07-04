"""Tests for tap-ldap streams."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from tap_ldap.streams import (
    CustomStream,
    GroupsStream,
    LDAPStream,
    OrganizationalUnitsStream,
    SchemaStream,
    UsersStream,
)
from tap_ldap.tap import TapLDAP


class TestLDAPStream:
    """Test base LDAP stream."""

    @pytest.fixture
    def tap(self, mock_ldap_config: dict[str, Any]) -> TapLDAP:
        """Create test tap instance."""
        return TapLDAP(config=mock_ldap_config)

    def test_ldap_stream_initialization(self, tap: TapLDAP) -> None:
        """Test LDAP stream initialization."""
        stream = LDAPStream(tap, name="test_stream")

        assert stream.tap_name == "tap-ldap"
        assert stream.name == "test_stream"
        assert stream.logger is not None

    def test_get_dn_from_record(self, tap: TapLDAP) -> None:
        """Test DN extraction from record."""
        stream = LDAPStream(tap, name="test_stream")

        # Test explicit DN
        record = {"dn": "uid=test,dc=example,dc=com"}
        assert stream.get_dn_from_record(record) == "uid=test,dc=example,dc=com"

        # Test DN construction with RDN
        stream.get_rdn_attribute = lambda: "cn"  # type: ignore
        record = {"cn": "testgroup"}
        dn = stream.get_dn_from_record(record)
        assert dn == "cn=testgroup,dc=test,dc=com"

    def test_transform_record(self, tap: TapLDAP) -> None:
        """Test record transformation."""
        stream = LDAPStream(tap, name="test_stream")

        entry = {
            "dn": "uid=test,dc=example,dc=com",
            "attributes": {
                "uid": "test",
                "createTimestamp": datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC),
                "objectClass": ["person", "top"],
            },
        }

        result = stream.transform_record(entry)

        assert result["dn"] == "uid=test,dc=example,dc=com"
        assert result["uid"] == "test"
        assert result["createTimestamp"] == "2024-01-01T12:00:00+00:00"
        assert result["objectClass"] == ["person", "top"]


class TestUsersStream:
    """Test users stream."""

    @pytest.fixture
    def users_stream(self, mock_ldap_config: dict[str, Any]) -> UsersStream:
        """Create users stream."""
        tap = TapLDAP(config=mock_ldap_config)
        return UsersStream(tap)

    def test_users_stream_properties(self, users_stream: UsersStream) -> None:
        """Test users stream properties."""
        assert users_stream.name == "users"
        assert users_stream.primary_keys == ["dn"]
        assert users_stream.replication_key == "modifyTimestamp"
        assert "uid" in users_stream.schema["properties"]
        assert "mail" in users_stream.schema["properties"]

    def test_get_search_filter(self, users_stream: UsersStream) -> None:
        """Test search filter generation."""
        # Basic filter
        filter_str = users_stream.get_search_filter()
        assert filter_str == "(objectClass=inetOrgPerson)"

        # With replication key
        with patch.object(users_stream, "get_starting_timestamp") as mock_timestamp:
            mock_timestamp.return_value = datetime(2024, 1, 1, tzinfo=UTC)
            filter_str = users_stream.get_search_filter()
            assert "(modifyTimestamp>=" in filter_str
            assert "(objectClass=inetOrgPerson)" in filter_str

    @patch("tap_ldap.streams.LDAPClient")
    def test_get_records(
        self,
        mock_client_class: MagicMock,
        users_stream: UsersStream,
    ) -> None:
        """Test record extraction."""
        # Mock client and search results
        mock_client = MagicMock()
        mock_client.search.return_value = [
            {
                "dn": "uid=jdoe,ou=users,dc=test,dc=com",
                "attributes": {
                    "uid": "jdoe",
                    "cn": "John Doe",
                    "mail": "jdoe@test.com",
                },
            }
        ]
        users_stream._client = mock_client

        # Get records
        records = list(users_stream.get_records(None))

        assert len(records) == 1
        assert records[0]["uid"] == "jdoe"
        assert records[0]["cn"] == "John Doe"

        # Verify search was called correctly
        mock_client.search.assert_called_once_with(
            base_dn="dc=test,dc=com",
            search_filter="(objectClass=inetOrgPerson)",
            attributes=[
                "uid",
                "cn",
                "sn",
                "givenName",
                "mail",
                "userPassword",
                "objectClass",
                "memberOf",
                "createTimestamp",
                "modifyTimestamp",
            ],
        )


class TestGroupsStream:
    """Test groups stream."""

    @pytest.fixture
    def groups_stream(self, mock_ldap_config: dict[str, Any]) -> GroupsStream:
        """Create groups stream."""
        tap = TapLDAP(config=mock_ldap_config)
        return GroupsStream(tap)

    def test_groups_stream_properties(self, groups_stream: GroupsStream) -> None:
        """Test groups stream properties."""
        assert groups_stream.name == "groups"
        assert groups_stream.primary_keys == ["dn"]
        assert groups_stream.replication_key == "modifyTimestamp"
        assert "cn" in groups_stream.schema["properties"]
        assert "member" in groups_stream.schema["properties"]

    def test_get_search_filter(self, groups_stream: GroupsStream) -> None:
        """Test search filter generation."""
        filter_str = groups_stream.get_search_filter()
        assert filter_str == "(objectClass=groupOfNames)"


class TestOrganizationalUnitsStream:
    """Test organizational units stream."""

    @pytest.fixture
    def ou_stream(self, mock_ldap_config: dict[str, Any]) -> OrganizationalUnitsStream:
        """Create OU stream."""
        tap = TapLDAP(config=mock_ldap_config)
        return OrganizationalUnitsStream(tap)

    def test_ou_stream_properties(self, ou_stream: OrganizationalUnitsStream) -> None:
        """Test OU stream properties."""
        assert ou_stream.name == "organizational_units"
        assert ou_stream.primary_keys == ["dn"]
        assert "ou" in ou_stream.schema["properties"]
        assert "description" in ou_stream.schema["properties"]


class TestSchemaStream:
    """Test schema stream."""

    @pytest.fixture
    def schema_stream(self, mock_ldap_config: dict[str, Any]) -> SchemaStream:
        """Create schema stream."""
        tap = TapLDAP(config=mock_ldap_config)
        return SchemaStream(tap)

    def test_schema_stream_properties(self, schema_stream: SchemaStream) -> None:
        """Test schema stream properties."""
        assert schema_stream.name == "schema"
        assert schema_stream.primary_keys == ["type", "name"]
        assert "definition" in schema_stream.schema["properties"]

    @patch("tap_ldap.streams.LDAPClient")
    def test_get_records(
        self,
        mock_client_class: MagicMock,
        schema_stream: SchemaStream,
    ) -> None:
        """Test schema extraction."""
        # Mock schema response
        mock_client = MagicMock()
        mock_client.get_schema.return_value = {
            "object_classes": [
                "( 2.5.6.6 NAME 'person' SUP top STRUCTURAL )",
            ],
            "attribute_types": [
                "( 2.5.4.3 NAME 'cn' SUP name )",
            ],
        }
        schema_stream._client = mock_client

        # Get records
        records = list(schema_stream.get_records(None))

        assert len(records) == 2
        assert records[0]["type"] == "objectClass"
        assert records[0]["name"] == "person"
        assert records[1]["type"] == "attributeType"
        assert records[1]["name"] == "cn"

    def test_extract_schema_name(self, schema_stream: SchemaStream) -> None:
        """Test schema name extraction."""
        definition = "( 2.5.6.6 NAME 'person' SUP top STRUCTURAL )"
        name = schema_stream._extract_schema_name(definition)
        assert name == "person"

        # Test with no name
        definition = "( 2.5.6.6 SUP top )"
        name = schema_stream._extract_schema_name(definition)
        assert name == "unknown"


class TestCustomStream:
    """Test custom stream functionality."""

    @pytest.fixture
    def tap(self, mock_ldap_config: dict[str, Any]) -> TapLDAP:
        """Create test tap instance."""
        return TapLDAP(config=mock_ldap_config)

    def test_custom_stream_creation(self, tap: TapLDAP) -> None:
        """Test custom stream creation."""
        schema_props = {
            "dn": {"type": "string"},
            "uid": {"type": "string"},
            "accountType": {"type": "string"},
        }

        stream = CustomStream(
            tap=tap,
            name="service_accounts",
            search_filter="(&(objectClass=account)(uid=svc-*))",
            schema_properties=schema_props,
            primary_keys=["uid"],
            replication_key="modifyTimestamp",
        )

        assert stream.name == "service_accounts"
        assert stream.get_search_filter() == "(&(objectClass=account)(uid=svc-*))"
        assert stream.primary_keys == ["uid"]
        assert stream.replication_key == "modifyTimestamp"
        assert "accountType" in stream.schema["properties"]
