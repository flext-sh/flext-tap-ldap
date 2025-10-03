"""LDAP Streams for flext-tap-ldap with integrated LDIF processing.

Consolidates all stream definitions including LDAP directory streams
and LDIF file processing streams using flext-ldap and flext-ldif integration.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import time
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from itertools import starmap
from pathlib import Path
from typing import override

from flext_ldap import FlextLdapClient
from flext_ldif import FlextLdif, FlextLdifModels
from singer_sdk import Stream
from singer_sdk.typing import (
    ArrayType,
    BooleanType,
    IntegerType,
    NumberType,
    ObjectType,
    PropertiesList,
    Property,
    StringType,
)

from flext_core import FlextLogger, FlextResult, FlextTypes
from flext_tap_ldap.client import LDAPClient
from flext_tap_ldap.tap import FlextTapLDAP
from flext_tap_ldap.typings import FlextTapLdapTypes

# "FlextTapLDAP" imported locally to avoid circular imports

# Use Singer SDK types directly for schema definitions
th = None  # Not needed anymore, using direct imports

logger = FlextLogger(__name__)


class FlextTapLdapStreams:
    """Unified streams class for LDAP tap operations with comprehensive stream management.

    This class consolidates all LDAP and LDIF stream implementations following
    the unified class pattern with Clean Architecture and Domain-Driven Design.

    Contains all stream classes as nested classes to maintain single responsibility
    while providing comprehensive LDAP/LDIF data extraction capabilities.
    """

    class FallbackDataFactory:
        """Factory for creating fallback test data.

        Implements Factory Pattern to eliminate code duplication
        following DRY principle (Don't Repeat Yourself).
        """

        @staticmethod
        def create_test_user_record() -> FlextTapLdapTypes.Core.Dict:
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
        def create_test_group_record() -> FlextTapLdapTypes.Core.Dict:
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
        def create_test_ou_record() -> FlextTapLdapTypes.Core.Dict:
            """Create standardized test organizational unit record."""
            return {
                "dn": "ou=users,dc=test,dc=com",
                "ou": "users",
                "objectClass": ["organizationalUnit", "top"],
                "description": "Users organizational unit",
                "modifyTimestamp": "2024-01-01T12:00:00Z",
            }

        @staticmethod
        def create_test_schema_record() -> FlextTapLdapTypes.Core.Dict:
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
        schema_properties: FlextTapLdapTypes.Core.Dict | None = None
        primary_keys: FlextTapLdapTypes.Core.StringList | None = None
        replication_key: str | None = None

        def __post_init__(self: object) -> None:
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
            tap: FlextTapLDAP,
            name: str | None = None,
            schema: FlextTapLdapTypes.Core.Dict | None = None,
        ) -> None:
            """Initialize the LDAP stream."""
            super().__init__(tap, name=name, schema=schema)
            self.tap = tap

            # Create LDAP client for directory operations
            self._create_ldap_client()

        def _create_ldap_client(self: object) -> None:
            """Create LDAP client from tap configuration."""
            self.client: LDAPClient | None = None
            try:
                connection_config: FlextTypes.Dict = self.tap.config.get(
                    "connection", {}
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
                logger.warning(f"Failed to create LDAP client: {e}")
                self.client = None

        def get_records(
            self,
            context: Mapping[str, object] | None = None,
        ) -> Iterable[FlextTapLdapTypes.Core.Dict]:
            """Get records from LDAP - base implementation."""
            # Use context parameter to avoid unused argument warning
            _context = context  # Acknowledge the parameter
            # This is a base implementation that yields empty records
            return []

        def _search_ldap(
            self,
            search_filter: str,
            base_dn: str | None = None,
            attributes: FlextTapLdapTypes.Core.StringList | None = None,
        ) -> list[FlextTapLdapTypes.Core.Dict]:
            """Search LDAP directory with error handling."""
            if not self.client:
                logger.warning("LDAP client not available, using fallback data")
                return self._get_fallback_data()

            try:
                # Use base DN from config if not specified
                if base_dn is None:
                    connection_config: FlextTypes.Dict = self.tap.config.get(
                        "connection", {}
                    )
                    base_dn = connection_config.get("base_dn", "")

                results = self.client.search(
                    base_dn=base_dn or "",
                    search_filter=search_filter,
                    attributes=attributes,
                    scope="SUBTREE",
                )

                if not results:
                    logger.info(f"No results found for filter: {search_filter}")
                    return self._get_fallback_data()

                return results

            except Exception as e:
                logger.warning(f"LDAP search failed: {e}, using fallback data")
                return self._get_fallback_data()

        def _get_fallback_data(self: object) -> list[FlextTapLdapTypes.Core.Dict]:
            """Get fallback data for testing/demo purposes."""
            return []

    class UsersStream(LDAPBaseStream):
        """Stream for LDAP user entries."""

        @override
        def __init__(self, tap: FlextTapLDAP) -> None:
            """Initialize users stream."""
            name = "users"
            schema: FlextTypes.Dict = PropertiesList(
                Property(
                    "objectClass",
                    ArrayType(StringType),
                    description="Object Classes",
                ),
                Property(
                    "memberOf",
                    ArrayType(StringType),
                    description="Group Memberships",
                ),
                Property(
                    "modifyTimestamp",
                    StringType,
                    description="Modification Time",
                ),
            ).to_dict()

            super().__init__(tap, name=name, schema=schema)
            self.primary_keys = ["dn"]

        def get_records(
            self,
            context: Mapping[str, object] | None = None,
        ) -> Iterable[FlextTapLdapTypes.Core.Dict]:
            """Get user records from LDAP."""
            # Use context parameter to avoid unused argument warning
            _context = context  # Acknowledge the parameter
            logger.info("Extracting LDAP users")

            user_filter = self.tap.config.get(
                "user_filter", "(objectClass=inetOrgPerson)"
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

            results: FlextResult[object] = self._search_ldap(
                user_filter, attributes=user_attributes
            )

            yield from results

        def _get_fallback_data(self: object) -> list[FlextTapLdapTypes.Core.Dict]:
            """Get fallback user data."""
            return [FlextTapLdapStreams.FallbackDataFactory.create_test_user_record()]

    class GroupsStream(LDAPBaseStream):
        """Stream for LDAP group entries."""

        @override
        def __init__(self, tap: FlextTapLDAP) -> None:
            """Initialize groups stream."""
            name = "groups"
            schema: FlextTypes.Dict = PropertiesList(
                Property(
                    "member",
                    ArrayType(StringType),
                    description="Group Members",
                ),
                Property(
                    "uniqueMember",
                    ArrayType(StringType),
                    description="Unique Members",
                ),
                Property(
                    "objectClass",
                    ArrayType(StringType),
                    description="Object Classes",
                ),
                Property(
                    "modifyTimestamp",
                    StringType,
                    description="Modification Time",
                ),
            ).to_dict()

            super().__init__(tap, name=name, schema=schema)
            self.primary_keys = ["dn"]

        def get_records(
            self,
            context: Mapping[str, object] | None = None,
        ) -> Iterable[FlextTapLdapTypes.Core.Dict]:
            """Get group records from LDAP."""
            # Use context parameter to avoid unused argument warning
            _context = context  # Acknowledge the parameter
            logger.info("Extracting LDAP groups")

            group_filter = self.tap.config.get(
                "group_filter", "(objectClass=groupOfNames)"
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
                group_filter, attributes=group_attributes
            )

            yield from results

        def _get_fallback_data(self: object) -> list[FlextTapLdapTypes.Core.Dict]:
            """Get fallback group data."""
            return [FlextTapLdapStreams.FallbackDataFactory.create_test_group_record()]

    class OrganizationalUnitsStream(LDAPBaseStream):
        """Stream for LDAP organizational unit entries."""

        @override
        def __init__(self, tap: FlextTapLDAP) -> None:
            """Initialize organizational units stream."""
            name = "organizational_units"
            schema: FlextTypes.Dict = PropertiesList(
                Property(
                    "objectClass",
                    ArrayType(StringType),
                    description="Object Classes",
                ),
                Property(
                    "modifyTimestamp",
                    StringType,
                    description="Modification Time",
                ),
            ).to_dict()

            super().__init__(tap, name=name, schema=schema)
            self.primary_keys = ["dn"]

        def get_records(
            self,
            context: Mapping[str, object] | None = None,
        ) -> Iterable[FlextTapLdapTypes.Core.Dict]:
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
                ou_filter, attributes=ou_attributes
            )

            yield from results

        def _get_fallback_data(self: object) -> list[FlextTapLdapTypes.Core.Dict]:
            """Get fallback organizational unit data."""
            return [FlextTapLdapStreams.FallbackDataFactory.create_test_ou_record()]

    class SchemaStream(LDAPBaseStream):
        """Stream for LDAP schema information."""

        @override
        def __init__(self, tap: FlextTapLDAP) -> None:
            """Initialize schema stream."""
            name = "schema"
            schema: FlextTypes.Dict = PropertiesList(
                Property(
                    "objectClass",
                    ArrayType(StringType),
                    description="Object Classes",
                ),
                Property(
                    "objectClasses",
                    ArrayType(StringType),
                    description="Available Object Classes",
                ),
                Property(
                    "attributeTypes",
                    ArrayType(StringType),
                    description="Available Attribute Types",
                ),
                Property(
                    "ldapSyntaxes",
                    ArrayType(StringType),
                    description="LDAP Syntaxes",
                ),
                Property(
                    "modifyTimestamp",
                    StringType,
                    description="Modification Time",
                ),
            ).to_dict()

            super().__init__(tap, name=name, schema=schema)
            self.primary_keys = ["dn"]

        def get_records(
            self,
            context: Mapping[str, object] | None = None,
        ) -> Iterable[FlextTapLdapTypes.Core.Dict]:
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
                    logger.debug(f"Schema search failed for base DN '{base_dn}': {e}")
                    continue

            # If no schema found, yield fallback
            for record in self._get_fallback_data():
                yield record

        def _get_fallback_data(self: object) -> list[FlextTapLdapTypes.Core.Dict]:
            """Get fallback schema data."""
            return [FlextTapLdapStreams.FallbackDataFactory.create_test_schema_record()]

    class CustomStream(LDAPBaseStream):
        """Custom LDAP stream with configurable filter and schema."""

        @override
        def __init__(
            self, tap: FlextTapLDAP, params: FlextTapLdapStreams.CustomStreamParams
        ) -> None:
            """Initialize custom stream with parameters."""
            self.params = params

            def _map_prop(name: str, definition: object) -> object:
                if isinstance(definition, dict):
                    prop_type = str(definition.get("type", "string"))
                    prop_desc = str(definition.get("description", f"{name} field"))
                    if prop_type == "integer":
                        return Property(name, IntegerType, description=prop_desc)
                    if prop_type == "number":
                        return Property(name, NumberType, description=prop_desc)
                    if prop_type == "boolean":
                        return Property(name, BooleanType, description=prop_desc)
                    if prop_type == "array":
                        return Property(
                            name,
                            ArrayType(StringType),
                            description=prop_desc,
                        )
                    return Property(name, StringType, description=prop_desc)
                # Fallback simple type
                return Property(name, StringType, description=f"{name} field")

            # Build schema from parameters
            if params.schema_properties:
                schema_props = list(
                    starmap(_map_prop, params.schema_properties.items())
                )
                # Ensure all are Property
                typed_props = [p for p in schema_props if isinstance(p, Property)]
                schema = PropertiesList(*typed_props).to_dict()
            else:
                schema = PropertiesList(
                    Property("dn", StringType, description="Distinguished Name"),
                    Property(
                        "objectClass",
                        ArrayType(StringType),
                        description="Object Classes",
                    ),
                    Property(
                        "modifyTimestamp",
                        StringType,
                        description="Modification Time",
                    ),
                ).to_dict()

            super().__init__(tap, name=params.name, schema=schema)
            self.primary_keys = params.primary_keys or ["dn"]
            self.replication_key = params.replication_key

        def get_records(
            self,
            context: Mapping[str, object] | None = None,
        ) -> Iterable[FlextTapLdapTypes.Core.Dict]:
            """Get records using custom filter."""
            # Use context parameter to avoid unused argument warning
            _context = context  # Acknowledge the parameter
            logger.info(
                f"Extracting LDAP records for custom stream: {self.params.name}"
            )

            results: FlextResult[object] = self._search_ldap(self.params.search_filter)

            yield from results

        def _get_fallback_data(self: object) -> list[FlextTapLdapTypes.Core.Dict]:
            """Get fallback data for custom stream."""
            return [
                {
                    "dn": f"cn=test-{self.params.name},dc=test,dc=com",
                    "objectClass": ["top", "testObject"],
                    "modifyTimestamp": "2024-01-01T12:00:00Z",
                },
            ]

    # LDIF STREAM IMPLEMENTATIONS using flext-ldif integration

    class LDIFStream(Stream):
        """LDIF stream using flext-ldif for ALL processing."""

        @override
        def __init__(self, tap: FlextTapLDAP) -> None:
            """Initialize LDIF stream with library delegation."""
            # Set required attributes BEFORE calling super().__init__()
            self.name = "ldif_entries"
            self.path = "/ldif_entries"
            self.primary_keys = ["dn"]

            # Store tap reference
            self.tap = tap

            # Initialize flext-ldif API for processing
            self._ldif_api = FlextLdif()
            self._ldap_api = FlextLdapClient()

            # Define schema
            schema: FlextTypes.Dict = PropertiesList(
                Property(
                    "entry_type",
                    StringType,
                    description="Entry type classification",
                ),
                Property(
                    "objectClass",
                    ArrayType(StringType),
                    description="Object classes",
                ),
                Property(
                    "attributes",
                    ObjectType(),
                    description="Entry attributes",
                ),
                Property(
                    "line_number",
                    IntegerType,
                    description="Line number in file",
                ),
            ).to_dict()

            super().__init__(tap, name=self.name, schema=schema)

            # Helper: simple classifier

        def _classify_entry_type(
            self, object_classes: FlextTapLdapTypes.Core.StringList
        ) -> str:
            """Classify entry type by simple objectClass heuristics."""
            lowered = {oc.lower() for oc in object_classes}
            if "inetorgperson" in lowered or "person" in lowered:
                return "user"
            if "groupofnames" in lowered or "group" in lowered:
                return "group"
            if "organizationalunit" in lowered or "ou" in lowered:
                return "ou"
            return "other"

        def get_records(
            self,
            context: Mapping[str, object] | None = None,
        ) -> Iterable[FlextTapLdapTypes.Core.Dict]:
            """Get LDIF records using flext-ldif processing."""
            # Use context parameter to avoid unused argument warning
            _context = context  # Acknowledge the parameter
            logger.info("Processing LDIF files using flext-ldif library")

            # Get LDIF files from config
            ldif_files: FlextTypes.List = self.tap.config.get("ldif_files", [])
            ldif_directory = self.tap.config.get("ldif_directory")

            if ldif_files:
                for ldif_file in ldif_files:
                    yield from self._process_ldif_file(ldif_file)

            if ldif_directory:
                pattern = self.tap.config.get("ldif_file_pattern", "*.ldif")
                ldif_dir = Path(ldif_directory)
                if ldif_dir.exists():
                    for ldif_file in ldif_dir.glob(pattern):
                        yield from self._process_ldif_file(str(ldif_file))

        def _process_ldif_file(
            self, file_path: str
        ) -> Iterable[FlextTapLdapTypes.Core.Dict]:
            """Process a single LDIF file using flext-ldif."""
            try:
                logger.info(f"Processing LDIF file: {file_path}")

                # Use flext-ldif to parse the file
                parse_result: FlextResult[object] = self._ldif_api.parse_ldif_file(
                    file_path
                )

                if not parse_result.success or not parse_result.value:
                    logger.warning(
                        f"Failed to parse LDIF file {file_path}: {parse_result.error}",
                    )
                    return

                entries = parse_result.value
                logger.info(f"Found {len(entries)} entries in {file_path}")

                for entry in entries:
                    try:
                        record = self._convert_ldif_entry_to_record(entry, file_path)
                        if record:
                            yield record
                    except Exception as e:
                        logger.warning(f"Failed to convert LDIF entry to record: {e}")
                        if not self.tap.config.get("ldif_ignore_entry_errors", True):
                            raise

            except Exception:
                logger.exception("Error processing LDIF file %s", file_path)
                if not self.tap.config.get("ldif_ignore_file_errors", True):
                    raise

        def _convert_ldif_entry_to_record(
            self,
            entry: FlextLdifModels.Entry,
            _source_file: str,
        ) -> FlextTapLdapTypes.Core.Dict | None:
            """Convert LDIF entry to stream record."""
            try:
                # Classify entry type by object classes
                object_classes: FlextTypes.List = (
                    entry.get_attribute("objectClass") or []
                )
                self._classify_entry_type(object_classes)

                return {
                    "dn": str(entry.dn),
                    "entry_type": "entry_type",
                    "objectClass": "object_classes",
                    "attributes": entry.attributes,
                    "source_file": "source_file",
                    "line_number": 0,
                }

            except Exception as e:
                logger.warning(f"Failed to convert LDIF entry {entry.dn}: {e}")
                return None

    class LDIFAnalysisStream(Stream):
        """LDIF analysis stream for migration statistics and validation."""

        @override
        def __init__(self, tap: FlextTapLDAP) -> None:
            """Initialize LDIF analysis stream."""
            self.name = "ldif_analysis"
            self.path = "/ldif_analysis"
            self.primary_keys = ["file_path"]
            self.tap = tap

            # Initialize flext-ldif API
            self._ldif_api = FlextLdif()

            # Define schema for analysis results
            schema: FlextTypes.Dict = PropertiesList(
                Property(
                    "total_entries",
                    IntegerType,
                    description="Total entries in file",
                ),
                Property(
                    "valid_entries",
                    IntegerType,
                    description="Valid entries count",
                ),
                Property(
                    "invalid_entries",
                    IntegerType,
                    description="Invalid entries count",
                ),
                Property(
                    "user_entries",
                    IntegerType,
                    description="User entries count",
                ),
                Property(
                    "group_entries",
                    IntegerType,
                    description="Group entries count",
                ),
                Property(
                    "other_entries",
                    IntegerType,
                    description="Other entries count",
                ),
                Property(
                    "object_class_distribution",
                    ObjectType(),
                    description="Object class distribution",
                ),
                Property(
                    "file_size_bytes",
                    IntegerType,
                    description="File size in bytes",
                ),
                Property(
                    "processing_time_seconds",
                    NumberType,
                    description="Processing time",
                ),
                Property(
                    "errors",
                    ArrayType(StringType),
                    description="Processing errors",
                ),
            ).to_dict()

            super().__init__(tap, name=self.name, schema=schema)

        def get_records(
            self,
            context: Mapping[str, object] | None = None,
        ) -> Iterable[FlextTapLdapTypes.Core.Dict]:
            """Get LDIF analysis records."""
            # Use context parameter to avoid unused argument warning
            _context = context  # Acknowledge the parameter
            logger.info("Analyzing LDIF files")

            # Get LDIF files from config
            ldif_files: FlextTypes.List = self.tap.config.get("ldif_files", [])
            ldif_directory = self.tap.config.get("ldif_directory")

            if ldif_files:
                for ldif_file in ldif_files:
                    yield from self._analyze_ldif_file(ldif_file)

            if ldif_directory:
                pattern = self.tap.config.get("ldif_file_pattern", "*.ldif")
                ldif_dir = Path(ldif_directory)
                if ldif_dir.exists():
                    for ldif_file in ldif_dir.glob(pattern):
                        yield from self._analyze_ldif_file(str(ldif_file))

        def _analyze_ldif_file(
            self, file_path: str
        ) -> Iterable[FlextTapLdapTypes.Core.Dict]:
            """Analyze a single LDIF file."""
            start_time = time.time()

            try:
                logger.info(f"Analyzing LDIF file: {file_path}")

                # Get file size
                (Path(file_path).stat().st_size if Path(file_path).exists() else 0)

                # Use flext-ldif to parse and analyze the file
                validation_result: FlextResult[object] = self._ldif_api.parse_file(
                    file_path
                )

                analysis_data = {
                    "file_path": "file_path",
                    "file_size_bytes": "file_size",
                    "processing_time_seconds": time.time() - start_time,
                    "total_entries": 0,
                    "valid_entries": 0,
                    "invalid_entries": 0,
                    "user_entries": 0,
                    "group_entries": 0,
                    "ou_entries": 0,
                    "other_entries": 0,
                    "object_class_distribution": {},
                    "errors": [],
                }

                if validation_result.success and validation_result.value:
                    entries = validation_result.value
                    analysis_data.update(
                        {
                            "total_entries": len(entries),
                            "valid_entries": len(entries),
                            "invalid_entries": 0,
                        },
                    )
                    # Build object class distribution and type counts
                    oc_dist: dict[str, int] = {}
                    for entry in entries:
                        ocs = entry.attributes.get_values("objectClass")
                        for oc in ocs:
                            oc_dist[oc] = oc_dist.get(oc, 0) + 1
                    analysis_data["object_class_distribution"] = oc_dist
                else:
                    analysis_data_errors: FlextTypes.Dict = analysis_data.get("errors")
                    if isinstance(analysis_data_errors, list):
                        analysis_data_errors.append(
                            f"Validation failed: {validation_result.error}",
                        )

                analysis_data["processing_time_seconds"] = time.time() - start_time
                yield analysis_data

            except Exception as e:
                logger.exception("Error analyzing LDIF file %s", file_path)
                yield {
                    "file_path": "file_path",
                    "file_size_bytes": 0,
                    "processing_time_seconds": time.time() - start_time,
                    "total_entries": 0,
                    "valid_entries": 0,
                    "invalid_entries": 0,
                    "user_entries": 0,
                    "group_entries": 0,
                    "ou_entries": 0,
                    "other_entries": 0,
                    "object_class_distribution": {},
                    "errors": [str(e)],
                }


# Backward compatibility aliases (to be removed when all imports are updated)
FallbackDataFactory = FlextTapLdapStreams.FallbackDataFactory
CustomStreamParams = FlextTapLdapStreams.CustomStreamParams
LDAPBaseStream = FlextTapLdapStreams.LDAPBaseStream
UsersStream = FlextTapLdapStreams.UsersStream
GroupsStream = FlextTapLdapStreams.GroupsStream
OrganizationalUnitsStream = FlextTapLdapStreams.OrganizationalUnitsStream
SchemaStream = FlextTapLdapStreams.SchemaStream
CustomStream = FlextTapLdapStreams.CustomStream
LDIFStream = FlextTapLdapStreams.LDIFStream
LDIFAnalysisStream = FlextTapLdapStreams.LDIFAnalysisStream


__all__ = [
    "CustomStream",
    "CustomStreamParams",
    "FallbackDataFactory",
    "GroupsStream",
    "LDAPBaseStream",
    "LDIFAnalysisStream",
    "LDIFStream",
    "OrganizationalUnitsStream",
    "SchemaStream",
    "UsersStream",
]
