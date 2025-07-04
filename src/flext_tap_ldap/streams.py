"""Stream implementations for tap-ldap.

This module defines the various streams for extracting different types of
data from LDAP directories.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, ClassVar

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

from singer_sdk import typing as th
from singer_sdk.streams import Stream
from tap_ldap.client import LDAPClient

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

    from tap_ldap.tap import TapLDAP

logger = logging.getLogger(__name__)


class LDAPStream(Stream):
    """Base class for LDAP streams."""

    tap_name: str = "tap-ldap"

    def __init__(self, tap: TapLDAP, name: str | None = None) -> None:
        """Initialize LDAP stream with required attributes."""
        # Set required attributes BEFORE super().__init__
        self.tap_name = "tap-ldap"
        self.logger = logger
        super().__init__(tap, name=name)
        self._client: LDAPClient | None = None

    @property
    def client(self) -> LDAPClient:
        """Get LDAP client instance."""
        if self._client is None:
            config = self.config
            self._client = LDAPClient(
                host=config["host"],
                port=config.get("port", 389),
                bind_dn=config.get("bind_dn"),
                password=config.get("password"),
                use_ssl=config.get("use_ssl", False),
                timeout=config.get("timeout", 30),
                page_size=config.get("page_size", 1000),
            )
        return self._client

    def get_records(
        self,
        context: Mapping[str, Any] | None = None,
    ) -> Iterable[dict[str, Any]]:
        """Get records from LDAP.

        Args:
        ----
            context: Stream context

        Yields:
        ------
            Record dicts

        """
        base_dn = self.config.get("base_dn", "")
        search_filter = self.get_search_filter()
        attributes = self.get_attributes()

        for entry in self.client.search(
            base_dn=base_dn,
            search_filter=search_filter,
            attributes=attributes,
        ):
            yield self.transform_record(entry)

    def get_search_filter(self) -> str:
        """Get LDAP search filter for this stream.

        Returns:
        -------
            LDAP filter string

        """
        return "(objectClass=*)"

    def get_attributes(self) -> list[str] | None:
        """Get list of attributes to retrieve.

        Returns:
        -------
            List of attribute names or None for all

        """
        return None

    def transform_record(self, entry: dict[str, Any]) -> dict[str, Any]:
        """Transform LDAP entry to stream record.

        Args:
        ----
            entry: LDAP entry dict

        Returns:
        -------
            Transformed record

        """
        record = {
            "dn": entry["dn"],
            **entry.get("attributes", {}),
        }

        # Convert datetime objects to ISO format
        for key, value in record.items():
            if isinstance(value, datetime):
                record[key] = value.isoformat()
            elif isinstance(value, list) and value and isinstance(value[0], datetime):
                record[key] = [v.isoformat() for v in value]

        return record


class UsersStream(LDAPStream):
    """Stream for LDAP user entries."""

    name = "users"
    schema: ClassVar[dict[str, Any]] = th.PropertiesList(
        th.Property(
            "dn",
            th.StringType,
            required=True,
            description="Distinguished Name",
        ),
        th.Property("uid", th.StringType, description="User ID"),
        th.Property("cn", th.StringType, description="Common Name"),
        th.Property("sn", th.StringType, description="Surname"),
        th.Property("givenName", th.StringType, description="Given Name"),
        th.Property("mail", th.StringType, description="Email Address"),
        th.Property("userPassword", th.StringType, description="User Password Hash"),
        th.Property(
            "objectClass",
            th.ArrayType(th.StringType),
            description="Object Classes",
        ),
        th.Property(
            "memberOf",
            th.ArrayType(th.StringType),
            description="Group Memberships",
        ),
        th.Property("createTimestamp", th.DateTimeType, description="Creation Time"),
        th.Property(
            "modifyTimestamp",
            th.DateTimeType,
            description="Last Modified Time",
        ),
    ).to_dict()

    primary_keys: ClassVar[list[str]] = ["dn"]
    replication_key = "modifyTimestamp"
    is_sorted = False

    def get_search_filter(self) -> str:
        """Get user-specific search filter."""
        user_filter: str = self.config.get("user_filter", "(objectClass=inetOrgPerson)")

        # Add incremental sync filter if applicable
        if self.replication_key:
            starting_timestamp = self.get_starting_timestamp(None)
            if starting_timestamp and isinstance(starting_timestamp, datetime):
                timestamp_str = starting_timestamp.strftime("%Y%m%d%H%M%S.%fZ")
                user_filter = f"(&{user_filter}(modifyTimestamp>={timestamp_str}))"

        return user_filter

    def get_attributes(self) -> list[str]:
        """Get user attributes to retrieve."""
        return [
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
        ]


class GroupsStream(LDAPStream):
    """Stream for LDAP group entries."""

    name = "groups"
    schema: ClassVar[dict[str, Any]] = th.PropertiesList(
        th.Property(
            "dn",
            th.StringType,
            required=True,
            description="Distinguished Name",
        ),
        th.Property("cn", th.StringType, description="Common Name"),
        th.Property("description", th.StringType, description="Description"),
        th.Property("member", th.ArrayType(th.StringType), description="Member DNs"),
        th.Property(
            "memberUid",
            th.ArrayType(th.StringType),
            description="Member UIDs",
        ),
        th.Property(
            "objectClass",
            th.ArrayType(th.StringType),
            description="Object Classes",
        ),
        th.Property("createTimestamp", th.DateTimeType, description="Creation Time"),
        th.Property(
            "modifyTimestamp",
            th.DateTimeType,
            description="Last Modified Time",
        ),
    ).to_dict()

    primary_keys: ClassVar[list[str]] = ["dn"]
    replication_key = "modifyTimestamp"
    is_sorted = False

    def get_search_filter(self) -> str:
        """Get group-specific search filter."""
        return self.config.get("group_filter", "(objectClass=groupOfNames)")

    def get_attributes(self) -> list[str]:
        """Get group attributes to retrieve."""
        return [
            "cn",
            "description",
            "member",
            "memberUid",
            "objectClass",
            "createTimestamp",
            "modifyTimestamp",
        ]


class OrganizationalUnitsStream(LDAPStream):
    """Stream for LDAP organizational unit entries."""

    name = "organizational_units"
    schema: ClassVar[dict[str, Any]] = th.PropertiesList(
        th.Property(
            "dn",
            th.StringType,
            required=True,
            description="Distinguished Name",
        ),
        th.Property("ou", th.StringType, description="Organizational Unit Name"),
        th.Property("description", th.StringType, description="Description"),
        th.Property("businessCategory", th.StringType, description="Business Category"),
        th.Property(
            "objectClass",
            th.ArrayType(th.StringType),
            description="Object Classes",
        ),
        th.Property("createTimestamp", th.DateTimeType, description="Creation Time"),
        th.Property(
            "modifyTimestamp",
            th.DateTimeType,
            description="Last Modified Time",
        ),
    ).to_dict()

    primary_keys: ClassVar[list[str]] = ["dn"]
    replication_key = "modifyTimestamp"
    is_sorted = False

    def get_search_filter(self) -> str:
        """Get OU-specific search filter."""
        return "(objectClass=organizationalUnit)"

    def get_attributes(self) -> list[str]:
        """Get OU attributes to retrieve."""
        return [
            "ou",
            "description",
            "businessCategory",
            "objectClass",
            "createTimestamp",
            "modifyTimestamp",
        ]


class SchemaStream(LDAPStream):
    """Stream for LDAP schema information."""

    name = "schema"
    schema: ClassVar[dict[str, Any]] = th.PropertiesList(
        th.Property("type", th.StringType, required=True, description="Schema Type"),
        th.Property("name", th.StringType, required=True, description="Schema Name"),
        th.Property("definition", th.StringType, description="Schema Definition"),
        th.Property(
            "extracted_at",
            th.DateTimeType,
            description="Extraction Timestamp",
        ),
    ).to_dict()

    primary_keys: ClassVar[list[str]] = ["type", "name"]

    def get_records(
        self,
        context: Mapping[str, Any] | None = None,
    ) -> Iterable[dict[str, Any]]:
        """Get schema records from LDAP.

        Args:
        ----
            context: Stream context

        Yields:
        ------
            Schema records

        """
        schema_info = self.client.get_schema()
        extracted_at = datetime.now(UTC).isoformat()

        # Process object classes
        for oc_def in schema_info.get("object_classes", []):
            yield {
                "type": "objectClass",
                "name": self._extract_schema_name(oc_def),
                "definition": oc_def,
                "extracted_at": extracted_at,
            }

        # Process attribute types
        for attr_def in schema_info.get("attribute_types", []):
            yield {
                "type": "attributeType",
                "name": self._extract_schema_name(attr_def),
                "definition": attr_def,
                "extracted_at": extracted_at,
            }

    def _extract_schema_name(self, definition: str) -> str:
        """Extract name from schema definition.

        Args:
        ----
            definition: Schema definition string

        Returns:
        -------
            Schema name

        """
        import re

        match = re.search(r"NAME\s+'([^']+)'", definition)
        return match.group(1) if match else "unknown"


class CustomStream(LDAPStream):
    """Dynamic stream for custom LDAP queries."""

    def __init__(
        self,
        tap: TapLDAP,
        name: str,
        search_filter: str,
        schema_properties: dict[str, Any],
        primary_keys: list[str] | None = None,
        replication_key: str | None = None,
    ) -> None:
        """Initialize custom stream.

        Args:
        ----
            tap: Parent tap instance
            name: Stream name
            search_filter: LDAP search filter
            schema_properties: Schema properties dict
            primary_keys: List of primary key fields
            replication_key: Replication key field

        """
        self.custom_filter = search_filter
        self._schema_properties = schema_properties
        self.primary_keys = primary_keys or ["dn"]
        self.replication_key = replication_key
        super().__init__(tap, name=name)

    @property
    def schema(self) -> dict[str, Any]:
        """Get stream schema."""
        return {"properties": self._schema_properties}

    @property
    def name(self) -> str:
        """Get stream name."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """Set stream name."""
        self._name = value

    def get_search_filter(self) -> str:
        """Get custom search filter."""
        return self.custom_filter
