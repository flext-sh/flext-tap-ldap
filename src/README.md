# 📡 TAP LDAP - Source Implementation

> **Module**: Complete LDAP tap source implementation with enterprise directory extraction and Singer SDK integration | **Audience**: Data Engineers, LDAP Administrators, Singer SDK Developers | **Status**: Production Ready

## 📋 **Overview**

Complete source implementation of the TAP LDAP Singer tap, providing comprehensive data extraction from LDAP directory services with advanced schema discovery, incremental synchronization, and enterprise directory management capabilities for seamless data pipeline integration.

---

## 🧭 **Navigation Context**

**🏠 Root**: [PyAuto Home](../../README.md) → **📂 Component**: [TAP LDAP](../README.md) → **📂 Current**: Source Implementation

---

## 🎯 **Module Purpose**

This source module implements a production-ready Singer tap for LDAP directory services, following Singer SDK specifications with comprehensive directory discovery, incremental extraction, and enterprise LDAP integration patterns for complex directory environments.

### **Key Capabilities**

- **Enterprise LDAP Extraction** - Comprehensive LDAP directory data extraction
- **Dynamic Discovery** - Automatic LDAP schema and structure discovery
- **Incremental Sync** - Efficient incremental data extraction with bookmarking
- **Stream Management** - Multiple stream implementations for different entity types
- **Performance Optimization** - Connection pooling and query optimization
- **Error Handling** - Comprehensive error recovery and retry mechanisms

---

## 📁 **Module Structure**

```
src/tap_ldap/
├── __init__.py              # Public API exports and Singer tap registration
├── client.py                # LDAP client implementation with connection management
├── ldif_processor.py        # LDIF processing and parsing capabilities
├── ldif_stream.py           # LDIF-based stream implementation
├── streams.py               # Core stream implementations for LDAP entities
└── tap.py                   # Main Singer tap implementation
```

---

## 🔧 **Core Components**

### **1. Main Tap Implementation (tap.py)**

Singer SDK-compliant tap implementation:

```python
class TapLDAP(Tap):
    """LDAP directory Singer tap for data extraction.

    Implements Singer SDK specification for LDAP directory
    data extraction with comprehensive stream management and discovery.
    """

    name = "tap-ldap"
    config_jsonschema = th.PropertiesList(
        th.Property("ldap_server", th.StringType, required=True),
        th.Property("ldap_port", th.IntegerType, default=389),
        th.Property("bind_dn", th.StringType, required=True),
        th.Property("bind_password", th.StringType, required=True, secret=True),
        th.Property("base_dn", th.StringType, required=True),
        th.Property("use_ssl", th.BooleanType, default=False),
        th.Property("use_tls", th.BooleanType, default=False),
        th.Property("page_size", th.IntegerType, default=1000),
        th.Property("timeout", th.IntegerType, default=60),
        th.Property("auto_discover", th.BooleanType, default=True),
        th.Property("extract_deleted", th.BooleanType, default=False),
    ).to_dict()

    def discover_streams(self) -> List[Stream]:
        """Discover available LDAP streams."""

        streams = []

        # Core LDAP streams
        streams.extend([
            UsersStream(tap=self),
            GroupsStream(tap=self),
            OrganizationalUnitsStream(tap=self),
            ContactsStream(tap=self),
        ])

        # Auto-discover additional streams if enabled
        if self.config.get("auto_discover", True):
            discovered_streams = self._auto_discover_streams()
            streams.extend(discovered_streams)

        return streams

    def _auto_discover_streams(self) -> List[Stream]:
        """Auto-discover additional LDAP streams."""

        discovered_streams = []

        with LdapClient(self.config) as client:
            # Discover object classes in use
            object_classes = client.discover_object_classes()

            for object_class in object_classes:
                if object_class not in ["user", "group", "organizationalUnit", "contact"]:
                    # Create dynamic stream for discovered object class
                    stream_class = self._create_dynamic_stream_class(object_class)
                    discovered_streams.append(stream_class(tap=self))

        return discovered_streams

    def _create_dynamic_stream_class(self, object_class: str) -> Type[Stream]:
        """Create dynamic stream class for discovered object class."""

        class DynamicLdapStream(LdapStream):
            name = f"{object_class}_objects"
            object_class_filter = object_class

            @property
            def schema(self) -> dict:
                # Generate schema based on object class attributes
                return self._generate_schema_for_object_class(object_class)

        return DynamicLdapStream
```

