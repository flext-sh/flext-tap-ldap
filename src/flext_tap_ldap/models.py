"""Domain models for tap-ldap using flext-core."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core import FlextResult, FlextValueObject as FlextDomainBaseModel
from pydantic import Field

if TYPE_CHECKING:
    from datetime import datetime

    from flext_ldap import FlextLdapEntry


def _get_entry_value(entry: dict[str, object] | FlextLdapEntry, key: str, default: object = None) -> object:
    """Helper function to get value from either dict or FlextLdapEntry."""
    if isinstance(entry, dict):
        return entry.get(key, default)
    # FlextLdapEntry - use getattr or similar access pattern
    return getattr(entry, key, default)


class LDAPAttribute(FlextDomainBaseModel):
    """Represents an LDAP attribute with its values."""

    name: str = Field(..., description="Attribute name")
    values: list[str] = Field(..., description="Attribute values")
    is_binary: bool = Field(
        default=False,
        description="Whether the attribute contains binary data",
    )

    def validate_domain_rules(self) -> FlextResult[None]:
        """Validate domain-specific rules for LDAP attributes."""
        # LDAP attributes can have any name and values
        return FlextResult.ok(None)

    @property
    def single_value(self) -> str | None:
        """Get first value if exists, None otherwise.

        Returns:
            First value from values list or None if empty.

        """
        return self.values[0] if self.values else None

    @property
    def is_multi_valued(self) -> bool:
        """Check if attribute has multiple values.

        Returns:
            True if attribute has more than one value.

        """
        return len(self.values) > 1


class LDAPEntry(FlextDomainBaseModel):
    """Represents an LDAP entry."""

    dn: str = Field(..., description="Distinguished Name", alias="id")
    object_classes: list[str] = Field(..., description="Object classes")

    def validate_domain_rules(self) -> FlextResult[None]:
        """Validate domain-specific rules for LDAP entries."""
        if not self.dn:
            return FlextResult.fail("DN cannot be empty")
        # Additional LDAP entry validation can be added here
        return FlextResult.ok(None)

    attributes: dict[str, object] = Field(
        default_factory=dict,
        description="Entry attributes",
    )

    # Metadata
    created_at: datetime | None = Field(None, description="Entry creation time")
    modified_at: datetime | None = Field(None, description="Entry modification time")
    created_by: str | None = Field(None, description="Entry creator")
    modified_by: str | None = Field(None, description="Entry modifier")

    # Change tracking
    change_type: str | None = Field(
        None,
        description="LDIF change type (add, modify, delete)",
    )
    controls: list[str] = Field(default_factory=list, description="LDAP controls")

    @property
    def id(self) -> str:
        """Get unique identifier for LDAP entry.

        Returns:
            Distinguished Name as unique identifier.

        """
        return self.dn

    def get_attribute(self, name: str) -> object | None:
        """Get attribute value by name (case-insensitive).

        Args:
            name: Attribute name to retrieve.

        Returns:
            Attribute value if found, None otherwise.

        """
        # LDAP attributes are case-insensitive
        for key, value in self.attributes.items():
            if key.lower() == name.lower():
                return value
        return None

    def has_object_class(self, object_class: str) -> bool:
        """Check if entry has specific object class.

        Args:
            object_class: Object class name to check.

        Returns:
            True if entry has the specified object class (case-insensitive).

        """
        return any(oc.lower() == object_class.lower() for oc in self.object_classes)


class LDAPUser(LDAPEntry):
    """Represents an LDAP user entry."""

    uid: str | None = Field(None, description="User ID")
    cn: str | None = Field(None, description="Common name")
    sn: str | None = Field(None, description="Surname")
    given_name: str | None = Field(None, description="Given name")
    display_name: str | None = Field(None, description="Display name")
    mail: str | None = Field(None, description="Email address")
    telephone_number: str | None = Field(None, description="Telephone number")
    mobile: str | None = Field(None, description="Mobile number")
    employee_number: str | None = Field(None, description="Employee number")
    employee_type: str | None = Field(None, description="Employee type")
    department: str | None = Field(None, description="Department")
    title: str | None = Field(None, description="Job title")
    manager: str | None = Field(None, description="Manager DN")
    home_directory: str | None = Field(None, description="Home directory")
    login_shell: str | None = Field(None, description="Login shell")

    @classmethod
    def from_entry(cls, entry: dict[str, object] | FlextLdapEntry) -> LDAPUser:
        """Create LDAPUser from LDAP entry."""
        return cls(
            # Required fields from LDAPEntry using alias 'id' for dn
            id=str(_get_entry_value(entry, "dn", "")),
            object_classes=list(_get_entry_value(entry, "objectClass", [])),  # type: ignore[call-overload]
            # Optional metadata fields from LDAPEntry with defaults
            created_at=None,
            modified_at=None,
            created_by=None,
            modified_by=None,
            change_type=None,
            # LDAPUser specific fields with defaults
            uid=str(_get_entry_value(entry, "uid", [None])[0]) if _get_entry_value(entry, "uid", [None]) else None,  # type: ignore[index]
            cn=str(_get_entry_value(entry, "cn", [None])[0]) if _get_entry_value(entry, "cn", [None]) else None,  # type: ignore[index]
            sn=str(_get_entry_value(entry, "sn", [None])[0]) if _get_entry_value(entry, "sn", [None]) else None,  # type: ignore[index]
            given_name=str(_get_entry_value(entry, "givenName", [None])[0]) if _get_entry_value(entry, "givenName", [None]) else None,  # type: ignore[index]
            display_name=str(_get_entry_value(entry, "displayName", [None])[0]) if _get_entry_value(entry, "displayName", [None]) else None,  # type: ignore[index]
            mail=str(_get_entry_value(entry, "mail", [None])[0]) if _get_entry_value(entry, "mail", [None]) else None,  # type: ignore[index]
            telephone_number=str(_get_entry_value(entry, "telephoneNumber", [None])[0]) if _get_entry_value(entry, "telephoneNumber", [None]) else None,  # type: ignore[index]
            mobile=str(_get_entry_value(entry, "mobile", [None])[0]) if _get_entry_value(entry, "mobile", [None]) else None,  # type: ignore[index]
            employee_number=str(_get_entry_value(entry, "employeeNumber", [None])[0]) if _get_entry_value(entry, "employeeNumber", [None]) else None,  # type: ignore[index]
            employee_type=str(_get_entry_value(entry, "employeeType", [None])[0]) if _get_entry_value(entry, "employeeType", [None]) else None,  # type: ignore[index]
            department=str(_get_entry_value(entry, "department", [None])[0]) if _get_entry_value(entry, "department", [None]) else None,  # type: ignore[index]
            title=str(_get_entry_value(entry, "title", [None])[0]) if _get_entry_value(entry, "title", [None]) else None,  # type: ignore[index]
            manager=str(_get_entry_value(entry, "manager", [None])[0]) if _get_entry_value(entry, "manager", [None]) else None,  # type: ignore[index]
            home_directory=str(_get_entry_value(entry, "homeDirectory", [None])[0]) if _get_entry_value(entry, "homeDirectory", [None]) else None,  # type: ignore[index]
            login_shell=str(_get_entry_value(entry, "loginShell", [None])[0]) if _get_entry_value(entry, "loginShell", [None]) else None,  # type: ignore[index]
        )


class LDAPGroup(LDAPEntry):
    """Represents an LDAP group entry."""

    cn: str | None = Field(None, description="Group name")
    description: str | None = Field(None, description="Group description")
    members: list[str] = Field(default_factory=list, description="Member DNs")
    unique_members: list[str] = Field(
        default_factory=list,
        description="Unique member DNs",
    )
    gid_number: str | None = Field(None, description="Group ID number")
    owner: str | None = Field(None, description="Group owner DN")
    create_timestamp: str | None = Field(None, description="Creation timestamp")
    modify_timestamp: str | None = Field(None, description="Modification timestamp")

    @classmethod
    def from_entry(cls, entry: dict[str, object] | FlextLdapEntry) -> LDAPGroup:
        """Create LDAPGroup from LDAP entry."""
        return cls(
            # Required fields from LDAPEntry using alias 'id' for dn
            id=str(_get_entry_value(entry, "dn", "")),
            object_classes=list(_get_entry_value(entry, "objectClass", [])),  # type: ignore[call-overload]
            # Optional metadata fields from LDAPEntry with defaults
            created_at=None,
            modified_at=None,
            created_by=None,
            modified_by=None,
            change_type=None,
            # LDAPGroup specific fields with defaults
            cn=str(_get_entry_value(entry, "cn", [None])[0]) if _get_entry_value(entry, "cn", [None]) else None,  # type: ignore[index]
            description=str(_get_entry_value(entry, "description", [None])[0]) if _get_entry_value(entry, "description", [None]) else None,  # type: ignore[index]
            members=list(_get_entry_value(entry, "member", [])),  # type: ignore[call-overload]
            unique_members=list(_get_entry_value(entry, "uniqueMember", [])),  # type: ignore[call-overload]
            gid_number=str(_get_entry_value(entry, "gidNumber", [None])[0]) if _get_entry_value(entry, "gidNumber", [None]) else None,  # type: ignore[index]
            owner=None,
            create_timestamp=str(_get_entry_value(entry, "createTimestamp", [None])[0]) if _get_entry_value(entry, "createTimestamp", [None]) else None,  # type: ignore[index]
            modify_timestamp=str(_get_entry_value(entry, "modifyTimestamp", [None])[0]) if _get_entry_value(entry, "modifyTimestamp", [None]) else None,  # type: ignore[index]
        )


class LDAPSchema(FlextDomainBaseModel):
    """Represents LDAP schema information."""

    object_classes: list[str] = Field(
        default_factory=list,
        description="Available object classes",
    )
    attribute_types: list[str] = Field(
        default_factory=list,
        description="Available attribute types",
    )
    ldap_syntaxes: list[str] = Field(default_factory=list, description="LDAP syntaxes")
    naming_contexts: list[str] = Field(
        default_factory=list,
        description="Naming contexts",
    )

    def validate_domain_rules(self) -> FlextResult[None]:
        """Validate domain-specific rules for LDAP schema."""
        # Schema validation rules can be added here
        return FlextResult.ok(None)

    @property
    def has_oracle_extensions(self) -> bool:
        """Check if schema contains Oracle-specific extensions.

        Returns:
            True if schema contains Oracle LDAP extensions.

        """
        oracle_prefixes = ["orcl", "oracl", "oid"]
        return any(
            any(oc.lower().startswith(prefix) for prefix in oracle_prefixes)
            for oc in self.object_classes
        )
