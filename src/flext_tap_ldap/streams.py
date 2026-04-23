"""LDAP Streams for flext-tap-ldap with integrated LDIF processing.

Consolidates all stream definitions including LDAP directory streams
and LDIF file processing streams using flext-ldap and flext-ldif integration.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import (
    Iterable,
    Mapping,
    Sequence,
)
from typing import TYPE_CHECKING, ClassVar, override

from flext_tap_ldap import FlextTapLdapClient, c, m, t, u

if TYPE_CHECKING:
    from flext_meltano import FlextMeltanoAbstractions as Tap

logger = u.fetch_logger(__name__)


class FlextTapLdapStreams:
    """Unified streams class for LDAP tap operations with complete stream management.

    This class consolidates all LDAP and LDIF stream implementations following
    the unified class pattern with Clean Architecture and Domain-Driven Design.

    Contains all stream classes as nested classes to maintain single responsibility
    while providing complete LDAP/LDIF data extraction capabilities.
    """

    class LDAPBaseStream:
        """Base class for LDAP streams with flext-ldap integration.

        Implements the inherited Singer stream protocol.
        """

        @staticmethod
        def coerce_positive_int(raw_value: t.JsonValue, default: int) -> int:
            """Coerce value to positive integer with safe fallback."""
            try:
                parsed = t.INTEGER_ADAPTER.validate_python(raw_value)
            except c.ValidationError:
                return default
            return parsed if parsed > 0 else default

        @staticmethod
        def coerce_optional_string(raw_value: t.JsonValue) -> str | None:
            """Coerce value to string only when source is already string-like."""
            if raw_value is None:
                return None
            try:
                validated = t.STRICT_STR_ADAPTER.validate_python(
                    raw_value,
                )
            except c.ValidationError:
                return None
            return validated or None

        @staticmethod
        def parse_connection_config(
            raw_value: t.JsonValue,
        ) -> m.TapLdap.LdapConnectionConfig:
            """Validate LDAP connection payload through Pydantic."""
            try:
                parsed = m.TapLdap.LdapConnectionConfig.model_validate(
                    raw_value,
                    strict=True,
                )
            except c.ValidationError as exc:
                msg = f"Invalid LDAP connection configuration: {exc}"
                raise ValueError(msg) from exc
            return m.TapLdap.LdapConnectionConfig(
                host=str(parsed.host),
                port=FlextTapLdapStreams.LDAPBaseStream.coerce_positive_int(
                    parsed.port,
                    c.Ldap.ConnectionDefaults.PORT,
                ),
                bind_dn=FlextTapLdapStreams.LDAPBaseStream.coerce_optional_string(
                    parsed.bind_dn,
                ),
                bind_password=FlextTapLdapStreams.LDAPBaseStream.coerce_optional_string(
                    parsed.bind_password,
                ),
                use_ssl=bool(parsed.use_ssl),
                timeout_seconds=FlextTapLdapStreams.LDAPBaseStream.coerce_positive_int(
                    parsed.timeout_seconds,
                    c.TapLdap.DEFAULT_SEARCH_TIMEOUT,
                ),
                base_dn=str(parsed.base_dn),
            )

        @staticmethod
        def parse_property_definition(
            raw_value: t.JsonValue,
        ) -> m.TapLdap.CustomPropertyDefinition:
            """Validate custom stream property definition through Pydantic."""
            try:
                return m.TapLdap.CustomPropertyDefinition.model_validate(
                    raw_value,
                    strict=True,
                )
            except c.ValidationError:
                return m.TapLdap.CustomPropertyDefinition()

        def __init__(
            self,
            tap: Tap,
            name: str | None = None,
            schema: t.JsonMapping | None = None,
        ) -> None:
            """Initialize the LDAP stream."""
            self.name = name
            self.tap_stream_id = name or "ldap_stream"
            self.schema = schema or {}
            self.settings: t.JsonMapping = getattr(tap, "tap_config", {})
            self.client: FlextTapLdapClient.LDAPClient | None = None
            self.tap = tap
            self._create_ldap_client()

        def get_records(
            self,
            context: t.JsonMapping | None = None,
        ) -> Iterable[t.JsonMapping]:
            """Get records from LDAP - base implementation."""
            _context = context
            return []

        def _create_ldap_client(self) -> None:
            """Create LDAP client from tap configuration."""
            try:
                raw_connection = self.settings.get("connection", {})
                connection_config = (
                    FlextTapLdapStreams.LDAPBaseStream.parse_connection_config(
                        raw_connection,
                    )
                )
                if not connection_config.host:
                    msg = "LDAP connection host is required"
                    raise ValueError(msg)
                page_size_raw = self.settings.get("page_size", 1000)
                page_size = FlextTapLdapStreams.LDAPBaseStream.coerce_positive_int(
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
            except c.Meltano.SINGER_SAFE_EXCEPTIONS as e:
                err_msg = str(e)
                logger.warning("Failed to create LDAP client: %s", err_msg)
                self.client = None

        def _search_ldap(
            self,
            search_filter: str,
            base_dn: str | None = None,
            attributes: t.StrSequence | None = None,
        ) -> Sequence[t.JsonMapping]:
            """Search LDAP directory with error handling."""
            if not self.client:
                msg = "LDAP client is not available"
                raise RuntimeError(msg)
            try:
                if base_dn is None:
                    raw_conn = self.settings.get("connection", {})
                    connection_config = (
                        FlextTapLdapStreams.LDAPBaseStream.parse_connection_config(
                            raw_conn,
                        )
                    )
                    base_dn = connection_config.base_dn
                results: Sequence[t.JsonMapping] = [
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
                    return []
                return results
            except c.Meltano.SINGER_SAFE_EXCEPTIONS as e:
                msg = f"LDAP search failed: {e}"
                raise RuntimeError(msg) from e

    class UsersStream(LDAPBaseStream):
        """Stream for LDAP user entries."""

        primary_keys: ClassVar[t.StrSequence] = ["dn"]
        replication_key: ClassVar[str] = "modifyTimestamp"

        @override
        def __init__(self, tap: Tap) -> None:
            """Initialize users stream."""
            name = "users"
            schema = {
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
            super().__init__(
                tap,
                name=name,
                schema=t.Cli.JSON_MAPPING_ADAPTER.validate_python(schema),
            )
            self.forced_replication_method = "INCREMENTAL"

        @override
        def get_records(
            self,
            context: t.JsonMapping | None = None,
        ) -> Iterable[t.JsonMapping]:
            """Get user records from LDAP."""
            _context = context
            logger.info("Extracting LDAP users")
            raw_filter = self.settings.get("user_filter", "(objectClass=inetOrgPerson)")
            user_filter = (
                FlextTapLdapStreams.LDAPBaseStream.coerce_optional_string(raw_filter)
                or "(objectClass=inetOrgPerson)"
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
            results: Sequence[t.JsonMapping] = self._search_ldap(
                user_filter,
                attributes=user_attributes,
            )
            yield from results

    class GroupsStream(LDAPBaseStream):
        """Stream for LDAP group entries."""

        primary_keys: ClassVar[t.StrSequence] = ["dn"]
        replication_key: ClassVar[str] = "modifyTimestamp"

        @override
        def __init__(self, tap: Tap) -> None:
            """Initialize groups stream."""
            name = "groups"
            schema = {
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
            super().__init__(
                tap,
                name=name,
                schema=t.Cli.JSON_MAPPING_ADAPTER.validate_python(schema),
            )
            self.forced_replication_method = "INCREMENTAL"

        @override
        def get_records(
            self,
            context: t.JsonMapping | None = None,
        ) -> Iterable[t.JsonMapping]:
            """Get group records from LDAP."""
            _context = context
            logger.info("Extracting LDAP groups")
            raw_group_filter = self.settings.get(
                "group_filter",
                "(objectClass=groupOfNames)",
            )
            group_filter = (
                FlextTapLdapStreams.LDAPBaseStream.coerce_optional_string(
                    raw_group_filter,
                )
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
            results: Sequence[t.JsonMapping] = self._search_ldap(
                group_filter,
                attributes=group_attributes,
            )
            yield from results

    class OrganizationalUnitsStream(LDAPBaseStream):
        """Stream for LDAP organizational unit entries."""

        primary_keys: ClassVar[t.StrSequence] = ["dn"]

        @override
        def __init__(self, tap: Tap) -> None:
            """Initialize organizational units stream."""
            name = "organizational_units"
            schema = {
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
            super().__init__(
                tap,
                name=name,
                schema=t.Cli.JSON_MAPPING_ADAPTER.validate_python(schema),
            )

        @override
        def get_records(
            self,
            context: t.JsonMapping | None = None,
        ) -> Iterable[t.JsonMapping]:
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
            results: Sequence[t.JsonMapping] = self._search_ldap(
                ou_filter,
                attributes=ou_attributes,
            )
            yield from results

    class SchemaStream(LDAPBaseStream):
        """Stream for LDAP schema information."""

        primary_keys: ClassVar[t.StrSequence] = ["dn"]

        @override
        def __init__(self, tap: Tap) -> None:
            """Initialize schema stream."""
            name = "schema"
            schema = {
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
            super().__init__(
                tap,
                name=name,
                schema=t.Cli.JSON_MAPPING_ADAPTER.validate_python(schema),
            )

        @override
        def get_records(
            self,
            context: t.JsonMapping | None = None,
        ) -> Iterable[t.JsonMapping]:
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
            last_error: str | None = None
            for base_dn in base_dns:
                try:
                    results = self._search_ldap(
                        schema_filter,
                        base_dn=base_dn,
                        attributes=schema_attributes,
                    )
                    if results:
                        yield from results
                        return
                except c.Meltano.SINGER_SAFE_EXCEPTIONS as e:
                    err_msg = str(e)
                    last_error = err_msg
                    logger.debug(
                        "Schema search failed for base DN '%s': %s",
                        base_dn,
                        err_msg,
                    )
                    continue
            if last_error is not None:
                msg = f"LDAP schema search failed: {last_error}"
                raise RuntimeError(msg)
            logger.info("No LDAP schema records found")

    class CustomStream(LDAPBaseStream):
        """Custom LDAP stream with configurable filter and schema."""

        _default_primary_keys: ClassVar[t.StrSequence] = ["dn"]

        @override
        def __init__(
            self,
            tap: Tap,
            params: m.TapLdap.CustomStreamParams,
        ) -> None:
            """Initialize custom stream with parameters."""
            self.params = params

            def _map_prop(
                name: str,
                definition: t.JsonValue,
            ) -> t.JsonMapping:
                parsed_definition = (
                    FlextTapLdapStreams.LDAPBaseStream.parse_property_definition(
                        definition,
                    )
                )
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
                dynamic_properties: Mapping[str, t.JsonMapping] = {
                    key: _map_prop(key, value)
                    for key, value in params.schema_properties.items()
                }
                schema = {
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
            super().__init__(
                tap,
                name=params.name,
                schema=t.Cli.JSON_MAPPING_ADAPTER.validate_python(schema),
            )

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
            context: t.JsonMapping | None = None,
        ) -> Iterable[t.JsonMapping]:
            """Get records using custom filter."""
            _context = context
            logger.info(
                f"Extracting LDAP records for custom stream: {self.params.name}",
            )
            results: Sequence[t.JsonMapping] = self._search_ldap(
                self.params.search_filter,
            )
            yield from results


__all__: list[str] = ["FlextTapLdapStreams"]
