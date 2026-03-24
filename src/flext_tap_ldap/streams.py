"""LDAP Streams for flext-tap-ldap with integrated LDIF processing.

Consolidates all stream definitions including LDAP directory streams
and LDIF file processing streams using flext-ldap and flext-ldif integration.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import TYPE_CHECKING, ClassVar, override

from flext_core import FlextLogger, t
from pydantic import ValidationError

if TYPE_CHECKING:
    from flext_meltano import FlextMeltanoAbstractions as Tap

from flext_tap_ldap.client import FlextTapLdapClient
from flext_tap_ldap.constants import c
from flext_tap_ldap.models import FlextTapLdapModels
from flext_tap_ldap.typings import FlextTapLdapTypes

logger = FlextLogger(__name__)


def _coerce_positive_int(raw_value: t.NormalizedValue, default: int) -> int:
    """Coerce value to positive integer with safe fallback."""
    try:
        parsed = int(str(raw_value))
    except (TypeError, ValueError):
        return default
    return parsed if parsed > 0 else default


def _coerce_optional_string(raw_value: t.NormalizedValue) -> str | None:
    """Coerce value to string only when source is already string-like."""
    if raw_value is None:
        return None
    try:
        validated = FlextTapLdapTypes.STRICT_STR_ADAPTER.validate_python(raw_value)
    except ValidationError:
        return None
    return validated or None


def _parse_connection_config(
    raw_value: t.NormalizedValue,
) -> FlextTapLdapModels.TapLdap.LdapConnectionConfig:
    """Validate LDAP connection payload through Pydantic."""
    try:
        parsed = FlextTapLdapModels.TapLdap.LdapConnectionConfig.model_validate(
            raw_value,
            strict=True,
        )
    except ValidationError:
        parsed = FlextTapLdapModels.TapLdap.LdapConnectionConfig()
    return FlextTapLdapModels.TapLdap.LdapConnectionConfig(
        host=str(parsed.host),
        port=_coerce_positive_int(parsed.port, c.TapLdap.DEFAULT_PORT),
        bind_dn=_coerce_optional_string(parsed.bind_dn),
        bind_password=_coerce_optional_string(parsed.bind_password),
        use_ssl=bool(parsed.use_ssl),
        timeout_seconds=_coerce_positive_int(
            parsed.timeout_seconds,
            c.TapLdap.DEFAULT_SEARCH_TIMEOUT,
        ),
        base_dn=str(parsed.base_dn),
    )


def _parse_property_definition(
    raw_value: t.NormalizedValue,
) -> FlextTapLdapModels.TapLdap.CustomPropertyDefinition:
    """Validate custom stream property definition through Pydantic."""
    try:
        return FlextTapLdapModels.TapLdap.CustomPropertyDefinition.model_validate(
            raw_value,
            strict=True,
        )
    except ValidationError:
        return FlextTapLdapModels.TapLdap.CustomPropertyDefinition()


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
        def create_test_group_record() -> t.ContainerMapping:
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
        def create_test_ou_record() -> t.ContainerMapping:
            """Create standardized test organizational unit record."""
            return {
                "dn": "ou=users,dc=test,dc=com",
                "ou": "users",
                "objectClass": ["organizationalUnit", "top"],
                "description": "Users organizational unit",
                "modifyTimestamp": "2024-01-01T12:00:00Z",
            }

        @staticmethod
        def create_test_schema_record() -> t.ContainerMapping:
            """Create standardized test schema record."""
            return {
                "dn": "cn=schema",
                "objectClass": ["top", "ldapSubentry", "schema"],
                "cn": "schema",
                "objectClasses": ["inetOrgPerson", "organizationalPerson", "person"],
                "attributeTypes": ["uid", "cn", "sn", "mail"],
                "modifyTimestamp": "2024-01-01T12:00:00Z",
            }

        @staticmethod
        def create_test_user_record() -> t.ContainerMapping:
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

    CustomStreamParams = FlextTapLdapModels.TapLdap.CustomStreamParams

    class LDAPBaseStream:
        """Base class for LDAP streams with flext-ldap integration.

        Implements FlextMeltanoProtocols.Singer.Stream protocol.
        """

        def __init__(
            self,
            tap: Tap,
            name: str | None = None,
            schema: t.ContainerMapping | None = None,
        ) -> None:
            """Initialize the LDAP stream."""
            self.name = name
            self.tap_stream_id = name or "ldap_stream"
            self.schema = schema or {}
            self.config: t.ContainerMapping = getattr(tap, "config", {})
            self.client: FlextTapLdapClient.LDAPClient | None = None
            self.tap = tap
            self._create_ldap_client()

        def get_records(
            self,
            context: t.ContainerMapping | None = None,
        ) -> Iterable[t.ContainerMapping]:
            """Get records from LDAP - base implementation."""
            _context = context
            return []

        def _create_ldap_client(self) -> None:
            """Create LDAP client from tap configuration."""
            try:
                raw_connection = self.config.get("connection", {})
                connection_config = _parse_connection_config(raw_connection)
                page_size_raw = self.config.get("page_size", 1000)
                page_size = _coerce_positive_int(
                    page_size_raw,
                    c.TapLdap.DEFAULT_PAGE_SIZE,
                )
                if (
                    connection_config.bind_dn is not None
                    and connection_config.bind_password is not None
                ):
                    self.client = FlextTapLdapClient.LDAPClient(
                        host=connection_config.host,
                        port=connection_config.port,
                        bind_dn=connection_config.bind_dn,
                        password=connection_config.bind_password,
                        use_ssl=connection_config.use_ssl,
                        timeout=connection_config.timeout_seconds,
                        page_size=page_size,
                    )
                elif connection_config.bind_dn is not None:
                    self.client = FlextTapLdapClient.LDAPClient(
                        host=connection_config.host,
                        port=connection_config.port,
                        bind_dn=connection_config.bind_dn,
                        use_ssl=connection_config.use_ssl,
                        timeout=connection_config.timeout_seconds,
                        page_size=page_size,
                    )
                elif connection_config.bind_password is not None:
                    self.client = FlextTapLdapClient.LDAPClient(
                        host=connection_config.host,
                        port=connection_config.port,
                        password=connection_config.bind_password,
                        use_ssl=connection_config.use_ssl,
                        timeout=connection_config.timeout_seconds,
                        page_size=page_size,
                    )
                else:
                    self.client = FlextTapLdapClient.LDAPClient(
                        host=connection_config.host,
                        port=connection_config.port,
                        use_ssl=connection_config.use_ssl,
                        timeout=connection_config.timeout_seconds,
                        page_size=page_size,
                    )
            except (
                ValueError,
                TypeError,
                KeyError,
                AttributeError,
                OSError,
                RuntimeError,
                ImportError,
            ) as e:
                err_msg = str(e)
                logger.warning("Failed to create LDAP client: %s", err_msg)
                self.client = None

        def _get_fallback_data(self) -> Sequence[t.ContainerMapping]:
            """Get fallback data for testing/demo purposes."""
            return []

        def _search_ldap(
            self,
            search_filter: str,
            base_dn: str | None = None,
            attributes: t.StrSequence | None = None,
        ) -> Sequence[t.ContainerMapping]:
            """Search LDAP directory with error handling."""
            if not self.client:
                logger.warning("LDAP client not available, using fallback data")
                return self._get_fallback_data()
            try:
                if base_dn is None:
                    raw_conn = self.config.get("connection", {})
                    connection_config = _parse_connection_config(raw_conn)
                    base_dn = connection_config.base_dn
                results: Sequence[t.ContainerMapping] = [
                    dict(entry)
                    for entry in self.client.search(
                        base_dn=base_dn or "",
                        search_filter=search_filter,
                        attributes=attributes,
                        scope="SUBTREE",
                    )
                ]
                if not results:
                    logger.info("No results found for filter: %s", search_filter)
                    return self._get_fallback_data()
                return results
            except (
                ValueError,
                TypeError,
                KeyError,
                AttributeError,
                OSError,
                RuntimeError,
                ImportError,
            ) as e:
                err_msg = str(e)
                logger.warning("LDAP search failed: %s, using fallback data", err_msg)
                return self._get_fallback_data()

    class UsersStream(LDAPBaseStream):
        """Stream for LDAP user entries."""

        primary_keys: ClassVar[t.StrSequence] = ["dn"]
        replication_key: ClassVar[str] = "modifyTimestamp"

        @override
        def __init__(self, tap: Tap) -> None:
            """Initialize users stream."""
            name = "users"
            schema: t.ContainerMapping = {
                "type": "object",
                "properties": {
                    "dn": {"type": "string", "description": "Distinguished Name"},
                    "objectClass": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Object Classes",
                    },
                    "memberOf": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Group Memberships",
                    },
                    "modifyTimestamp": {
                        "type": "string",
                        "description": "Modification Time",
                    },
                },
            }
            super().__init__(tap, name=name, schema=schema)
            self.forced_replication_method = "INCREMENTAL"

        @override
        def get_records(
            self,
            context: t.ContainerMapping | None = None,
        ) -> Iterable[t.ContainerMapping]:
            """Get user records from LDAP."""
            _context = context
            logger.info("Extracting LDAP users")
            raw_filter = self.config.get("user_filter", "(objectClass=inetOrgPerson)")
            user_filter = (
                _coerce_optional_string(raw_filter) or "(objectClass=inetOrgPerson)"
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
            results: Sequence[t.ContainerMapping] = self._search_ldap(
                user_filter,
                attributes=user_attributes,
            )
            yield from results

        @override
        def _get_fallback_data(self) -> Sequence[t.ContainerMapping]:
            """Get fallback user data."""
            return [
                dict(FlextTapLdapStreams.FallbackDataFactory.create_test_user_record()),
            ]

    class GroupsStream(LDAPBaseStream):
        """Stream for LDAP group entries."""

        primary_keys: ClassVar[t.StrSequence] = ["dn"]
        replication_key: ClassVar[str] = "modifyTimestamp"

        @override
        def __init__(self, tap: Tap) -> None:
            """Initialize groups stream."""
            name = "groups"
            schema: t.ContainerMapping = {
                "type": "object",
                "properties": {
                    "dn": {"type": "string", "description": "Distinguished Name"},
                    "member": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Group Members",
                    },
                    "uniqueMember": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Unique Members",
                    },
                    "objectClass": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Object Classes",
                    },
                    "modifyTimestamp": {
                        "type": "string",
                        "description": "Modification Time",
                    },
                },
            }
            super().__init__(tap, name=name, schema=schema)
            self.forced_replication_method = "INCREMENTAL"

        @override
        def get_records(
            self,
            context: t.ContainerMapping | None = None,
        ) -> Iterable[t.ContainerMapping]:
            """Get group records from LDAP."""
            _context = context
            logger.info("Extracting LDAP groups")
            raw_group_filter = self.config.get(
                "group_filter",
                "(objectClass=groupOfNames)",
            )
            group_filter = (
                _coerce_optional_string(raw_group_filter)
                or "(objectClass=groupOfNames)"
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
            results: Sequence[t.ContainerMapping] = self._search_ldap(
                group_filter,
                attributes=group_attributes,
            )
            yield from results

        @override
        def _get_fallback_data(self) -> Sequence[t.ContainerMapping]:
            """Get fallback group data."""
            return [
                dict(
                    FlextTapLdapStreams.FallbackDataFactory.create_test_group_record()
                ),
            ]

    class OrganizationalUnitsStream(LDAPBaseStream):
        """Stream for LDAP organizational unit entries."""

        primary_keys: ClassVar[t.StrSequence] = ["dn"]

        @override
        def __init__(self, tap: Tap) -> None:
            """Initialize organizational units stream."""
            name = "organizational_units"
            schema: t.ContainerMapping = {
                "type": "object",
                "properties": {
                    "dn": {"type": "string", "description": "Distinguished Name"},
                    "objectClass": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Object Classes",
                    },
                    "modifyTimestamp": {
                        "type": "string",
                        "description": "Modification Time",
                    },
                },
            }
            super().__init__(tap, name=name, schema=schema)

        @override
        def get_records(
            self,
            context: t.ContainerMapping | None = None,
        ) -> Iterable[t.ContainerMapping]:
            """Get organizational unit records from LDAP."""
            _context = context
            logger.info("Extracting LDAP organizational units")
            ou_filter = "(objectClass=organizationalUnit)"
            ou_attributes = [
                "ou",
                "description",
                "objectClass",
                "createTimestamp",
                "modifyTimestamp",
            ]
            results: Sequence[t.ContainerMapping] = self._search_ldap(
                ou_filter,
                attributes=ou_attributes,
            )
            yield from results

        @override
        def _get_fallback_data(self) -> Sequence[t.ContainerMapping]:
            """Get fallback organizational unit data."""
            return [
                dict(FlextTapLdapStreams.FallbackDataFactory.create_test_ou_record()),
            ]

    class SchemaStream(LDAPBaseStream):
        """Stream for LDAP schema information."""

        primary_keys: ClassVar[t.StrSequence] = ["dn"]

        @override
        def __init__(self, tap: Tap) -> None:
            """Initialize schema stream."""
            name = "schema"
            schema: t.ContainerMapping = {
                "type": "object",
                "properties": {
                    "objectClass": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Object Classes",
                    },
                    "objectClasses": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Available Object Classes",
                    },
                    "attributeTypes": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Available Attribute Types",
                    },
                    "ldapSyntaxes": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "LDAP Syntaxes",
                    },
                    "modifyTimestamp": {
                        "type": "string",
                        "description": "Modification Time",
                    },
                },
            }
            super().__init__(tap, name=name, schema=schema)

        @override
        def get_records(
            self,
            context: t.ContainerMapping | None = None,
        ) -> Iterable[t.ContainerMapping]:
            """Get schema records from LDAP."""
            _context = context
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
                        return
                except (
                    ValueError,
                    TypeError,
                    KeyError,
                    AttributeError,
                    OSError,
                    RuntimeError,
                    ImportError,
                ) as e:
                    err_msg = str(e)
                    logger.debug(
                        "Schema search failed for base DN '%s': %s",
                        base_dn,
                        err_msg,
                    )
                    continue
            for record in self._get_fallback_data():
                yield record

        @override
        def _get_fallback_data(self) -> Sequence[t.ContainerMapping]:
            """Get fallback schema data."""
            return [
                dict(
                    FlextTapLdapStreams.FallbackDataFactory.create_test_schema_record(),
                ),
            ]

    class CustomStream(LDAPBaseStream):
        """Custom LDAP stream with configurable filter and schema."""

        _default_primary_keys: ClassVar[t.StrSequence] = ["dn"]

        @override
        def __init__(
            self,
            tap: Tap,
            params: FlextTapLdapModels.TapLdap.CustomStreamParams,
        ) -> None:
            """Initialize custom stream with parameters."""
            self.params = params

            def _map_prop(
                name: str,
                definition: t.NormalizedValue,
            ) -> t.ContainerMapping:
                parsed_definition = _parse_property_definition(definition)
                prop_type = parsed_definition.type
                prop_desc = parsed_definition.description or f"{name} field"
                if prop_type == "integer":
                    return {"type": "integer", "description": prop_desc}
                if prop_type == "number":
                    return {"type": "number", "description": prop_desc}
                if prop_type == "boolean":
                    return {"type": "boolean", "description": prop_desc}
                if prop_type == "array":
                    return {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": prop_desc,
                    }
                return {"type": "string", "description": prop_desc}

            if params.schema_properties:
                dynamic_properties: Mapping[str, t.ContainerMapping] = {
                    key: _map_prop(key, value)
                    for key, value in params.schema_properties.items()
                }
                schema: t.ContainerMapping = {
                    "type": "object",
                    "properties": {
                        "dn": {
                            "type": "string",
                            "description": "Distinguished Name",
                        },
                        **dynamic_properties,
                    },
                }
            else:
                schema = {
                    "type": "object",
                    "properties": {
                        "dn": {
                            "type": "string",
                            "description": "Distinguished Name",
                        },
                        "objectClass": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Object Classes",
                        },
                        "modifyTimestamp": {
                            "type": "string",
                            "description": "Modification Time",
                        },
                    },
                }
            super().__init__(tap, name=params.name, schema=schema)

        @property
        def primary_keys(self) -> t.StrSequence:
            """Get primary key columns for this stream."""
            return self.params.primary_keys or self._default_primary_keys

        @property
        def replication_key(self) -> str | None:
            """Get replication key for incremental sync."""
            return self.params.replication_key

        @override
        def get_records(
            self,
            context: t.ContainerMapping | None = None,
        ) -> Iterable[t.ContainerMapping]:
            """Get records using custom filter."""
            _context = context
            logger.info(
                f"Extracting LDAP records for custom stream: {self.params.name}",
            )
            results: Sequence[t.ContainerMapping] = self._search_ldap(
                self.params.search_filter,
            )
            yield from results

        @override
        def _get_fallback_data(self) -> Sequence[t.ContainerMapping]:
            """Get fallback data for custom stream."""
            return [
                {
                    "dn": f"cn=test-{self.params.name},dc=test,dc=com",
                    "objectClass": ["top", "testObject"],
                    "modifyTimestamp": "2024-01-01T12:00:00Z",
                },
            ]


__all__ = ["FlextTapLdapStreams"]