### **2. LDAP Client (client.py)**

Comprehensive LDAP client with connection management:

```python
class LdapClient:
    """LDAP client with comprehensive directory operations.

    Provides enterprise LDAP connectivity with connection pooling,
    error handling, and advanced query capabilities.
    """

    def __init__(self, config: dict):
        self.config = config
        self._connection_pool = self._create_connection_pool()
        self._schema_cache = {}

    def __enter__(self):
        """Context manager entry."""
        self._connection = self._get_connection()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if hasattr(self, '_connection'):
            self._return_connection(self._connection)

    def search_entries(
        self,
        search_base: str,
        search_filter: str,
        attributes: List[str] = None,
        search_scope: str = SUBTREE,
        paged: bool = True,
        page_size: int = None
    ) -> Iterator[Dict[str, Any]]:
        """Search LDAP entries with pagination support."""

        page_size = page_size or self.config.get("page_size", 1000)

        if paged:
            # Use paged search for large result sets
            cookie = None
            while True:
                entries, cookie = self._paged_search(
                    search_base, search_filter, attributes, search_scope, page_size, cookie
                )

                for entry in entries:
                    yield self._format_ldap_entry(entry)

                if not cookie:
                    break
        else:
            # Simple search for small result sets
            entries = self._simple_search(search_base, search_filter, attributes, search_scope)
            for entry in entries:
                yield self._format_ldap_entry(entry)

    def _paged_search(
        self,
        search_base: str,
        search_filter: str,
        attributes: List[str],
        search_scope: str,
        page_size: int,
        cookie: bytes = None
    ) -> Tuple[List[Entry], bytes]:
        """Perform paged LDAP search."""

        try:
            search_result = self._connection.search(
                search_base=search_base,
                search_filter=search_filter,
                search_scope=search_scope,
                attributes=attributes,
                paged_size=page_size,
                paged_cookie=cookie
            )

            if search_result:
                entries = list(self._connection.entries)
                new_cookie = self._connection.result.get('controls', {}).get('1.2.840.113556.1.4.319', {}).get('value', {}).get('cookie')
                return entries, new_cookie
            else:
                return [], None

        except Exception as e:
            raise LdapSearchError(f"LDAP search failed: {e}")

    def get_entry_by_dn(self, dn: str, attributes: List[str] = None) -> Optional[Dict[str, Any]]:
        """Get specific LDAP entry by DN."""

        try:
            search_result = self._connection.search(
                search_base=dn,
                search_filter="(objectClass=*)",
                search_scope=BASE,
                attributes=attributes
            )

            if search_result and self._connection.entries:
                return self._format_ldap_entry(self._connection.entries[0])
            else:
                return None

        except Exception as e:
            raise LdapSearchError(f"LDAP entry lookup failed: {e}")

    def discover_object_classes(self) -> List[str]:
        """Discover object classes in use in the directory."""

        object_classes = set()

        # Search for all entries and collect object classes
        for entry in self.search_entries(
            search_base=self.config["base_dn"],
            search_filter="(objectClass=*)",
            attributes=["objectClass"],
            paged=True,
            page_size=100
        ):
            entry_object_classes = entry.get("objectClass", [])
            if isinstance(entry_object_classes, str):
                entry_object_classes = [entry_object_classes]

            object_classes.update(entry_object_classes)

        return sorted(list(object_classes))

    def get_schema_info(self) -> Dict[str, Any]:
        """Get LDAP schema information."""

        if self._schema_cache:
            return self._schema_cache

        try:
            # Get schema from server
            schema = self._connection.server.schema

            schema_info = {
                "object_classes": {
                    name: {
                        "must_attributes": list(oc.must_contain),
                        "may_attributes": list(oc.may_contain),
                        "superior_classes": list(oc.superior)
                    }
                    for name, oc in schema.object_classes.items()
                },
                "attributes": {
                    name: {
                        "syntax": attr.syntax,
                        "single_value": attr.single_value,
                        "equality_rule": attr.equality
                    }
                    for name, attr in schema.attribute_types.items()
                }
            }

            self._schema_cache = schema_info
            return schema_info

        except Exception as e:
            raise LdapSchemaError(f"Failed to retrieve LDAP schema: {e}")

    def _format_ldap_entry(self, entry: Entry) -> Dict[str, Any]:
        """Format LDAP entry for output."""

        formatted = {
            "dn": str(entry.entry_dn),
            "_metadata": {
                "last_modified": self._get_entry_timestamp(entry),
                "object_guid": self._get_entry_guid(entry)
            }
        }

        # Process entry attributes
        for attr_name in entry.entry_attributes:
            attr_values = getattr(entry, attr_name)

            # Handle single vs multi-value attributes
            if isinstance(attr_values, list):
                if len(attr_values) == 1:
                    formatted[attr_name] = attr_values[0]
                else:
                    formatted[attr_name] = attr_values
            else:
                formatted[attr_name] = attr_values

        return formatted

    def _get_entry_timestamp(self, entry: Entry) -> Optional[str]:
        """Get entry last modified timestamp."""

        # Try different timestamp attributes
        timestamp_attrs = ["whenChanged", "modifyTimeStamp", "whenModified"]

        for attr in timestamp_attrs:
            if hasattr(entry, attr):
                timestamp = getattr(entry, attr)
                if timestamp:
                    return str(timestamp)

        return None

    def _get_entry_guid(self, entry: Entry) -> Optional[str]:
        """Get entry GUID if available."""

        if hasattr(entry, "objectGUID"):
            guid = getattr(entry, "objectGUID")
            if guid:
                return str(guid)

        return None
```

