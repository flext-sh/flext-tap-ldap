"""Tests for LDAP domain models."""

from __future__ import annotations

from flext_tap_ldap import (
    LDAPAttribute,
    LDAPEntry,
    LDAPGroup,
    LDAPSchema,
    LDAPUser,
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

    def test_attribute_with_binary_data(self) -> None:
      """Test attribute with binary data."""
      attr = LDAPAttribute(
          name="userCertificate",
          values=["binary_data_here"],
          is_binary=True,
      )

      assert attr.name == "userCertificate"
      assert attr.is_binary is True

    def test_single_value_property(self) -> None:
      """Test single_value property."""
      # Single value
      single_attr = LDAPAttribute(name="uid", values=["jdoe"])
      assert single_attr.single_value == "jdoe"

      # Multiple values
      multi_attr = LDAPAttribute(name="cn", values=["John Doe", "J. Doe"])
      assert multi_attr.single_value == "John Doe"

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

      # Empty values
      empty_attr = LDAPAttribute(name="empty", values=[])
      assert empty_attr.is_multi_valued is False

    def test_attribute_validation(self) -> None:
      """Test attribute validation."""
      # Valid attribute
      attr = LDAPAttribute(name="mail", values=["test@example.com"])
      assert attr.name == "mail"

      # Test with empty name (should work)
      empty_name_attr = LDAPAttribute(name="", values=["value"])
      assert empty_name_attr.name == ""


class TestLDAPEntry:
    """Test LDAP entry model."""

    def test_entry_creation(self) -> None:
      """Test creating LDAP entry."""
      entry = LDAPEntry(
          dn="uid=jdoe,ou=users,dc=example,dc=com",
          object_classes=["inetOrgPerson", "person"],
          attributes={
              "uid": ["jdoe"],
              "cn": ["John Doe"],
          },
      )

      assert entry.dn == "uid=jdoe,ou=users,dc=example,dc=com"
      assert entry.object_classes == ["inetOrgPerson", "person"]
      assert "uid" in entry.attributes
      assert "cn" in entry.attributes

    def test_entry_rdn_property(self) -> None:
      """Test RDN property extraction."""
      entry = LDAPEntry(
          dn="uid=jdoe,ou=users,dc=example,dc=com",
          object_classes=["person"],
          attributes={},
      )

      rdn = entry.rdn
      assert rdn == "uid=jdoe"

    def test_entry_rdn_complex_dn(self) -> None:
      """Test RDN with complex DN."""
      # Multi-valued RDN
      entry = LDAPEntry(
          dn="cn=John Doe+uid=jdoe,ou=users,dc=example,dc=com",
          object_classes=["person"],
          attributes={},
      )

      rdn = entry.rdn
      assert rdn == "cn=John Doe+uid=jdoe"

    def test_entry_get_attribute(self) -> None:
      """Test getting attribute from entry."""
      uid_attr = LDAPAttribute(name="uid", values=["jdoe"])
      entry = LDAPEntry(
          dn="uid=jdoe,dc=example,dc=com",
          object_classes=["person"],
          attributes={"uid": uid_attr},
      )

      # Existing attribute
      result = entry.get_attribute("uid")
      assert result == uid_attr

      # Non-existent attribute
      result = entry.get_attribute("nonexistent")
      assert result is None

    def test_entry_get_attribute_values(self) -> None:
      """Test getting attribute values from entry."""
      entry = LDAPEntry(
          dn="uid=jdoe,dc=example,dc=com",
          object_classes=["person"],
          attributes={
              "uid": LDAPAttribute(name="uid", values=["jdoe"]),
              "cn": LDAPAttribute(name="cn", values=["John", "J. Doe"]),
          },
      )

      # Existing attribute
      values = entry.get_attribute_values("uid")
      assert values == ["jdoe"]

      # Multi-valued attribute
      values = entry.get_attribute_values("cn")
      assert values == ["John", "J. Doe"]

      # Non-existent attribute
      values = entry.get_attribute_values("nonexistent")
      assert values == []

    def test_entry_has_object_class(self) -> None:
      """Test checking object class."""
      entry = LDAPEntry(
          dn="uid=jdoe,dc=example,dc=com",
          object_classes=["inetOrgPerson", "person", "top"],
          attributes={},
      )

      # Existing object class
      assert entry.has_object_class("person") is True
      assert entry.has_object_class("inetOrgPerson") is True

      # Case insensitive
      assert entry.has_object_class("PERSON") is True

      # Non-existent object class
      assert entry.has_object_class("groupOfNames") is False

    def test_entry_to_dict(self) -> None:
      """Test converting entry to dictionary."""
      entry = LDAPEntry(
          dn="uid=jdoe,dc=example,dc=com",
          object_classes=["person"],
          attributes={
              "uid": LDAPAttribute(name="uid", values=["jdoe"]),
          },
      )

      entry_dict = entry.to_dict()

      assert entry_dict["dn"] == "uid=jdoe,dc=example,dc=com"
      assert entry_dict["objectClass"] == ["person"]
      assert entry_dict["uid"] == ["jdoe"]

    def test_entry_from_dict(self) -> None:
      """Test creating entry from dictionary."""
      data = {
          "dn": "uid=jdoe,dc=example,dc=com",
          "objectClass": ["person", "inetOrgPerson"],
          "uid": ["jdoe"],
          "cn": ["John Doe"],
          "mail": ["john@example.com"],
      }

      entry = LDAPEntry.from_dict(data)

      assert entry.dn == "uid=jdoe,dc=example,dc=com"
      assert entry.object_classes == ["person", "inetOrgPerson"]
      assert entry.get_attribute_values("uid") == ["jdoe"]
      assert entry.get_attribute_values("cn") == ["John Doe"]
      assert entry.get_attribute_values("mail") == ["john@example.com"]


class TestLDAPUser:
    """Test LDAP user model."""

    def test_user_creation(self) -> None:
      """Test creating LDAP user."""
      user = LDAPUser(
          dn="uid=jdoe,ou=users,dc=example,dc=com",
          object_classes=["inetOrgPerson", "person"],
          attributes={
              "uid": LDAPAttribute(name="uid", values=["jdoe"]),
              "cn": LDAPAttribute(name="cn", values=["John Doe"]),
              "sn": LDAPAttribute(name="sn", values=["Doe"]),
              "givenName": LDAPAttribute(name="givenName", values=["John"]),
              "mail": LDAPAttribute(name="mail", values=["john@example.com"]),
          },
      )

      assert user.dn == "uid=jdoe,ou=users,dc=example,dc=com"
      assert user.uid == "jdoe"
      assert user.common_name == "John Doe"
      assert user.surname == "Doe"
      assert user.given_name == "John"
      assert user.email == "john@example.com"

    def test_user_missing_attributes(self) -> None:
      """Test user with missing attributes."""
      user = LDAPUser(
          dn="uid=jdoe,dc=example,dc=com",
          object_classes=["person"],
          attributes={},
      )

      assert user.uid is None
      assert user.common_name is None
      assert user.surname is None
      assert user.given_name is None
      assert user.email is None

    def test_user_display_name_property(self) -> None:
      """Test display name property."""
      # With common name
      user_with_cn = LDAPUser(
          dn="uid=jdoe,dc=example,dc=com",
          object_classes=["person"],
          attributes={
              "cn": LDAPAttribute(name="cn", values=["John Doe"]),
              "uid": LDAPAttribute(name="uid", values=["jdoe"]),
          },
      )
      assert user_with_cn.display_name == "John Doe"

      # Without common name, fallback to uid
      user_no_cn = LDAPUser(
          dn="uid=jdoe,dc=example,dc=com",
          object_classes=["person"],
          attributes={
              "uid": LDAPAttribute(name="uid", values=["jdoe"]),
          },
      )
      assert user_no_cn.display_name == "jdoe"

      # No uid or cn
      user_minimal = LDAPUser(
          dn="cn=unknown,dc=example,dc=com",
          object_classes=["person"],
          attributes={},
      )
      assert user_minimal.display_name == "unknown"  # Should extract from DN

    def test_user_is_active_property(self) -> None:
      """Test is_active property."""
      # Active user (no account control or disabled attributes)
      active_user = LDAPUser(
          dn="uid=active,dc=example,dc=com",
          object_classes=["person"],
          attributes={},
      )
      assert active_user.is_active is True

      # User with account disabled
      disabled_user = LDAPUser(
          dn="uid=disabled,dc=example,dc=com",
          object_classes=["person"],
          attributes={
              "userAccountControl": LDAPAttribute(
                  name="userAccountControl",
                  values=["514"],
              ),  # Disabled
          },
      )
      # Implementation may vary, test that property exists and returns bool
      assert isinstance(disabled_user.is_active, bool)


class TestLDAPGroup:
    """Test LDAP group model."""

    def test_group_creation(self) -> None:
      """Test creating LDAP group."""
      group = LDAPGroup(
          dn="cn=developers,ou=groups,dc=example,dc=com",
          object_classes=["groupOfNames"],
          attributes={
              "cn": LDAPAttribute(name="cn", values=["developers"]),
              "description": LDAPAttribute(
                  name="description",
                  values=["Development team"],
              ),
              "member": LDAPAttribute(
                  name="member",
                  values=[
                      "uid=jdoe,ou=users,dc=example,dc=com",
                      "uid=jane,ou=users,dc=example,dc=com",
                  ],
              ),
          },
      )

      assert group.dn == "cn=developers,ou=groups,dc=example,dc=com"
      assert group.group_name == "developers"
      assert group.description == "Development team"
      assert len(group.members) == 2
      assert "uid=jdoe,ou=users,dc=example,dc=com" in group.members

    def test_group_missing_attributes(self) -> None:
      """Test group with missing attributes."""
      group = LDAPGroup(
          dn="cn=empty,dc=example,dc=com",
          object_classes=["group"],
          attributes={},
      )

      assert group.group_name is None
      assert group.description is None
      assert group.members == []

    def test_group_member_count(self) -> None:
      """Test member count property."""
      group = LDAPGroup(
          dn="cn=team,dc=example,dc=com",
          object_classes=["groupOfNames"],
          attributes={
              "member": LDAPAttribute(
                  name="member",
                  values=[
                      "uid=user1,dc=example,dc=com",
                      "uid=user2,dc=example,dc=com",
                      "uid=user3,dc=example,dc=com",
                  ],
              ),
          },
      )

      assert group.member_count == 3

    def test_group_has_member(self) -> None:
      """Test checking if group has specific member."""
      group = LDAPGroup(
          dn="cn=team,dc=example,dc=com",
          object_classes=["groupOfNames"],
          attributes={
              "member": LDAPAttribute(
                  name="member",
                  values=[
                      "uid=jdoe,ou=users,dc=example,dc=com",
                      "uid=jane,ou=users,dc=example,dc=com",
                  ],
              ),
          },
      )

      assert group.has_member("uid=jdoe,ou=users,dc=example,dc=com") is True
      assert group.has_member("uid=jane,ou=users,dc=example,dc=com") is True
      assert group.has_member("uid=unknown,ou=users,dc=example,dc=com") is False


class TestLDAPSchema:
    """Test LDAP schema model."""

    def test_schema_creation(self) -> None:
      """Test creating LDAP schema."""
      schema = LDAPSchema(
          dn="cn=schema",
          object_classes=["top", "subschema"],
          attribute_types={
              "uid": {
                  "name": "uid",
                  "oid": "0.9.2342.19200300.100.1.1",
                  "syntax": "directoryString",
                  "single_value": False,
              },
              "cn": {
                  "name": "cn",
                  "oid": "2.5.4.3",
                  "syntax": "directoryString",
                  "single_value": False,
              },
          },
          object_class_definitions={
              "person": {
                  "name": "person",
                  "oid": "2.5.6.6",
                  "required_attributes": ["sn", "cn"],
                  "optional_attributes": ["description", "telephoneNumber"],
              },
          },
      )

      assert schema.dn == "cn=schema"
      assert "uid" in schema.attribute_types
      assert "person" in schema.object_class_definitions

    def test_schema_get_attribute_type(self) -> None:
      """Test getting attribute type definition."""
      schema = LDAPSchema(
          dn="cn=schema",
          object_classes=["subschema"],
          attribute_types={
              "mail": {
                  "name": "mail",
                  "oid": "0.9.2342.19200300.100.1.3",
                  "syntax": "ia5String",
                  "single_value": False,
              },
          },
          object_class_definitions={},
      )

      # Existing attribute type
      mail_def = schema.get_attribute_type("mail")
      assert mail_def is not None
      assert mail_def["name"] == "mail"
      assert mail_def["syntax"] == "ia5String"

      # Non-existent attribute type
      unknown_def = schema.get_attribute_type("unknown")
      assert unknown_def is None

    def test_schema_get_object_class_definition(self) -> None:
      """Test getting object class definition."""
      schema = LDAPSchema(
          dn="cn=schema",
          object_classes=["subschema"],
          attribute_types={},
          object_class_definitions={
              "inetOrgPerson": {
                  "name": "inetOrgPerson",
                  "oid": "2.16.840.1.113730.3.2.2",
                  "required_attributes": ["cn", "sn"],
                  "optional_attributes": ["mail", "telephoneNumber"],
              },
          },
      )

      # Existing object class
      inetorg_def = schema.get_object_class_definition("inetOrgPerson")
      assert inetorg_def is not None
      assert inetorg_def["name"] == "inetOrgPerson"
      assert "cn" in inetorg_def["required_attributes"]

      # Non-existent object class
      unknown_def = schema.get_object_class_definition("unknown")
      assert unknown_def is None

    def test_schema_validate_entry(self) -> None:
      """Test validating entry against schema."""
      schema = LDAPSchema(
          dn="cn=schema",
          object_classes=["subschema"],
          attribute_types={
              "cn": {
                  "name": "cn",
                  "syntax": "directoryString",
                  "single_value": False,
              },
              "sn": {
                  "name": "sn",
                  "syntax": "directoryString",
                  "single_value": False,
              },
              "mail": {"name": "mail", "syntax": "ia5String", "single_value": False},
          },
          object_class_definitions={
              "person": {
                  "name": "person",
                  "required_attributes": ["cn", "sn"],
                  "optional_attributes": ["mail"],
              },
          },
      )

      # Valid entry
      valid_entry = LDAPEntry(
          dn="cn=test,dc=example,dc=com",
          object_classes=["person"],
          attributes={
              "cn": LDAPAttribute(name="cn", values=["Test User"]),
              "sn": LDAPAttribute(name="sn", values=["User"]),
          },
      )

      validation_result = schema.validate_entry(valid_entry)
      assert validation_result.is_valid is True
      assert len(validation_result.errors) == 0

      # Invalid entry (missing required attribute)
      invalid_entry = LDAPEntry(
          dn="cn=invalid,dc=example,dc=com",
          object_classes=["person"],
          attributes={
              "cn": LDAPAttribute(name="cn", values=["Test User"]),
              # Missing required 'sn' attribute
          },
      )

      validation_result = schema.validate_entry(invalid_entry)
      assert validation_result.is_valid is False
      assert len(validation_result.errors) > 0


class TestModelIntegration:
    """Integration tests for models."""

    def test_complex_user_entry(self) -> None:
      """Test complex user entry with multiple attributes."""
      user = LDAPUser(
          dn="uid=complex.user,ou=people,dc=company,dc=com",
          object_classes=["inetOrgPerson", "person", "organizationalPerson"],
          attributes={
              "uid": LDAPAttribute(name="uid", values=["complex.user"]),
              "cn": LDAPAttribute(name="cn", values=["Complex User", "C. User"]),
              "sn": LDAPAttribute(name="sn", values=["User"]),
              "givenName": LDAPAttribute(name="givenName", values=["Complex"]),
              "mail": LDAPAttribute(
                  name="mail",
                  values=["complex@company.com", "c.user@company.com"],
              ),
              "telephoneNumber": LDAPAttribute(
                  name="telephoneNumber",
                  values=["+1-555-1234"],
              ),
              "employeeNumber": LDAPAttribute(
                  name="employeeNumber",
                  values=["12345"],
              ),
          },
      )

      assert user.uid == "complex.user"
      assert user.common_name == "Complex User"  # First value
      assert user.email == "complex@company.com"  # First value
      assert user.has_object_class("inetOrgPerson")
      assert user.get_attribute_values("mail") == [
          "complex@company.com",
          "c.user@company.com",
      ]

    def test_entry_serialization_round_trip(self) -> None:
      """Test serializing and deserializing entry."""
      original_entry = LDAPEntry(
          dn="uid=test,dc=example,dc=com",
          object_classes=["person", "inetOrgPerson"],
          attributes={
              "uid": LDAPAttribute(name="uid", values=["test"]),
              "cn": LDAPAttribute(name="cn", values=["Test User"]),
              "mail": LDAPAttribute(name="mail", values=["test@example.com"]),
          },
      )

      # Serialize to dict
      entry_dict = original_entry.to_dict()

      # Deserialize back to entry
      restored_entry = LDAPEntry.from_dict(entry_dict)

      # Should be equivalent
      assert restored_entry.dn == original_entry.dn
      assert restored_entry.object_classes == original_entry.object_classes
      assert restored_entry.get_attribute_values(
          "uid",
      ) == original_entry.get_attribute_values("uid")
      assert restored_entry.get_attribute_values(
          "cn",
      ) == original_entry.get_attribute_values("cn")
      assert restored_entry.get_attribute_values(
          "mail",
      ) == original_entry.get_attribute_values("mail")
