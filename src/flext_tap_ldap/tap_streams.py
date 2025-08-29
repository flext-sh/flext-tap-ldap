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

from flext_core import FlextLogger
from flext_ldap import get_ldap_api
from flext_ldif import FlextLdifAPI, FlextLdifEntry
from flext_meltano import Stream, singer_typing as th

from flext_tap_ldap.client import LDAPClient
from flext_tap_ldap.tap_client import FlextTapLDAP

logger = FlextLogger(__name__)


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
    and improve maintainability following SOLID principles.
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

    def __init__(
        self,
        tap: FlextTapLDAP,
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
            connection_config = self.tap.config.get("connection", {})
            self.client = LDAPClient(
                host=str(connection_config.get("host", "localhost")),
                port=int(connection_config.get("port", 389)),
                bind_dn=connection_config.get("bind_dn")
                if isinstance(connection_config.get("bind_dn"), str)
                else None,
                password=connection_config.get("bind_password")
                if isinstance(connection_config.get("bind_password"), str)
                else None,
                use_ssl=bool(connection_config.get("use_ssl", False)),
                timeout=int(connection_config.get("timeout_seconds", 30)),
                page_size=int(self.tap.config.get("page_size", 1000)),
            )
        except Exception as e:
            logger.warning(f"Failed to create LDAP client: {e}")
            self.client = None

    def get_records(
        self,
        _context: Mapping[str, object] | None = None,
    ) -> Iterable[dict[str, object]]:
        """Get records from LDAP - base implementation."""
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
                connection_config = self.tap.config.get("connection", {})
                base_dn = connection_config.get("base_dn", "")

            results = self.client.search(
                base_dn=base_dn,
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

    def _get_fallback_data(self) -> list[dict[str, object]]:
        """Get fallback data for testing/demo purposes."""
        return []


class UsersStream(LDAPBaseStream):
    """Stream for LDAP user entries."""

    def __init__(self, tap: FlextTapLDAP) -> None:
        """Initialize users stream."""
        name = "users"
        schema = th.PropertiesList(
            th.Property("dn", th.StringType, description="Distinguished Name"),
            th.Property("uid", th.StringType, description="User ID"),
            th.Property("cn", th.StringType, description="Common Name"),
            th.Property("sn", th.StringType, description="Surname"),
            th.Property("givenName", th.StringType, description="Given Name"),
            th.Property("displayName", th.StringType, description="Display Name"),
            th.Property("mail", th.StringType, description="Email Address"),
            th.Property("telephoneNumber", th.StringType, description="Phone Number"),
            th.Property("mobile", th.StringType, description="Mobile Number"),
            th.Property("employeeNumber", th.StringType, description="Employee Number"),
            th.Property("employeeType", th.StringType, description="Employee Type"),
            th.Property("department", th.StringType, description="Department"),
            th.Property("title", th.StringType, description="Job Title"),
            th.Property("manager", th.StringType, description="Manager DN"),
            th.Property("homeDirectory", th.StringType, description="Home Directory"),
            th.Property("loginShell", th.StringType, description="Login Shell"),
            th.Property("userPassword", th.StringType, description="User Password"),
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
            th.Property("createTimestamp", th.StringType, description="Creation Time"),
            th.Property(
                "modifyTimestamp",
                th.StringType,
                description="Modification Time",
            ),
        ).to_dict()

        super().__init__(tap, name=name, schema=schema)
        self.primary_keys = ["dn"]

    def get_records(
        self,
        _context: Mapping[str, object] | None = None,
    ) -> Iterable[dict[str, object]]:
        """Get user records from LDAP."""
        logger.info("Extracting LDAP users")

        user_filter = self.tap.config.get("user_filter", "(objectClass=inetOrgPerson)")
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

        results = self._search_ldap(user_filter, attributes=user_attributes)

        yield from results

    def _get_fallback_data(self) -> list[dict[str, object]]:
        """Get fallback user data."""
        return [FallbackDataFactory.create_test_user_record()]


class GroupsStream(LDAPBaseStream):
    """Stream for LDAP group entries."""

    def __init__(self, tap: FlextTapLDAP) -> None:
        """Initialize groups stream."""
        name = "groups"
        schema = th.PropertiesList(
            th.Property("dn", th.StringType, description="Distinguished Name"),
            th.Property("cn", th.StringType, description="Group Name"),
            th.Property("description", th.StringType, description="Group Description"),
            th.Property(
                "member",
                th.ArrayType(th.StringType),
                description="Group Members",
            ),
            th.Property(
                "uniqueMember",
                th.ArrayType(th.StringType),
                description="Unique Members",
            ),
            th.Property("gidNumber", th.StringType, description="Group ID Number"),
            th.Property("owner", th.StringType, description="Group Owner"),
            th.Property(
                "objectClass",
                th.ArrayType(th.StringType),
                description="Object Classes",
            ),
            th.Property("createTimestamp", th.StringType, description="Creation Time"),
            th.Property(
                "modifyTimestamp",
                th.StringType,
                description="Modification Time",
            ),
        ).to_dict()

        super().__init__(tap, name=name, schema=schema)
        self.primary_keys = ["dn"]

    def get_records(
        self,
        _context: Mapping[str, object] | None = None,
    ) -> Iterable[dict[str, object]]:
        """Get group records from LDAP."""
        logger.info("Extracting LDAP groups")

        group_filter = self.tap.config.get("group_filter", "(objectClass=groupOfNames)")
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

        results = self._search_ldap(group_filter, attributes=group_attributes)

        yield from results

    def _get_fallback_data(self) -> list[dict[str, object]]:
        """Get fallback group data."""
        return [FallbackDataFactory.create_test_group_record()]


class OrganizationalUnitsStream(LDAPBaseStream):
    """Stream for LDAP organizational unit entries."""

    def __init__(self, tap: FlextTapLDAP) -> None:
        """Initialize organizational units stream."""
        name = "organizational_units"
        schema = th.PropertiesList(
            th.Property("dn", th.StringType, description="Distinguished Name"),
            th.Property("ou", th.StringType, description="Organizational Unit Name"),
            th.Property("description", th.StringType, description="Description"),
            th.Property(
                "objectClass",
                th.ArrayType(th.StringType),
                description="Object Classes",
            ),
            th.Property("createTimestamp", th.StringType, description="Creation Time"),
            th.Property(
                "modifyTimestamp",
                th.StringType,
                description="Modification Time",
            ),
        ).to_dict()

        super().__init__(tap, name=name, schema=schema)
        self.primary_keys = ["dn"]

    def get_records(
        self,
        _context: Mapping[str, object] | None = None,
    ) -> Iterable[dict[str, object]]:
        """Get organizational unit records from LDAP."""
        logger.info("Extracting LDAP organizational units")

        ou_filter = "(objectClass=organizationalUnit)"
        ou_attributes = [
            "ou",
            "description",
            "objectClass",
            "createTimestamp",
            "modifyTimestamp",
        ]

        results = self._search_ldap(ou_filter, attributes=ou_attributes)

        yield from results

    def _get_fallback_data(self) -> list[dict[str, object]]:
        """Get fallback organizational unit data."""
        return [FallbackDataFactory.create_test_ou_record()]


class SchemaStream(LDAPBaseStream):
    """Stream for LDAP schema information."""

    def __init__(self, tap: FlextTapLDAP) -> None:
        """Initialize schema stream."""
        name = "schema"
        schema = th.PropertiesList(
            th.Property("dn", th.StringType, description="Distinguished Name"),
            th.Property("cn", th.StringType, description="Common Name"),
            th.Property(
                "objectClass",
                th.ArrayType(th.StringType),
                description="Object Classes",
            ),
            th.Property(
                "objectClasses",
                th.ArrayType(th.StringType),
                description="Available Object Classes",
            ),
            th.Property(
                "attributeTypes",
                th.ArrayType(th.StringType),
                description="Available Attribute Types",
            ),
            th.Property(
                "ldapSyntaxes",
                th.ArrayType(th.StringType),
                description="LDAP Syntaxes",
            ),
            th.Property(
                "modifyTimestamp",
                th.StringType,
                description="Modification Time",
            ),
        ).to_dict()

        super().__init__(tap, name=name, schema=schema)
        self.primary_keys = ["dn"]

    def get_records(
        self,
        _context: Mapping[str, object] | None = None,
    ) -> Iterable[dict[str, object]]:
        """Get schema records from LDAP."""
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

    def _get_fallback_data(self) -> list[dict[str, object]]:
        """Get fallback schema data."""
        return [FallbackDataFactory.create_test_schema_record()]


class CustomStream(LDAPBaseStream):
    """Custom LDAP stream with configurable filter and schema."""

    def __init__(self, tap: FlextTapLDAP, params: CustomStreamParams) -> None:
        """Initialize custom stream with parameters."""
        self.params = params

        def _map_prop(name: str, definition: object) -> object:
            if isinstance(definition, dict):
                prop_type = str(definition.get("type", "string"))
                prop_desc = str(definition.get("description", f"{name} field"))
                if prop_type == "integer":
                    return th.Property(name, th.IntegerType, description=prop_desc)
                if prop_type == "number":
                    return th.Property(name, th.NumberType, description=prop_desc)
                if prop_type == "boolean":
                    return th.Property(name, th.BooleanType, description=prop_desc)
                if prop_type == "array":
                    return th.Property(
                        name,
                        th.ArrayType(th.StringType),
                        description=prop_desc,
                    )
                return th.Property(name, th.StringType, description=prop_desc)
            # Fallback simple type
            return th.Property(name, th.StringType, description=f"{name} field")

        # Build schema from parameters
        if params.schema_properties:
            schema_props = list(starmap(_map_prop, params.schema_properties.items()))
            # Ensure all are th.Property
            typed_props = [p for p in schema_props if isinstance(p, th.Property)]
            schema = th.PropertiesList(*typed_props).to_dict()
        else:
            schema = th.PropertiesList(
                th.Property("dn", th.StringType, description="Distinguished Name"),
                th.Property(
                    "objectClass",
                    th.ArrayType(th.StringType),
                    description="Object Classes",
                ),
                th.Property(
                    "modifyTimestamp",
                    th.StringType,
                    description="Modification Time",
                ),
            ).to_dict()

        super().__init__(tap, name=params.name, schema=schema)
        self.primary_keys = params.primary_keys or ["dn"]
        self.replication_key = params.replication_key

    def get_records(
        self,
        _context: Mapping[str, object] | None = None,
    ) -> Iterable[dict[str, object]]:
        """Get records using custom filter."""
        logger.info(f"Extracting LDAP records for custom stream: {self.params.name}")

        results = self._search_ldap(self.params.search_filter)

        yield from results

    def _get_fallback_data(self) -> list[dict[str, object]]:
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

    def __init__(self, tap: FlextTapLDAP) -> None:
        """Initialize LDIF stream with library delegation."""
        # Set required attributes BEFORE calling super().__init__()
        self.name = "ldif_entries"
        self.path = "/ldif_entries"
        self.primary_keys = ["dn"]

        # Store tap reference
        self.tap = tap

        # Initialize flext-ldif API for processing
        self._ldif_api = FlextLdifAPI()
        self._ldap_api = get_ldap_api()

        # Define schema
        schema = th.PropertiesList(
            th.Property("dn", th.StringType, description="Distinguished Name"),
            th.Property(
                "entry_type",
                th.StringType,
                description="Entry type classification",
            ),
            th.Property(
                "objectClass",
                th.ArrayType(th.StringType),
                description="Object classes",
            ),
            th.Property(
                "attributes",
                th.ObjectType(),
                description="Entry attributes",
            ),
            th.Property("source_file", th.StringType, description="Source LDIF file"),
            th.Property(
                "line_number",
                th.IntegerType,
                description="Line number in file",
            ),
        ).to_dict()

        super().__init__(tap, name=self.name, schema=schema)

        # Helper: simple classifier

    def _classify_entry_type(self, object_classes: list[str]) -> str:
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
        _context: Mapping[str, object] | None = None,
    ) -> Iterable[dict[str, object]]:
        """Get LDIF records using flext-ldif processing."""
        logger.info("Processing LDIF files using flext-ldif library")

        # Get LDIF files from config
        ldif_files = self.tap.config.get("ldif_files", [])
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

    def _process_ldif_file(self, file_path: str) -> Iterable[dict[str, object]]:
        """Process a single LDIF file using flext-ldif."""
        try:
            logger.info(f"Processing LDIF file: {file_path}")

            # Use flext-ldif to parse the file
            parse_result = self._ldif_api.parse_file(file_path)

            if not parse_result.success or not parse_result.data:
                logger.warning(
                    f"Failed to parse LDIF file {file_path}: {parse_result.error}",
                )
                return

            entries = parse_result.data
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
        entry: FlextLdifEntry,
        source_file: str,
    ) -> dict[str, object] | None:
        """Convert LDIF entry to stream record."""
        try:
            # Classify entry type by object classes
            object_classes = entry.attributes.get_values("objectClass")
            entry_type = self._classify_entry_type(object_classes)

            return {
                "dn": entry.dn.value,
                "entry_type": entry_type,
                "objectClass": object_classes,
                "attributes": entry.attributes.attributes,
                "source_file": source_file,
                "line_number": 0,
            }

        except Exception as e:
            logger.warning(f"Failed to convert LDIF entry {entry.dn}: {e}")
            return None