### **3. Core Streams (streams.py)**

Stream implementations for different LDAP entity types:

```python
class LdapStream(RESTStream):
    """Base LDAP stream implementation."""

    def __init__(self, tap: Tap):
        super().__init__(tap)
        self.ldap_client = LdapClient(tap.config)

    @property
    def url_base(self) -> str:
        """Not applicable for LDAP."""
        return ""

    def get_records(self, context: Optional[dict]) -> Iterable[dict]:
        """Get records from LDAP directory."""

        with self.ldap_client as client:
            search_filter = self._build_search_filter(context)
            search_base = self._get_search_base(context)
            attributes = self._get_attributes()

            for entry in client.search_entries(
                search_base=search_base,
                search_filter=search_filter,
                attributes=attributes,
                paged=True
            ):
                yield entry

    def _build_search_filter(self, context: Optional[dict]) -> str:
        """Build LDAP search filter."""
        raise NotImplementedError("Subclasses must implement _build_search_filter")

    def _get_search_base(self, context: Optional[dict]) -> str:
        """Get search base DN."""
        return self.config.get("base_dn")

    def _get_attributes(self) -> List[str]:
        """Get attributes to retrieve."""
        # Return all attributes by default
        return ["*"]

class UsersStream(LdapStream):
    """Stream for LDAP user entries."""

    name = "users"
    primary_keys = ["dn"]
    replication_key = "_metadata.last_modified"

    @property
    def schema(self) -> dict:
        """User stream schema."""
        return {
            "type": "object",
            "properties": {
                "dn": {"type": "string"},
                "cn": {"type": ["string", "null"]},
                "sn": {"type": ["string", "null"]},
                "givenName": {"type": ["string", "null"]},
                "displayName": {"type": ["string", "null"]},
                "mail": {"type": ["string", "null"]},
                "sAMAccountName": {"type": ["string", "null"]},
                "userPrincipalName": {"type": ["string", "null"]},
                "telephoneNumber": {"type": ["string", "null"]},
                "mobile": {"type": ["string", "null"]},
                "department": {"type": ["string", "null"]},
                "title": {"type": ["string", "null"]},
                "manager": {"type": ["string", "null"]},
                "memberOf": {
                    "type": ["array", "null"],
                    "items": {"type": "string"}
                },
                "objectClass": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "_metadata": {
                    "type": "object",
                    "properties": {
                        "last_modified": {"type": ["string", "null"]},
                        "object_guid": {"type": ["string", "null"]}
                    }
                }
            }
        }

    def _build_search_filter(self, context: Optional[dict]) -> str:
        """Build search filter for users."""
        base_filter = "(|(objectClass=person)(objectClass=user)(objectClass=inetOrgPerson))"

        # Add incremental filter if available
        if context and context.get("last_modified"):
            timestamp = context["last_modified"]
            incremental_filter = f"(whenChanged>={timestamp})"
            return f"(&{base_filter}{incremental_filter})"

        return base_filter

class GroupsStream(LdapStream):
    """Stream for LDAP group entries."""

    name = "groups"
    primary_keys = ["dn"]
    replication_key = "_metadata.last_modified"

    @property
    def schema(self) -> dict:
        """Group stream schema."""
        return {
            "type": "object",
            "properties": {
                "dn": {"type": "string"},
                "cn": {"type": ["string", "null"]},
                "description": {"type": ["string", "null"]},
                "member": {
                    "type": ["array", "null"],
                    "items": {"type": "string"}
                },
                "memberOf": {
                    "type": ["array", "null"],
                    "items": {"type": "string"}
                },
                "groupType": {"type": ["integer", "null"]},
                "sAMAccountName": {"type": ["string", "null"]},
                "objectClass": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "_metadata": {
                    "type": "object",
                    "properties": {
                        "last_modified": {"type": ["string", "null"]},
                        "object_guid": {"type": ["string", "null"]}
                    }
                }
            }
        }

    def _build_search_filter(self, context: Optional[dict]) -> str:
        """Build search filter for groups."""
        base_filter = "(|(objectClass=group)(objectClass=groupOfNames)(objectClass=posixGroup))"

        # Add incremental filter if available
        if context and context.get("last_modified"):
            timestamp = context["last_modified"]
            incremental_filter = f"(whenChanged>={timestamp})"
            return f"(&{base_filter}{incremental_filter})"

        return base_filter

class OrganizationalUnitsStream(LdapStream):
    """Stream for LDAP organizational unit entries."""

    name = "organizational_units"
    primary_keys = ["dn"]
    replication_key = "_metadata.last_modified"

    def _build_search_filter(self, context: Optional[dict]) -> str:
        """Build search filter for organizational units."""
        return "(objectClass=organizationalUnit)"

class ContactsStream(LdapStream):
    """Stream for LDAP contact entries."""

    name = "contacts"
    primary_keys = ["dn"]
    replication_key = "_metadata.last_modified"

    def _build_search_filter(self, context: Optional[dict]) -> str:
        """Build search filter for contacts."""
        return "(objectClass=contact)"
```

