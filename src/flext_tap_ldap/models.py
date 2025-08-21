"""Domain models for tap-ldap using flext-core."""

from __future__ import annotations

from datetime import datetime

from flext_core import FlextResult, FlextValue as FlextDomainBaseModel
from flext_ldap import FlextLdapEntry
from pydantic import Field

from flext_tap_ldap.domain.entities import (
    ConnectionTestedEvent,
    LDAPConnection,
    LDAPRecord,
    LDAPStream,
    RecordExtractedEvent,
    StreamDiscoveredEvent,
    TapExecution,
    TapExecutionCompletedEvent,
    TapExecutionStartedEvent,
)


def _get_entry_value(
    entry: dict[str, object] | FlextLdapEntry,
    key: str,
    default: object = None,
) -> object:
    """Get a value from either a dict or `FlextLdapEntry`.

    Returns the attribute value by name from a plain dict or an attribute of
    a `FlextLdapEntry`, falling back to `default` when not present.
    """
    if isinstance(entry, dict):
        return entry.get(key, default)
    # FlextLdapEntry - use getattr or similar access pattern
    return getattr(entry, key, default)


def _safe_list_str(value: object) -> list[str]:
    """Safely coerce a value to list[str]."""
    if isinstance(value, list):
        return [str(v) for v in value]
    if isinstance(value, tuple):
        return [str(v) for v in value]
    if isinstance(value, str):
        # Single string treated as single-element list
        return [value]
    return []


def _safe_first_str(value: object) -> str | None:
    """Safely get the first string from a possibly list-like value."""
    if isinstance(value, list | tuple):
        return str(value[0]) if value else None
    if isinstance(value, str):
        return value
    return None


class LDAPAttribute(FlextDomainBaseModel):
    """Represents an LDAP attribute with its values."""

    name: str = Field(..., description="Attribute name")
    values: list[str] = Field(..., description="Attribute values")
    is_binary: bool = Field(
        default=False,
        description="Whether the attribute contains binary data",
    )

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate business rules for LDAP attributes."""
        # LDAP attributes can have any name and values
        return FlextResult[None].ok(None)

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

    dn: str = Field(..., description="Distinguished Name")
    object_classes: list[str] = Field(..., description="Object classes")

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate business rules for LDAP entries."""
        if not self.dn:
            return FlextResult[None].fail("DN cannot be empty")
        # Additional LDAP entry validation can be added here
        return FlextResult[None].ok(None)

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

    def to_dict(self) -> dict[str, object]:
        """Convert entry to dictionary format.

        Returns:
            Dictionary representation of the LDAP entry.

        """
        result = {
            "dn": self.dn,
            "objectClass": self.object_classes,
        }

        # Add attributes
        for name, value in self.attributes.items():
            if isinstance(value, LDAPAttribute):
                result[name] = value.values
            else:
                result[name] = value

        return result

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> LDAPEntry:
        """Create LDAPEntry from dictionary.

        Args:
            data: Dictionary with entry data.

        Returns:
            LDAPEntry instance.

        """
        return cls(
            dn=str(data.get("dn", "")),
            object_classes=_safe_list_str(data.get("objectClass", [])),
            attributes=data.get("attributes", {}),
        )


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
            # Required fields from LDAPEntry
            dn=str(_get_entry_value(entry, "dn", "")),
            object_classes=_safe_list_str(_get_entry_value(entry, "objectClass", [])),
            # Optional metadata fields from LDAPEntry with defaults
            created_at=None,
            modified_at=None,
            created_by=None,
            modified_by=None,
            change_type=None,
            # LDAPUser specific fields with safe extraction
            uid=_safe_first_str(_get_entry_value(entry, "uid", [])),
            cn=_safe_first_str(_get_entry_value(entry, "cn", [])),
            sn=_safe_first_str(_get_entry_value(entry, "sn", [])),
            given_name=_safe_first_str(_get_entry_value(entry, "givenName", [])),
            display_name=_safe_first_str(_get_entry_value(entry, "displayName", [])),
            mail=_safe_first_str(_get_entry_value(entry, "mail", [])),
            telephone_number=_safe_first_str(
                _get_entry_value(entry, "telephoneNumber", []),
            ),
            mobile=_safe_first_str(_get_entry_value(entry, "mobile", [])),
            employee_number=_safe_first_str(
                _get_entry_value(entry, "employeeNumber", []),
            ),
            employee_type=_safe_first_str(
                _get_entry_value(entry, "employeeType", []),
            ),
            department=_safe_first_str(_get_entry_value(entry, "department", [])),
            title=_safe_first_str(_get_entry_value(entry, "title", [])),
            manager=_safe_first_str(_get_entry_value(entry, "manager", [])),
            home_directory=_safe_first_str(
                _get_entry_value(entry, "homeDirectory", []),
            ),
            login_shell=_safe_first_str(_get_entry_value(entry, "loginShell", [])),
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
            # Required fields from LDAPEntry
            dn=str(_get_entry_value(entry, "dn", "")),
            object_classes=_safe_list_str(_get_entry_value(entry, "objectClass", [])),
            # Optional metadata fields from LDAPEntry with defaults
            created_at=None,
            modified_at=None,
            created_by=None,
            modified_by=None,
            change_type=None,
            # LDAPGroup specific fields with safe extraction
            cn=_safe_first_str(_get_entry_value(entry, "cn", [])),
            description=_safe_first_str(_get_entry_value(entry, "description", [])),
            members=_safe_list_str(_get_entry_value(entry, "member", [])),
            unique_members=_safe_list_str(_get_entry_value(entry, "uniqueMember", [])),
            gid_number=_safe_first_str(_get_entry_value(entry, "gidNumber", [])),
            owner=None,
            create_timestamp=_safe_first_str(
                _get_entry_value(entry, "createTimestamp", []),
            ),
            modify_timestamp=_safe_first_str(
                _get_entry_value(entry, "modifyTimestamp", []),
            ),
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

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate business rules for LDAP schema."""
        # Schema validation rules can be added here
        return FlextResult[None].ok(None)

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


# Public API: expose local value objects and re-exported domain entities/events
__all__ = [
    "ConnectionTestedEvent",
    "LDAPAttribute",
    "LDAPConnection",
    "LDAPEntry",
    "LDAPGroup",
    "LDAPRecord",
    "LDAPSchema",
    "LDAPStream",
    "LDAPUser",
    "RecordExtractedEvent",
    "StreamDiscoveredEvent",
    "TapExecution",
    "TapExecutionCompletedEvent",
    "TapExecutionStartedEvent",
]
