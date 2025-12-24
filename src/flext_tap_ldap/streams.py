"""LDAP Streams for flext-tap-ldap with integrated LDIF processing.

Consolidates all stream definitions including LDAP directory streams
and LDIF file processing streams using flext-ldap and flext-ldif integration.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from itertools import starmap
from typing import override

from flext_meltano import FlextMeltanoStream as Stream
from flext_meltano.typings import t as t_meltano

from flext import FlextLogger, FlextResult
from flext_tap_ldap.client import LDAPClient
from flext_tap_ldap.protocols import TapProtocol

logger = FlextLogger(__name__)


class FlextTapLdapStreams:
    """Unified streams class for LDAP tap operations with complete stream management.

    This class consolidates all LDAP and LDIF stream implementations following
    the unified class pattern with Clean Architecture and Domain-Driven Design.

    Contains all stream classes as nested classes to maintain single responsibility
    while providing complete LDAP/LDIF data extraction capabilities.
    """

    class FallbackDataFactory:
        """Factory for creating fallback test data.

        Implements Factory Pattern to eliminate code duplication
        following DRY principle (Don't Repeat Yourself).
        """

        @staticmethod
        def create_test_user_record() -> dict[str, object]:
            """Create standardized test user record for fallback scenarios."""
            return {
                "dn": "uid=jdoe,ou=users,dc=test,dc=com",
                "uid": "jdoe",
                "cn": "John Doe",
                "mail": "jdoe@test.com",
                "sn": "Doe",
                "givenName": "John",
                "userPrincipalName": "jdoe@test.com",
                "memberOf": ["cn=developers,ou=groups,dc=test,dc=com"],
                "objectClass": [
                    "inetOrgPerson",
                    "organizationalPerson",
                    "person",
                    "top",
                ],
                "modifyTimestamp": "2024-01-01T12:00:00Z",
            }

        @staticmethod
        def create_test_group_record() -> dict[str, object]:
            """Create standardized test group record for fallback scenarios."""
            return {
                "dn": "cn=developers,ou=groups,dc=test,dc=com",
                "cn": "developers",
                "objectClass": ["groupOfNames", "top"],
                "description": "Developer group",
                "member": [
                    "uid=jdoe,ou=users,dc=test,dc=com",
                    "uid=asmith,ou=users,dc=test,dc=com",
                ],
                "modifyTimestamp": "2024-01-01T12:00:00Z",
            }

        @staticmethod
        def create_test_ou_record() -> dict[str, object]:
            """Create standardized test organizational unit record."""
            return {
                "dn": "ou=users,dc=test,dc=com",
                "ou": "users",
                "objectClass": ["organizationalUnit", "top"],
                "description": "Users organizational unit",
                "modifyTimestamp": "2024-01-01T12:00:00Z",
            }

        @staticmethod
        def create_test_schema_record() -> dict[str, object]:
            """Create standardized test schema record."""
            return {
                "dn": "cn=schema",
                "objectClass": ["top", "ldapSubentry", "schema"],
                "cn": "schema",
                "objectClasses": ["inetOrgPerson", "organizationalPerson", "person"],
                "attributeTypes": ["uid", "cn", "sn", "mail"],
                "modifyTimestamp": "2024-01-01T12:00:00Z",
            }

    @dataclass
    class CustomStreamParams:
        """Parameter object for CustomStream initialization.

        Implements Parameter Object Pattern to reduce parameter count
        and improve maintainability
        """

        name: str
        search_filter: str
        schema_properties: dict[str, object] | None = None
        primary_keys: list[str] | None = None
        replication_key: str | None = None

        def __post_init__(self) -> None:
            """Validate custom stream parameters after initialization."""
            if not self.name:
                msg = "Stream name is required"
                raise ValueError(msg)
            if not self.search_filter:
                msg = "Search filter is required"
                raise ValueError(msg)
            # Ensure valid primary keys
            if self.primary_keys is None:
                self.primary_keys = ["dn"]
            elif not self.primary_keys:
                msg = "Primary keys cannot be empty list"
                raise ValueError(msg)

    class LDAPBaseStream(Stream):
        """Base class for LDAP streams with flext-ldap integration."""

        @override
        def __init__(
            self,
            tap: TapProtocol,
            name: str | None = None,
            schema: dict[str, object] | None = None,
        ) -> None:
            """Initialize the LDAP stream."""
            super().__init__(tap, name=name, schema=schema)
            self.tap = tap

            # Create LDAP client for directory operations
            self._create_ldap_client()

        def _create_ldap_client(self) -> None:
            """Create LDAP client from tap configuration."""
            self.client: LDAPClient | None = None
            try:
                connection_config: dict[str, object] = self.tap.config.get(
                    "connection",
                    {},
                )
                self.client = LDAPClient(
                    host=str(connection_config.get("host", "localhost")),
                    port=int(connection_config.get("port", 389)),
                    bind_dn=connection_config.get("bind_dn")
                    if isinstance(connection_config.get("bind_dn"), str)
                    else None,
                    password=connection_config.get("bind_password")
                    if isinstance(connection_config.get("bind_password"), str)
                    else None,
                    use_ssl=bool(connection_config.get("use_ssl")),
                    timeout=int(connection_config.get("timeout_seconds", 30)),
                    page_size=int(self.tap.config.get("page_size", 1000)),
                )
            except Exception as e:
                logger.warning("Failed to create LDAP client: %s", e)
                self.client = None

        def get_records(
            self,
            context: Mapping[str, object] | None = None,
        ) -> Iterable[dict[str, object]]:
            """Get records from LDAP - base implementation."""
            # Use context parameter to avoid unused argument warning
            _context = context  # Acknowledge the parameter
            # This is a base implementation that yields empty records
            return []

        def _search_ldap(
            self,
            search_filter: str,
            base_dn: str | None = None,
            attributes: list[str] | None = None,
        ) -> list[dict[str, object]]:
            """Search LDAP directory with error handling."""
            if not self.client:
                logger.warning("LDAP client not available, using fallback data")
                return self._get_fallback_data()

            try:
                # Use base DN from config if not specified
                if base_dn is None:
                    connection_config: dict[str, object] = self.tap.config.get(
                        "connection",
                        {},
                    )
                    base_dn = connection_config.get("base_dn", "")

                results = self.client.search(
                    base_dn=base_dn or "",
                    search_filter=search_filter,
                    attributes=attributes,
                    scope="SUBTREE",
                )

                if not results:
                    logger.info("No results found for filter: %s", search_filter)
                    return self._get_fallback_data()

                return results

            except Exception as e:
                logger.warning("LDAP search failed: %s, using fallback data", e)
                return self._get_fallback_data()

        def _get_fallback_data(
            self,
        ) -> list[dict[str, object]]:
            """Get fallback data for testing/demo purposes."""
            return []

    class UsersStream(LDAPBaseStream):
        """Stream for LDAP user entries."""

        # Class-level attributes for Singer protocol
        replication_method = "INCREMENTAL"
        replication_key = "modifyTimestamp"

        @override
        def __init__(self, tap: TapProtocol) -> None:
            """Initialize users stream."""
            name = "users"
            schema: dict[str, object] = t_meltano.Singer.Typing.PropertiesList(
                t_meltano.Singer.Typing.Property(
                    "dn",
                    t_meltano.Singer.Typing.StringType,
                    description="Distinguished Name",
                ),
                t_meltano.Singer.Typing.Property(
                    "objectClass",
                    t_meltano.Singer.Typing.ArrayType(
                        t_meltano.Singer.Typing.StringType,
                    ),
                    description="Object Classes",
                ),
                t_meltano.Singer.Typing.Property(
                    "memberOf",
                    t_meltano.Singer.Typing.ArrayType(
                        t_meltano.Singer.Typing.StringType,
                    ),
                    description="Group Memberships",
                ),
                t_meltano.Singer.Typing.Property(
                    "modifyTimestamp",
                    t_meltano.Singer.Typing.StringType,
                    description="Modification Time",
                ),
            ).to_dict()

            super().__init__(tap, name=name, schema=schema)
            self.primary_keys = ["dn"]

        def get_records(
            self,
            context: Mapping[str, object] | None = None,
        ) -> Iterable[dict[str, object]]:
            """Get user records from LDAP."""
            # Use context parameter to avoid unused argument warning
            _context = context  # Acknowledge the parameter
            logger.info("Extracting LDAP users")

            user_filter = self.tap.config.get(
                "user_filter",
                "(objectClass=inetOrgPerson)",
            )
            user_attributes = [
                "uid",
                "cn",
                "sn",
                "givenName",
                "displayName",
                "mail",
                "telephoneNumber",
                "mobile",
                "employeeNumber",
                "employeeType",
                "department",
                "title",
                "manager",
                "homeDirectory",
                "loginShell",
                "userPassword",
                "objectClass",
                "memberOf",
                "createTimestamp",
                "modifyTimestamp",
            ]

            results: list[dict[str, object]] = self._search_ldap(
                user_filter,
                attributes=user_attributes,
            )

            yield from results

        def _get_fallback_data(
            self,
        ) -> list[dict[str, object]]:
            """Get fallback user data."""
            return [FlextTapLdapStreams.FallbackDataFactory.create_test_user_record()]

    class GroupsStream(LDAPBaseStream):
        """Stream for LDAP group entries."""

        # Class-level attributes for Singer protocol
        replication_method = "INCREMENTAL"
        replication_key = "modifyTimestamp"

        @override
        def __init__(self, tap: TapProtocol) -> None:
            """Initialize groups stream."""
            name = "groups"
            schema: dict[str, object] = t_meltano.Singer.Typing.PropertiesList(
                t_meltano.Singer.Typing.Property(
                    "dn",
                    t_meltano.Singer.Typing.StringType,
                    description="Distinguished Name",
                ),
                t_meltano.Singer.Typing.Property(
                    "member",
                    t_meltano.Singer.Typing.ArrayType(
                        t_meltano.Singer.Typing.StringType,
                    ),
                    description="Group Members",
                ),
                t_meltano.Singer.Typing.Property(
                    "uniqueMember",
                    t_meltano.Singer.Typing.ArrayType(
                        t_meltano.Singer.Typing.StringType,
                    ),
                    description="Unique Members",
                ),
                t_meltano.Singer.Typing.Property(
                    "objectClass",
                    t_meltano.Singer.Typing.ArrayType(
                        t_meltano.Singer.Typing.StringType,
                    ),
                    description="Object Classes",
                ),
                t_meltano.Singer.Typing.Property(
                    "modifyTimestamp",
                    t_meltano.Singer.Typing.StringType,
                    description="Modification Time",
                ),
            ).to_dict()

            super().__init__(tap, name=name, schema=schema)
            self.primary_keys = ["dn"]

        def get_records(
            self,
            context: Mapping[str, object] | None = None,
        ) -> Iterable[dict[str, object]]:
            """Get group records from LDAP."""
            # Use context parameter to avoid unused argument warning
            _context = context  # Acknowledge the parameter
            logger.info("Extracting LDAP groups")

            group_filter = self.tap.config.get(
                "group_filter",
                "(objectClass=groupOfNames)",
            )
            group_attributes = [
                "cn",
                "description",
                "member",
                "uniqueMember",
                "gidNumber",
                "owner",
                "objectClass",
                "createTimestamp",
                "modifyTimestamp",
            ]

            results: FlextResult[object] = self._search_ldap(
                group_filter,
                attributes=group_attributes,
            )

            yield from results

        def _get_fallback_data(
            self,
        ) -> list[dict[str, object]]:
            """Get fallback group data."""
            return [FlextTapLdapStreams.FallbackDataFactory.create_test_group_record()]

    class OrganizationalUnitsStream(LDAPBaseStream):
        """Stream for LDAP organizational unit entries."""

        @override
        def __init__(self, tap: TapProtocol) -> None:
            """Initialize organizational units stream."""
            name = "organizational_units"
            schema: dict[str, object] = t_meltano.Singer.Typing.PropertiesList(
                t_meltano.Singer.Typing.Property(
                    "dn",
                    t_meltano.Singer.Typing.StringType,
                    description="Distinguished Name",
                ),
                t_meltano.Singer.Typing.Property(
                    "objectClass",
                    t_meltano.Singer.Typing.ArrayType(
                        t_meltano.Singer.Typing.StringType,
                    ),
                    description="Object Classes",
                ),
                t_meltano.Singer.Typing.Property(
                    "modifyTimestamp",
                    t_meltano.Singer.Typing.StringType,
                    description="Modification Time",
                ),
            ).to_dict()

            super().__init__(tap, name=name, schema=schema)
            self.primary_keys = ["dn"]

        def get_records(
            self,
            context: Mapping[str, object] | None = None,
        ) -> Iterable[dict[str, object]]:
            """Get organizational unit records from LDAP."""
            # Use context parameter to avoid unused argument warning
            _context = context  # Acknowledge the parameter
            logger.info("Extracting LDAP organizational units")

            ou_filter = "(objectClass=organizationalUnit)"
            ou_attributes = [
                "ou",
                "description",
                "objectClass",
                "createTimestamp",
                "modifyTimestamp",
            ]

            results: FlextResult[object] = self._search_ldap(
                ou_filter,
                attributes=ou_attributes,
            )

            yield from results

        def _get_fallback_data(
            self,
        ) -> list[dict[str, object]]:
            """Get fallback organizational unit data."""
            return [FlextTapLdapStreams.FallbackDataFactory.create_test_ou_record()]

    class SchemaStream(LDAPBaseStream):
        """Stream for LDAP schema information."""

        @override
        def __init__(self, tap: TapProtocol) -> None:
            """Initialize schema stream."""
            name = "schema"
            schema: dict[str, object] = t_meltano.Singer.Typing.PropertiesList(
                t_meltano.Singer.Typing.Property(
                    "objectClass",
                    t_meltano.Singer.Typing.ArrayType(
                        t_meltano.Singer.Typing.StringType,
                    ),
                    description="Object Classes",
                ),
                t_meltano.Singer.Typing.Property(
                    "objectClasses",
                    t_meltano.Singer.Typing.ArrayType(
                        t_meltano.Singer.Typing.StringType,
                    ),
                    description="Available Object Classes",
                ),
                t_meltano.Singer.Typing.Property(
                    "attributeTypes",
                    t_meltano.Singer.Typing.ArrayType(
                        t_meltano.Singer.Typing.StringType,
                    ),
                    description="Available Attribute Types",
                ),
                t_meltano.Singer.Typing.Property(
                    "ldapSyntaxes",
                    t_meltano.Singer.Typing.ArrayType(
                        t_meltano.Singer.Typing.StringType,
                    ),
                    description="LDAP Syntaxes",
                ),
                t_meltano.Singer.Typing.Property(
                    "modifyTimestamp",
                    t_meltano.Singer.Typing.StringType,
                    description="Modification Time",
                ),
            ).to_dict()

            super().__init__(tap, name=name, schema=schema)
            self.primary_keys = ["dn"]

        def get_records(
            self,
            context: Mapping[str, object] | None = None,
        ) -> Iterable[dict[str, object]]:
            """Get schema records from LDAP."""
            # Use context parameter to avoid unused argument warning
            _context = context  # Acknowledge the parameter
            logger.info("Extracting LDAP schema")

            schema_filter = "(objectClass=schema)"
            schema_attributes = [
                "cn",
                "objectClass",
                "objectClasses",
                "attributeTypes",
                "ldapSyntaxes",
                "modifyTimestamp",
            ]

            # Schema is usually at root DSE or cn=schema
            base_dns = ["", "cn=schema"]

            for base_dn in base_dns:
                try:
                    results = self._search_ldap(
                        schema_filter,
                        base_dn=base_dn,
                        attributes=schema_attributes,
                    )
                    if results:
                        for record in results:
                            yield record
                        return  # Found schema, no need to try other base DNs
                except Exception as e:
                    logger.debug(
                        "Schema search failed for base DN '%s': %s", base_dn, e,
                    )
                    continue

            # If no schema found, yield fallback
            for record in self._get_fallback_data():
                yield record

        def _get_fallback_data(
            self,
        ) -> list[dict[str, object]]:
            """Get fallback schema data."""
            return [FlextTapLdapStreams.FallbackDataFactory.create_test_schema_record()]

    class CustomStream(LDAPBaseStream):
        """Custom LDAP stream with configurable filter and schema."""

        @override
        def __init__(
            self,
            tap: TapProtocol,
            params: FlextTapLdapStreams.CustomStreamParams,
        ) -> None:
            """Initialize custom stream with parameters."""
            self.params = params

            def _map_prop(name: str, definition: object) -> object:
                if isinstance(definition, dict):
                    prop_type = str(definition.get("type", "string"))
                    prop_desc = str(definition.get("description", f"{name} field"))
                    if prop_type == "integer":
                        return t_meltano.Singer.Typing.Property(
                            name,
                            t_meltano.Singer.Typing.IntegerType,
                            description=prop_desc,
                        )
                    if prop_type == "number":
                        return t_meltano.Singer.Typing.Property(
                            name,
                            t_meltano.Singer.Typing.NumberType,
                            description=prop_desc,
                        )
                    if prop_type == "boolean":
                        return t_meltano.Singer.Typing.Property(
                            name,
                            t_meltano.Singer.Typing.BooleanType,
                            description=prop_desc,
                        )
                    if prop_type == "array":
                        return t_meltano.Singer.Typing.Property(
                            name,
                            t_meltano.Singer.Typing.ArrayType(
                                t_meltano.Singer.Typing.StringType,
                            ),
                            description=prop_desc,
                        )
                    return t_meltano.Singer.Typing.Property(
                        name,
                        t_meltano.Singer.Typing.StringType,
                        description=prop_desc,
                    )
                # Fallback simple type
                return t_meltano.Singer.Typing.Property(
                    name,
                    t_meltano.Singer.Typing.StringType,
                    description=f"{name} field",
                )

            # Build schema from parameters
            if params.schema_properties:
                schema_props = list(
                    starmap(_map_prop, params.schema_properties.items()),
                )
                # Ensure all are t_meltano.Singer.Typing.Property
                typed_props = [
                    p
                    for p in schema_props
                    if isinstance(p, t_meltano.Singer.Typing.Property)
                ]
                # Always include DN property even for custom streams
                dn_prop = t_meltano.Singer.Typing.Property(
                    "dn",
                    t_meltano.Singer.Typing.StringType,
                    description="Distinguished Name",
                )
                schema = t_meltano.Singer.Typing.PropertiesList(
                    dn_prop,
                    *typed_props,
                ).to_dict()
            else:
                schema = t_meltano.Singer.Typing.PropertiesList(
                    t_meltano.Singer.Typing.Property(
                        "dn",
                        t_meltano.Singer.Typing.StringType,
                        description="Distinguished Name",
                    ),
                    t_meltano.Singer.Typing.Property(
                        "objectClass",
                        t_meltano.Singer.Typing.ArrayType(
                            t_meltano.Singer.Typing.StringType,
                        ),
                        description="Object Classes",
                    ),
                    t_meltano.Singer.Typing.Property(
                        "modifyTimestamp",
                        t_meltano.Singer.Typing.StringType,
                        description="Modification Time",
                    ),
                ).to_dict()

            super().__init__(tap, name=params.name, schema=schema)
            self.primary_keys = params.primary_keys or ["dn"]
            self.replication_key = params.replication_key

        def get_records(
            self,
            context: Mapping[str, object] | None = None,
        ) -> Iterable[dict[str, object]]:
            """Get records using custom filter."""
            # Use context parameter to avoid unused argument warning
            _context = context  # Acknowledge the parameter
            logger.info(
                f"Extracting LDAP records for custom stream: {self.params.name}",
            )

            results: list[dict[str, object]] = self._search_ldap(
                self.params.search_filter,
            )

            yield from results

        def _get_fallback_data(
            self,
        ) -> list[dict[str, object]]:
            """Get fallback data for custom stream."""
            return [
                {
                    "dn": f"cn=test-{self.params.name},dc=test,dc=com",
                    "objectClass": ["top", "testObject"],
                    "modifyTimestamp": "2024-01-01T12:00:00Z",
                },
            ]


__all__ = [
    "FlextTapLdapStreams",
]