### **4. LDIF Processing (ldif_processor.py)**

LDIF file processing capabilities:

```python
class LdifProcessor:
    """LDIF file processor for LDAP data extraction.

    Provides comprehensive LDIF parsing and processing capabilities
    for bulk LDAP data extraction and transformation.
    """

    def __init__(self, config: dict):
        self.config = config
        self.encoding = config.get("ldif_encoding", "utf-8")

    def process_ldif_file(self, file_path: str) -> Iterator[Dict[str, Any]]:
        """Process LDIF file and yield entries."""

        try:
            with open(file_path, 'r', encoding=self.encoding) as ldif_file:
                ldif_parser = ldif.LDIFRecordList(ldif_file)
                ldif_parser.parse()

                for dn, entry in ldif_parser.all_records:
                    formatted_entry = self._format_ldif_entry(dn, entry)
                    yield formatted_entry

        except Exception as e:
            raise LdifProcessingError(f"LDIF processing failed: {e}")

    def _format_ldif_entry(self, dn: str, entry: dict) -> Dict[str, Any]:
        """Format LDIF entry for output."""

        formatted = {
            "dn": dn,
            "_metadata": {
                "source": "ldif",
                "processed_at": datetime.utcnow().isoformat()
            }
        }

        # Process entry attributes
        for attr_name, attr_values in entry.items():
            if isinstance(attr_values, list) and len(attr_values) == 1:
                formatted[attr_name] = attr_values[0].decode('utf-8') if isinstance(attr_values[0], bytes) else attr_values[0]
            else:
                formatted[attr_name] = [
                    value.decode('utf-8') if isinstance(value, bytes) else value
                    for value in attr_values
                ]

        return formatted
```

