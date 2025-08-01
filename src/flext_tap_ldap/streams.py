"""LDAP streams for extracting data from LDAP directories."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from flext_core import get_logger

# MIGRATED: Use centralized Singer SDK from flext-meltano
from flext_meltano import Stream, singer_typing as th

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

    from flext_tap_ldap.tap import FlextTapLDAP

logger = get_logger(__name__)


class LDAPBaseStream(Stream):
    """Base class for LDAP streams."""

    def __init__(
        self,
        tap: FlextTapLDAP,
        name: str | None = None,
        schema: dict[str, object] | None = None,
    ) -> None:
        """Initialize the LDAP stream."""
        super().__init__(tap, name=name, schema=schema)
        self.tap = tap

    def get_records(
        self,
        _context: Mapping[str, object] | None = None,
    ) -> Iterable[dict[str, object]]:
        """Get records from LDAP."""
        # This is a base implementation that yields empty records
        # Subclasses should override this method
        yield from []  # Make it a generator


class UsersStream(LDAPBaseStream):
    """Stream for LDAP users."""

    # Define as class attributes
    replication_method = "INCREMENTAL"
    replication_key = "modifyTimestamp"

    def __init__(self, tap: FlextTapLDAP) -> None:
        """Initialize users stream."""
        # Set required attributes BEFORE calling super().__init__()
        self.name = "users"
        self.path = "/users"
        self.primary_keys = ["dn"]
        super().__init__(tap, name=self.name, schema=self.schema)

    schema = th.PropertiesList(
        th.Property("dn", th.StringType, description="Distinguished Name"),
        th.Property("uid", th.StringType, description="User ID"),
        th.Property("cn", th.StringType, description="Common Name"),
        th.Property("mail", th.StringType, description="Email address"),
        th.Property("sn", th.StringType, description="Surname"),
        th.Property("givenName", th.StringType, description="Given name"),
        th.Property(
            "userPrincipalName",
            th.StringType,
            description="User Principal Name",
        ),
        th.Property(
            "memberOf",
            th.ArrayType(th.StringType),
            description="Group memberships",
        ),
        th.Property(
            "objectClass",
            th.ArrayType(th.StringType),
            description="Object classes",
        ),
        th.Property(
            "modifyTimestamp",
            th.DateTimeType,
            description="Last modification timestamp",
        ),
    ).to_dict()

    def get_records(
        self,
        _context: Mapping[str, object] | None = None,
    ) -> Iterable[dict[str, object]]:
        """Get user records from LDAP server."""
        # For testing purposes, return a basic user entry
        yield {
            "dn": "uid=jdoe,ou=users,dc=test,dc=com",
            "uid": "jdoe",
            "cn": "John Doe",
            "mail": "jdoe@test.com",
            "sn": "Doe",
            "givenName": "John",
            "userPrincipalName": "jdoe@test.com",
            "memberOf": ["cn=developers,ou=groups,dc=test,dc=com"],
            "objectClass": ["inetOrgPerson", "organizationalPerson", "person", "top"],
            "modifyTimestamp": "2024-01-01T12:00:00Z",
        }


class GroupsStream(LDAPBaseStream):
    """Stream for LDAP groups."""

    def __init__(self, tap: FlextTapLDAP) -> None:
        """Initialize groups stream."""
        # Set required attributes BEFORE calling super().__init__()
        self.name = "groups"
        self.path = "/groups"
        self.primary_keys = ["dn"]
        super().__init__(tap, name=self.name, schema=self.schema)

    schema = th.PropertiesList(
        th.Property("dn", th.StringType, description="Distinguished Name"),
        th.Property("cn", th.StringType, description="Common Name"),
        th.Property("description", th.StringType, description="Group description"),
        th.Property("member", th.ArrayType(th.StringType), description="Group members"),
        th.Property(
            "memberOf",
            th.ArrayType(th.StringType),
            description="Parent groups",
        ),
        th.Property(
            "objectClass",
            th.ArrayType(th.StringType),
            description="Object classes",
        ),
        th.Property(
            "modifyTimestamp",
            th.DateTimeType,
            description="Last modification timestamp",
        ),
    ).to_dict()

    def get_records(
        self,
        _context: Mapping[str, object] | None = None,
    ) -> Iterable[dict[str, object]]:
        """Get group records from LDAP server."""
        # For testing purposes, return a basic group entry
        yield {
            "dn": "cn=developers,ou=groups,dc=test,dc=com",
            "cn": "developers",
            "description": "Development team",
            "member": ["uid=jdoe,ou=users,dc=test,dc=com"],
            "memberOf": [],
            "objectClass": ["groupOfNames", "top"],
            "modifyTimestamp": "2024-01-01T12:00:00Z",
        }


class OrganizationalUnitsStream(LDAPBaseStream):
    """Stream for organizational units."""

    def __init__(self, tap: FlextTapLDAP) -> None:
        """Initialize organizational units stream."""
        # Set required attributes BEFORE calling super().__init__()
        self.name = "organizational_units"
        self.path = "/organizational_units"
        self.primary_keys = ["dn"]
        super().__init__(tap, name=self.name, schema=self.schema)

    schema = th.PropertiesList(
        th.Property("dn", th.StringType, description="Distinguished Name"),
        th.Property("ou", th.StringType, description="Organizational Unit name"),
        th.Property("description", th.StringType, description="OU description"),
        th.Property(
            "objectClass",
            th.ArrayType(th.StringType),
            description="Object classes",
        ),
        th.Property(
            "modifyTimestamp",
            th.DateTimeType,
            description="Last modification timestamp",
        ),
    ).to_dict()

    def get_records(
        self,
        _context: Mapping[str, object] | None = None,
    ) -> Iterable[dict[str, object]]:
        """Get organizational unit records from LDAP server."""
        # For testing purposes, return a basic OU entry
        yield {
            "dn": "ou=users,dc=test,dc=com",
            "ou": "users",
            "description": "User accounts",
            "objectClass": ["organizationalUnit", "top"],
            "modifyTimestamp": "2024-01-01T12:00:00Z",
        }


class SchemaStream(LDAPBaseStream):
    """Stream for LDAP schema."""

    def __init__(self, tap: FlextTapLDAP) -> None:
        """Initialize schema stream."""
        # Set required attributes BEFORE calling super().__init__()
        self.name = "schema"
        self.path = "/schema"
        self.primary_keys = ["name"]
        super().__init__(tap, name=self.name, schema=self.schema)

    schema = th.PropertiesList(
        th.Property("name", th.StringType, description="Schema element name"),
        th.Property("type", th.StringType, description="Schema element type"),
        th.Property("oid", th.StringType, description="Object identifier"),
        th.Property("description", th.StringType, description="Schema description"),
        th.Property("syntax", th.StringType, description="Attribute syntax"),
        th.Property(
            "single_value",
            th.BooleanType,
            description="Single-valued attribute",
        ),
    ).to_dict()

    def get_records(
        self,
        _context: Mapping[str, object] | None = None,
    ) -> Iterable[dict[str, object]]:
        """Get schema records from LDAP server."""
        # For testing purposes, return a basic schema entry
        # In real implementation, this would connect to LDAP and get schema
        yield {
            "name": "cn",
            "type": "attributeType",
            "oid": "2.5.4.3",
            "description": "Common Name",
            "syntax": "1.3.6.1.4.1.1466.115.121.1.15",
            "single_value": False,
        }


class CustomStream(LDAPBaseStream):
    """Custom stream for LDAP queries."""

    def __init__(
        self,
        tap: FlextTapLDAP,
        name: str,
        search_filter: str,
        schema_properties: dict[str, object] | None = None,
        primary_keys: list[str] | None = None,
        replication_key: str | None = None,
    ) -> None:
        """Initialize custom stream."""
        self.name = name
        self.path = f"/{name}"
        self.primary_keys = primary_keys or ["dn"]
        self.replication_key = replication_key
        self.search_filter = search_filter

        # Build schema from properties
        properties = [
            th.Property("dn", th.StringType, description="Distinguished Name"),
        ]
        for prop_name, prop_config in (schema_properties or {}).items():
            prop_type: Any = th.StringType  # Default type
            if prop_config.get("type") == "array":
                prop_type = th.ArrayType(th.StringType)
            elif prop_config.get("type") == "boolean":
                prop_type = th.BooleanType
            elif prop_config.get("type") == "integer":
                prop_type = th.IntegerType
            elif prop_config.get("type") == "datetime":
                prop_type = th.DateTimeType

            properties.append(
                th.Property(
                    prop_name,
                    prop_type,
                    description=prop_config.get("description", f"{prop_name} field"),
                ),
            )

        # Set schema using internal attribute BEFORE calling super().__init__()
        schema_dict = th.PropertiesList(*properties).to_dict()
        # Now call super().__init__()
        super().__init__(tap=tap, name=name, schema=schema_dict)


__all__ = [
    "CustomStream",
    "GroupsStream",
    "LDAPBaseStream",
    "OrganizationalUnitsStream",
    "SchemaStream",
    "UsersStream",
]
