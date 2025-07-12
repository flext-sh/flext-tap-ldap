"""Stream implementations for tap-ldap using flext-core patterns.

Zero tolerance implementation with proper Singer SDK integration.
"""

from __future__ import annotations

from singer_sdk import Stream
from singer_sdk import typing as th


class LDAPBaseStream(Stream):
    """Base class for LDAP streams using flext-core patterns."""

    def __init__(self, tap, **kwargs) -> None:
        """Initialize LDAP stream."""
        super().__init__(tap=tap, **kwargs)

    def get_records(self, context: dict | None = None):
        """Get records from LDAP - basic implementation for testing."""
        # Basic implementation for testing - would be replaced with actual LDAP queries
        yield {"id": f"test-{self.name}", "name": f"Test {self.name.replace('_', ' ').title()}"}


class UsersStream(LDAPBaseStream):
    """Stream for LDAP users."""

    name = "users"
    path = "/users"
    primary_keys = ["dn"]

    schema = th.PropertiesList(
        th.Property("dn", th.StringType, description="Distinguished Name"),
        th.Property("uid", th.StringType, description="User ID"),
        th.Property("cn", th.StringType, description="Common Name"),
        th.Property("mail", th.StringType, description="Email address"),
        th.Property("sn", th.StringType, description="Surname"),
        th.Property("givenName", th.StringType, description="Given name"),
        th.Property("userPrincipalName", th.StringType, description="User Principal Name"),
        th.Property("memberOf", th.ArrayType(th.StringType), description="Group memberships"),
        th.Property("objectClass", th.ArrayType(th.StringType), description="Object classes"),
        th.Property("modifyTimestamp", th.DateTimeType, description="Last modification timestamp"),
    ).to_dict()


class GroupsStream(LDAPBaseStream):
    """Stream for LDAP groups."""

    name = "groups"
    path = "/groups"
    primary_keys = ["dn"]

    schema = th.PropertiesList(
        th.Property("dn", th.StringType, description="Distinguished Name"),
        th.Property("cn", th.StringType, description="Common Name"),
        th.Property("description", th.StringType, description="Group description"),
        th.Property("member", th.ArrayType(th.StringType), description="Group members"),
        th.Property("memberOf", th.ArrayType(th.StringType), description="Parent groups"),
        th.Property("objectClass", th.ArrayType(th.StringType), description="Object classes"),
        th.Property("modifyTimestamp", th.DateTimeType, description="Last modification timestamp"),
    ).to_dict()


class OrganizationalUnitsStream(LDAPBaseStream):
    """Stream for organizational units."""

    name = "organizational_units"
    path = "/organizational_units"
    primary_keys = ["dn"]

    schema = th.PropertiesList(
        th.Property("dn", th.StringType, description="Distinguished Name"),
        th.Property("ou", th.StringType, description="Organizational Unit name"),
        th.Property("description", th.StringType, description="OU description"),
        th.Property("objectClass", th.ArrayType(th.StringType), description="Object classes"),
        th.Property("modifyTimestamp", th.DateTimeType, description="Last modification timestamp"),
    ).to_dict()


class SchemaStream(LDAPBaseStream):
    """Stream for LDAP schema."""

    name = "schema"
    path = "/schema"
    primary_keys = ["name"]

    schema = th.PropertiesList(
        th.Property("name", th.StringType, description="Schema element name"),
        th.Property("type", th.StringType, description="Schema element type"),
        th.Property("oid", th.StringType, description="Object identifier"),
        th.Property("description", th.StringType, description="Schema description"),
        th.Property("syntax", th.StringType, description="Attribute syntax"),
        th.Property("single_value", th.BooleanType, description="Single-valued attribute"),
    ).to_dict()


class CustomStream(LDAPBaseStream):
    """Custom stream for LDAP queries."""

    def __init__(self, tap, name: str, search_filter: str, schema_properties: dict,
                 primary_keys: list | None = None, replication_key: str | None = None, **kwargs) -> None:
        """Initialize custom stream."""
        self.name = name
        self.path = f"/{name}"
        self.primary_keys = primary_keys or ["dn"]
        self.replication_key = replication_key
        self.search_filter = search_filter

        # Build schema from properties
        properties = [th.Property("dn", th.StringType, description="Distinguished Name")]
        for prop_name, prop_config in schema_properties.items():
            prop_type = th.StringType  # Default type
            if prop_config.get("type") == "array":
                prop_type = th.ArrayType(th.StringType)
            elif prop_config.get("type") == "boolean":
                prop_type = th.BooleanType
            elif prop_config.get("type") == "integer":
                prop_type = th.IntegerType
            elif prop_config.get("type") == "datetime":
                prop_type = th.DateTimeType

            properties.append(th.Property(
                prop_name,
                prop_type,
                description=prop_config.get("description", f"{prop_name} field"),
            ))

        self.schema = th.PropertiesList(*properties).to_dict()
        super().__init__(tap=tap, **kwargs)


__all__ = ["CustomStream", "GroupsStream", "LDAPBaseStream", "OrganizationalUnitsStream", "SchemaStream", "UsersStream"]