---

## 🔄 **Operation Workflows**

### **Complete LDAP Extraction Workflow**

```python
async def execute_ldap_extraction(
    tap: TapLDAP,
    catalog: Catalog,
    state: Optional[Dict] = None
) -> ExtractionResult:
    """Execute complete LDAP data extraction."""

    extraction_stats = ExtractionStats()

    try:
        # Initialize tap
        tap.catalog = catalog
        if state:
            tap.load_state(state)

        # Test connectivity
        with LdapClient(tap.config) as client:
            # Verify connection
            schema_info = client.get_schema_info()
            extraction_stats.schema_objects = len(schema_info["object_classes"])

        # Process selected streams
        for catalog_stream in catalog.streams:
            if catalog_stream.metadata.selected:
                stream = tap.get_stream(catalog_stream.tap_stream_id)

                # Extract stream data
                stream_stats = await extract_stream_data(stream, catalog_stream)
                extraction_stats.add_stream_stats(catalog_stream.tap_stream_id, stream_stats)

        return ExtractionResult(
            streams_extracted=len(extraction_stats.stream_stats),
            total_records=extraction_stats.total_records,
            extraction_duration=extraction_stats.get_duration(),
            final_state=tap.get_state(),
            schema_info=schema_info
        )

    except Exception as e:
        raise LdapExtractionError(f"LDAP extraction failed: {e}")
```

---

## 🧪 **Testing Utilities**

### **Test Patterns**

```python
@pytest.mark.asyncio
async def test_ldap_user_extraction():
    """Test LDAP user extraction functionality."""
    config = {
        "ldap_server": "test-ldap.company.com",
        "ldap_port": 389,
        "bind_dn": "cn=admin,dc=company,dc=com",
        "bind_password": "test_password",
        "base_dn": "dc=company,dc=com"
    }

    tap = TapLDAP(config=config)
    users_stream = UsersStream(tap=tap)

    # Mock LDAP responses
    with patch.object(LdapClient, 'search_entries') as mock_search:
        mock_search.return_value = [
            {
                "dn": "cn=John Doe,ou=Users,dc=company,dc=com",
                "cn": "John Doe",
                "mail": "john.doe@company.com",
                "sAMAccountName": "jdoe",
                "objectClass": ["person", "user"]
            }
        ]

        records = list(users_stream.get_records({}))
        assert len(records) == 1
        assert records[0]["cn"] == "John Doe"
        assert records[0]["mail"] == "john.doe@company.com"
```

---

## 🔗 **Cross-References**

### **Component Documentation**

- [Component Overview](../README.md) - Complete TAP LDAP documentation
- [Examples](../examples/README.md) - Usage examples and configurations
- [Tests](../tests/README.md) - Testing strategies and utilities

### **Singer SDK References**

- [Singer SDK Documentation](https://sdk.meltano.com/en/latest/) - Singer SDK specification
- [Tap Patterns](https://sdk.meltano.com/en/latest/taps.html) - Tap implementation patterns
- [Stream Development](https://sdk.meltano.com/en/latest/stream_maps.html) - Stream implementation guide

### **LDAP References**

- [LDAP Protocol Specification](https://tools.ietf.org/html/rfc4511) - LDAP protocol standards
- [LDIF Format Specification](https://tools.ietf.org/html/rfc2849) - LDIF format standards

---

**📂 Module**: Source Implementation | **🏠 Component**: [TAP LDAP](../README.md) | **Framework**: Singer SDK 0.35.0+ | **Updated**: 2025-06-19