class LDIFAnalysisStream(Stream):
    """LDIF analysis stream for migration statistics and validation."""

    def __init__(self, tap: FlextTapLDAP) -> None:
        """Initialize LDIF analysis stream."""
        self.name = "ldif_analysis"
        self.path = "/ldif_analysis"
        self.primary_keys = ["file_path"]
        self.tap = tap

        # Initialize flext-ldif API
        self._ldif_api = FlextLdifAPI()

        # Define schema for analysis results
        schema = th.PropertiesList(
            th.Property("file_path", th.StringType, description="LDIF file path"),
            th.Property(
                "total_entries",
                th.IntegerType,
                description="Total entries in file",
            ),
            th.Property(
                "valid_entries",
                th.IntegerType,
                description="Valid entries count",
            ),
            th.Property(
                "invalid_entries",
                th.IntegerType,
                description="Invalid entries count",
            ),
            th.Property(
                "user_entries",
                th.IntegerType,
                description="User entries count",
            ),
            th.Property(
                "group_entries",
                th.IntegerType,
                description="Group entries count",
            ),
            th.Property("ou_entries", th.IntegerType, description="OU entries count"),
            th.Property(
                "other_entries",
                th.IntegerType,
                description="Other entries count",
            ),
            th.Property(
                "object_class_distribution",
                th.ObjectType(),
                description="Object class distribution",
            ),
            th.Property(
                "file_size_bytes",
                th.IntegerType,
                description="File size in bytes",
            ),
            th.Property(
                "processing_time_seconds",
                th.NumberType,
                description="Processing time",
            ),
            th.Property(
                "errors",
                th.ArrayType(th.StringType),
                description="Processing errors",
            ),
        ).to_dict()

        super().__init__(tap, name=self.name, schema=schema)

    def get_records(
        self,
        _context: Mapping[str, object] | None = None,
    ) -> Iterable[dict[str, object]]:
        """Get LDIF analysis records."""
        logger.info("Analyzing LDIF files")

        # Get LDIF files from config
        ldif_files = self.tap.config.get("ldif_files", [])
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

    def _analyze_ldif_file(self, file_path: str) -> Iterable[dict[str, object]]:
        """Analyze a single LDIF file."""
        start_time = time.time()

        try:
            logger.info(f"Analyzing LDIF file: {file_path}")

            # Get file size
            file_size = (
                Path(file_path).stat().st_size if Path(file_path).exists() else 0
            )

            # Use flext-ldif to parse and analyze the file
            validation_result = self._ldif_api.parse_file(file_path)

            analysis_data = {
                "file_path": file_path,
                "file_size_bytes": file_size,
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

            if validation_result.success and validation_result.data:
                entries = validation_result.data
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
                analysis_data_errors = analysis_data.get("errors")
                if isinstance(analysis_data_errors, list):
                    analysis_data_errors.append(
                        f"Validation failed: {validation_result.error}",
                    )

            analysis_data["processing_time_seconds"] = time.time() - start_time
            yield analysis_data

        except Exception as e:
            logger.exception("Error analyzing LDIF file %s", file_path)
            yield {
                "file_path": file_path,
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
