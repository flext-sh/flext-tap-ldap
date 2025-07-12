"""Domain models for tap-ldap using flext-core."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from pydantic import Field

from flext_core.domain.pydantic_base import DomainBaseModel

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
    mail: str | None = Field(None, description="Email address")
    employee_number: str | None = Field(None, description="Employee number")
    department: str | None = Field(None, description="Department")
    title: str | None = Field(None, description="Job title")
    manager: str | None = Field(None, description="Manager DN")

    @classmethod
    def from_entry(cls, entry: LDAPEntry) -> LDAPUser:
        """Create LDAPUser from generic LDAP entry.

        Args:
            entry: Generic LDAP entry to convert.

        Returns:
            LDAPUser instance with extracted user attributes.

        """
        return cls(
            dn=entry.dn,
            object_classes=entry.object_classes,
            attributes=entry.attributes,
            uid=entry.get_attribute("uid"),
            cn=entry.get_attribute("cn"),
            sn=entry.get_attribute("sn"),
            given_name=entry.get_attribute("givenName"),
            mail=entry.get_attribute("mail"),
            employee_number=entry.get_attribute("employeeNumber"),
            department=entry.get_attribute("department"),
            title=entry.get_attribute("title"),
            manager=entry.get_attribute("manager"),
        )


class LDAPGroup(LDAPEntry):
    """Represents an LDAP group entry."""

    cn: str | None = Field(None, description="Group name")
    description: str | None = Field(None, description="Group description")
    members: list[str] = Field(default_factory=list, description="Member DNs")
    owner: str | None = Field(None, description="Group owner DN")

    @classmethod
    def from_entry(cls, entry: LDAPEntry) -> LDAPGroup:
        """Create LDAPGroup from generic LDAP entry.

        Args:
            entry: Generic LDAP entry to convert.

        Returns:
            LDAPGroup instance with extracted group attributes.

        """
        members = (
            entry.get_attribute("member") or entry.get_attribute("uniqueMember") or []
        )
        if isinstance(members, str):
            members = [members]

        return cls(
            dn=entry.dn,
            object_classes=entry.object_classes,
            attributes=entry.attributes,
            cn=entry.get_attribute("cn"),
            description=entry.get_attribute("description"),
            members=members,
            owner=entry.get_attribute("owner"),
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
