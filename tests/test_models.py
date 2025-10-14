"""Simple tests for LDAP domain models.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_tap_ldap import (
    LDAPAttribute,
    LDAPEntry,
    LDAPSchema,
)


class TestLDAPAttribute:
    """Test LDAP attribute model."""

    def test_attribute_creation(self) -> None:
        """Test method."""
        """Test creating LDAP attribute."""
        attr = LDAPAttribute(
            name="cn",
            values=["John Doe"],
        )

        assert attr.name == "cn"
        assert attr.values == ["John Doe"]
        assert attr.is_binary is False

    def test_single_value_property(self) -> None:
        """Test method."""
        """Test single_value property."""
        # Single value
        single_attr = LDAPAttribute(name="uid", values=["jdoe"])
        assert single_attr.single_value == "jdoe"

        # Empty values
        empty_attr = LDAPAttribute(name="empty", values=[])
        assert empty_attr.single_value is None

    def test_is_multi_valued_property(self) -> None:
        """Test method."""
        """Test is_multi_valued property."""
        # Single value
        single_attr = LDAPAttribute(name="uid", values=["jdoe"])
        assert single_attr.is_multi_valued is False

        # Multiple values
        multi_attr = LDAPAttribute(name="cn", values=["John Doe", "J. Doe"])
        assert multi_attr.is_multi_valued is True

    def test_validate_domain_rules(self) -> None:
        """Test method."""
        """Test domain validation."""
        attr = LDAPAttribute(name="test", values=["value"])
        # Should not raise exception
        attr.validate_business_rules()


class TestLDAPEntry:
    """Test LDAP entry model."""

    def test_entry_creation(self) -> None:
        """Test method."""
        """Test creating LDAP entry."""
        entry = LDAPEntry(
            dn="uid=jdoe,ou=users,dc=example,dc=com",
            object_classes=["inetOrgPerson", "person"],
        )

        assert entry.dn == "uid=jdoe,ou=users,dc=example,dc=com"
        assert entry.object_classes == ["inetOrgPerson", "person"]

    def test_entry_validation(self) -> None:
        """Test method."""
        """Test entry validation."""
        # Valid entry
        entry = LDAPEntry(
            dn="uid=test,dc=example,dc=com",
            object_classes=["person"],
        )
        result = entry.validate_business_rules()
        assert result.is_success

        # Invalid entry (empty DN)
        invalid_entry = LDAPEntry(
            dn="",
            object_classes=["person"],
        )
        result = invalid_entry.validate_business_rules()
        assert not result.is_success
        assert result.error is not None and "DN cannot be empty" in result.error


class TestLDAPSchema:
    """Test LDAP schema model."""

    def test_schema_creation(self) -> None:
        """Test method."""
        """Test creating LDAP schema."""
        schema = LDAPSchema(
            object_classes=["person", "inetOrgPerson"],
            attribute_types=["cn", "sn", "uid"],
        )

        assert "person" in schema.object_classes
        assert "cn" in schema.attribute_types

    def test_schema_validation(self) -> None:
        """Test method."""
        """Test schema validation."""
        schema = LDAPSchema()
        # Should not raise exception
        schema.validate_business_rules()

    def test_has_oracle_extensions(self) -> None:
        """Test method."""
        """Test Oracle extensions detection."""
        # Schema without Oracle extensions
        normal_schema = LDAPSchema(
            object_classes=["person", "inetOrgPerson"],
        )
        assert normal_schema.has_oracle_extensions is False

        # Schema with Oracle extensions
        oracle_schema = LDAPSchema(
            object_classes=["person", "orclContainer"],
        )
        assert oracle_schema.has_oracle_extensions is True
