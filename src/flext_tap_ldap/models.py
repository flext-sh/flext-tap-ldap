"""Domain models for tap-ldap using flext-core."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

# 🚨 ARCHITECTURAL COMPLIANCE: Using DI container
from flext_tap_ldap.infrastructure.di_container import (
    get_base_config,
    get_domain_entity,
    get_domain_value_object,
    get_field,
    get_service_result,
)

ServiceResult = get_service_result()
DomainEntity = get_domain_entity()
Field = get_field()
DomainValueObject = get_domain_value_object()
BaseConfig = get_base_config()
from pydantic import Field

if TYPE_CHECKING:
    from datetime import datetime


class LDAPAttribute(DomainBaseModel):
    """Represents an LDAP attribute with its values."""

    name: str = Field(..., description="Attribute name")
    values: list[str] = Field(..., description="Attribute values")
    is_binary: bool = Field(
        False,
        description="Whether the attribute contains binary data",
    )

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


class LDAPEntry(DomainBaseModel):
    """Represents an LDAP entry."""

    dn: str = Field(..., description="Distinguished Name", alias="id")
    object_classes: list[str] = Field(..., description="Object classes")
    attributes: dict[str, Any] = Field(
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

    def get_attribute(self, name: str) -> Any | None:
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
    def from_entry(cls, entry: Any) -> LDAPUser:
        """Create LDAPUser from LDAP entry."""
        return cls(
            # Required fields from LDAPEntry using alias 'id' for dn
            id=entry.get("dn", ""),
            object_classes=entry.get("objectClass", []),
            # Optional metadata fields from LDAPEntry with defaults
            created_at=None,
            modified_at=None,
            created_by=None,
            modified_by=None,
            change_type=None,
            # LDAPUser specific fields with defaults
            uid=entry.get("uid", [None])[0],
            cn=entry.get("cn", [None])[0],
            sn=entry.get("sn", [None])[0],
            given_name=entry.get("givenName", [None])[0],
            display_name=entry.get("displayName", [None])[0],
            mail=entry.get("mail", [None])[0],
            telephone_number=entry.get("telephoneNumber", [None])[0],
            mobile=entry.get("mobile", [None])[0],
            employee_number=entry.get("employeeNumber", [None])[0],
            employee_type=entry.get("employeeType", [None])[0],
            department=entry.get("department", [None])[0],
            title=entry.get("title", [None])[0],
            manager=entry.get("manager", [None])[0],
            home_directory=entry.get("homeDirectory", [None])[0],
            login_shell=entry.get("loginShell", [None])[0],
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
    def from_entry(cls, entry: Any) -> LDAPGroup:
        """Create LDAPGroup from LDAP entry."""
        return cls(
            # Required fields from LDAPEntry using alias 'id' for dn
            id=entry.get("dn", ""),
            object_classes=entry.get("objectClass", []),
            # Optional metadata fields from LDAPEntry with defaults
            created_at=None,
            modified_at=None,
            created_by=None,
            modified_by=None,
            change_type=None,
            # LDAPGroup specific fields with defaults
            cn=entry.get("cn", [None])[0],
            description=entry.get("description", [None])[0],
            members=entry.get("member", []),
            unique_members=entry.get("uniqueMember", []),
            gid_number=entry.get("gidNumber", [None])[0],
            owner=None,
            create_timestamp=entry.get("createTimestamp", [None])[0],
            modify_timestamp=entry.get("modifyTimestamp", [None])[0],
        )


class LDAPSchema(DomainBaseModel):
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
