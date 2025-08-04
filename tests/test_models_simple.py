"""Simple tests for LDAP domain models."""

from __future__ import annotations

from flext_tap_ldap.models import (
    LDAPAttribute,
    LDAPEntry,
    LDAPSchema,
)


class TestLDAPAttribute:
    """Test LDAP attribute model."""

    def test_attribute_creation(self) -> None:
        """Test creating LDAP attribute."""
        attr = LDAPAttribute(
            name="cn",
            values=["John Doe"],
        )

        assert attr.name == "cn"
        assert attr.values == ["John Doe"]
        assert attr.is_binary is False

    def test_single_value_property(self) -> None:
        """Test single_value property."""
        # Single value
        single_attr = LDAPAttribute(name="uid", values=["jdoe"])
        assert single_attr.single_value == "jdoe"

        # Empty values
        empty_attr = LDAPAttribute(name="empty", values=[])
        assert empty_attr.single_value is None

    def test_is_multi_valued_property(self) -> None:
        """Test is_multi_valued property."""
        # Single value
        single_attr = LDAPAttribute(name="uid", values=["jdoe"])
        assert single_attr.is_multi_valued is False

        # Multiple values
        multi_attr = LDAPAttribute(name="cn", values=["John Doe", "J. Doe"])
        assert multi_attr.is_multi_valued is True

    def test_validate_domain_rules(self) -> None:
        """Test domain validation."""
        attr = LDAPAttribute(name="test", values=["value"])
        # Should not raise exception
        attr.validate_domain_rules()


class TestLDAPEntry:
    """Test LDAP entry model."""

    def test_entry_creation(self) -> None:
        """Test creating LDAP entry."""
        entry = LDAPEntry(
            id="uid=jdoe,ou=users,dc=example,dc=com",
            object_classes=["inetOrgPerson", "person"],
        )

        assert entry.dn == "uid=jdoe,ou=users,dc=example,dc=com"
        assert entry.object_classes == ["inetOrgPerson", "person"]

    def test_entry_validation(self) -> None:
        """Test entry validation."""
        # Valid entry
        entry = LDAPEntry(
            id="uid=test,dc=example,dc=com",
            object_classes=["person"],
        )
        result = entry.validate_domain_rules()
        assert result.success

        # Invalid entry (empty DN)
        invalid_entry = LDAPEntry(
            id="",
            object_classes=["person"],
        )
        result = invalid_entry.validate_domain_rules()
        assert not result.success
        assert "DN cannot be empty" in result.error


class TestLDAPSchema:
    """Test LDAP schema model."""

    def test_schema_creation(self) -> None:
        """Test creating LDAP schema."""
        schema = LDAPSchema(
            object_classes=["person", "inetOrgPerson"],
            attribute_types=["cn", "sn", "uid"],
        )

        assert "person" in schema.object_classes
        assert "cn" in schema.attribute_types

    def test_schema_validation(self) -> None:
        """Test schema validation."""
        schema = LDAPSchema()
        # Should not raise exception
        schema.validate_domain_rules()

    def test_has_oracle_extensions(self) -> None:
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
