# 🧪 TAP LDAP - Test Suite

> **Module**: Comprehensive test suite for TAP LDAP with Singer SDK compliance and LDAP extraction testing | **Audience**: QA Engineers, LDAP Administrators, TAP Testing Specialists | **Status**: Production Ready

## 📋 **Overview**

Enterprise-grade test suite for the TAP LDAP implementation, providing comprehensive testing coverage including unit tests, integration tests with real LDAP directories, performance testing, and Singer SDK compliance validation. This test suite demonstrates best practices for testing Singer taps and LDAP data extraction operations.

---

## 🧭 **Navigation Context**

**🏠 Root**: [PyAuto Home](../../README.md) → **📂 Component**: [TAP LDAP](../README.md) → **📂 Current**: Test Suite

---

## 🎯 **Module Purpose**

This test module provides comprehensive validation for the TAP LDAP implementation, ensuring reliability, performance, and correctness of all LDAP data extraction operations, Singer SDK compliance, and enterprise LDAP directory integration workflows.

### **Key Testing Areas**

- **Unit Testing** - Core tap logic and LDAP client validation
- **Integration Testing** - End-to-end data extraction with real LDAP directories
- **Performance Testing** - LDAP search performance and throughput
- **Singer SDK Testing** - TAP compliance and specification validation
- **LDAP Authentication Testing** - LDAP bind and search validation
- **LDIF Processing Testing** - LDIF file processing and stream generation

---

## 📁 **Test Structure**

```
tests/
├── unit/
│   ├── test_tap_core.py                 # Core TAP functionality tests
│   ├── test_client_ldap.py              # LDAP client tests
│   ├── test_streams_validation.py       # Stream implementation tests
│   ├── test_ldif_processor.py           # LDIF processor tests
│   └── test_config_validation.py        # Configuration validation tests
├── integration/
│   ├── test_ldap_integration.py         # LDAP directory integration tests
│   ├── test_singer_compliance.py        # Singer SDK compliance tests
│   ├── test_data_extraction.py          # End-to-end data extraction tests
│   ├── test_schema_discovery.py         # LDAP schema discovery tests
│   └── test_incremental_extraction.py   # Incremental extraction tests
├── e2e/
│   ├── __init__.py                      # E2E test package initialization
│   ├── conftest.py                      # E2E specific fixtures
│   ├── test_tap_e2e.py                  # Complete end-to-end workflow tests
│   └── ldif/                            # LDIF test data
│       ├── 01-base.ldif                 # Base LDIF test data
│       ├── 02-users.ldif                # User entries test data
│       └── 03-groups.ldif               # Group entries test data
├── performance/
│   ├── test_search_performance.py       # LDAP search performance testing
│   ├── test_concurrent_extraction.py    # Concurrent extraction scenarios
│   ├── test_memory_optimization.py      # Memory usage optimization tests
│   └── test_scalability_limits.py       # LDAP scalability testing
├── singer/
│   ├── test_tap_compliance.py           # Singer TAP specification compliance
│   ├── test_catalog_generation.py       # Catalog generation validation
│   ├── test_state_management.py         # State management testing
│   └── test_record_processing.py        # Record processing tests
├── fixtures/
│   ├── ldap_fixtures.py                 # LDAP test data fixtures
│   ├── singer_fixtures.py               # Singer message test fixtures
│   └── ldif_fixtures.py                 # LDIF test data fixtures
├── conftest.py                           # Pytest configuration and fixtures
├── test_client.py                        # LDAP client tests
├── test_integration.py                   # Integration tests
├── test_ldif_processor.py                # LDIF processor tests
├── test_ldif_stream.py                   # LDIF stream tests
├── test_streams.py                       # Stream implementation tests
└── test_tap.py                           # Core TAP tests
```

---

## 🔧 **Test Categories**

### **1. Unit Tests (unit/)**

#### **Core TAP Testing (test_tap_core.py)**

```python
"""Unit tests for TAP LDAP core functionality."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
import json
from datetime import datetime

from tap_ldap.tap import TapLDAP
from tap_ldap.config import TapConfig
from tap_ldap.streams import LDAPStream
from tap_ldap.exceptions import (
    TapConfigurationError,
    LDAPConnectionError,
    DataExtractionError
)

class TestTapLDAP:
    """Test LDAP TAP core functionality."""

    @pytest.fixture
    def tap_config(self):
        """TAP configuration fixture."""
        return TapConfig(
            ldap_host="ldap://test-ldap.example.com",
            ldap_port=389,
            bind_dn="cn=readonly,dc=example,dc=com",
            bind_password="readonly_password",
            base_dn="dc=example,dc=com",
            search_scope="subtree",
            page_size=1000
        )

    @pytest.fixture
    def mock_ldap_client(self):
        """Mock LDAP client fixture."""
        client = Mock()
        client.bind.return_value = True
        client.search.return_value = [
            {"dn": "uid=user1,ou=users,dc=example,dc=com", "uid": ["user1"], "cn": ["User One"]},
            {"dn": "uid=user2,ou=users,dc=example,dc=com", "uid": ["user2"], "cn": ["User Two"]}
        ]
        return client

    @pytest.fixture
    def tap_instance(self, tap_config, mock_ldap_client):
        """TAP instance with mocked dependencies."""
        with patch('tap_ldap.tap.LDAPClient', return_value=mock_ldap_client):
            return TapLDAP(config=tap_config)

    def test_tap_initialization_success(self, tap_config):
        """Test successful TAP initialization."""
        # Act
        tap = TapLDAP(config=tap_config)

        # Assert
        assert tap.config == tap_config
        assert tap.name == "tap-ldap"
        assert tap.config.page_size == 1000

    def test_tap_initialization_invalid_config(self):
        """Test TAP initialization with invalid configuration."""
        # Arrange
        invalid_config = TapConfig(
            ldap_host="",  # Invalid empty host
            bind_dn="cn=readonly,dc=example,dc=com",
            bind_password="password"
        )

        # Act & Assert
        with pytest.raises(TapConfigurationError):
            TapLDAP(config=invalid_config)

    def test_discover_streams(self, tap_instance):
        """Test LDAP stream discovery."""
        # Act
        catalog = tap_instance.discover_streams()

        # Assert
        assert len(catalog.streams) > 0

        # Check for common LDAP object classes
        stream_names = [stream.tap_stream_id for stream in catalog.streams]
        assert "users" in stream_names or "inetOrgPerson" in stream_names

    def test_get_stream_for_object_class(self, tap_instance):
        """Test stream creation for specific object class."""
        # Arrange
        object_class = "inetOrgPerson"

        # Act
        stream = tap_instance.get_stream(object_class)

        # Assert
        assert isinstance(stream, LDAPStream)
        assert stream.object_class == object_class

    def test_connection_test(self, tap_instance, mock_ldap_client):
        """Test LDAP connection testing."""
        # Act
        result = tap_instance.test_connection()

        # Assert
        assert result is True
        mock_ldap_client.bind.assert_called_once()
```

#### **LDAP Client Testing (test_client_ldap.py)**

```python
"""Unit tests for LDAP client functionality."""

import pytest
from unittest.mock import Mock, patch
import ldap

from tap_ldap.client import LDAPClient
from tap_ldap.config import TapConfig
from tap_ldap.exceptions import LDAPConnectionError, LDAPSearchError

class TestLDAPClient:
    """Test LDAP client functionality."""

    @pytest.fixture
    def client_config(self):
        """LDAP client configuration fixture."""
        return TapConfig(
            ldap_host="ldap://test-ldap.example.com",
            ldap_port=389,
            bind_dn="cn=readonly,dc=example,dc=com",
            bind_password="readonly_password",
            base_dn="dc=example,dc=com",
            search_scope="subtree",
            use_ssl=False,
            timeout=30
        )

    @pytest.fixture
    def mock_ldap_connection(self):
        """Mock python-ldap connection."""
        connection = Mock()
        connection.simple_bind_s.return_value = None
        connection.search_ext_s.return_value = [
            ("uid=user1,ou=users,dc=example,dc=com", {"uid": [b"user1"], "cn": [b"User One"]}),
            ("uid=user2,ou=users,dc=example,dc=com", {"uid": [b"user2"], "cn": [b"User Two"]})
        ]
        return connection

    @pytest.fixture
    def ldap_client(self, client_config, mock_ldap_connection):
        """LDAP client instance with mocked connection."""
        with patch('ldap.initialize', return_value=mock_ldap_connection):
            return LDAPClient(config=client_config)

    def test_client_initialization(self, client_config):
        """Test LDAP client initialization."""
        # Act
        client = LDAPClient(config=client_config)

        # Assert
        assert client.config == client_config
        assert client.ldap_host == "ldap://test-ldap.example.com"
        assert client.ldap_port == 389

    def test_bind_success(self, ldap_client, mock_ldap_connection):
        """Test successful LDAP bind."""
        # Act
        result = ldap_client.bind()

        # Assert
        assert result is True
        mock_ldap_connection.simple_bind_s.assert_called_once_with(
            "cn=readonly,dc=example,dc=com",
            "readonly_password"
        )

    def test_bind_failure(self, ldap_client, mock_ldap_connection):
        """Test LDAP bind failure."""
        # Arrange
        mock_ldap_connection.simple_bind_s.side_effect = ldap.INVALID_CREDENTIALS("Invalid credentials")

        # Act & Assert
        with pytest.raises(LDAPConnectionError):
            ldap_client.bind()

    def test_search_success(self, ldap_client, mock_ldap_connection):
        """Test successful LDAP search."""
        # Arrange
        search_filter = "(objectClass=inetOrgPerson)"
        attributes = ["uid", "cn", "mail"]

        # Act
        results = ldap_client.search(
            base_dn="ou=users,dc=example,dc=com",
            search_filter=search_filter,
            attributes=attributes
        )

        # Assert
        assert len(results) == 2
        assert results[0]["dn"] == "uid=user1,ou=users,dc=example,dc=com"
        assert results[0]["uid"] == ["user1"]
        mock_ldap_connection.search_ext_s.assert_called_once()

    def test_search_with_pagination(self, ldap_client, mock_ldap_connection):
        """Test LDAP search with pagination."""
        # Arrange
        search_filter = "(objectClass=*)"
        page_size = 100

        # Mock paginated results
        mock_ldap_connection.search_ext_s.return_value = [
            ("uid=user1,ou=users,dc=example,dc=com", {"uid": [b"user1"]}),
            ("uid=user2,ou=users,dc=example,dc=com", {"uid": [b"user2"]})
        ]

        # Act
        results = ldap_client.search_paged(
            base_dn="dc=example,dc=com",
            search_filter=search_filter,
            page_size=page_size
        )

        # Assert
        assert len(list(results)) == 2

    def test_connection_ssl_configuration(self, client_config):
        """Test SSL connection configuration."""
        # Arrange
        client_config.use_ssl = True
        client_config.ldap_port = 636

        # Act & Assert
        with patch('ldap.initialize') as mock_init:
            client = LDAPClient(config=client_config)
            client.connect()

            # Verify SSL URI was used
            mock_init.assert_called_with("ldaps://test-ldap.example.com:636")

    def test_attribute_value_decoding(self, ldap_client):
        """Test LDAP attribute value decoding."""
        # Arrange
        raw_entry = {
            "dn": "uid=test,ou=users,dc=example,dc=com",
            "attributes": {
                "uid": [b"test"],
                "cn": [b"Test User"],
                "mail": [b"test@example.com"],
                "objectClass": [b"inetOrgPerson", b"organizationalPerson"]
            }
        }

        # Act
        decoded_entry = ldap_client.decode_entry(raw_entry)

        # Assert
        assert decoded_entry["uid"] == ["test"]
        assert decoded_entry["cn"] == ["Test User"]
        assert decoded_entry["mail"] == ["test@example.com"]
        assert "inetOrgPerson" in decoded_entry["objectClass"]
```

#### **LDIF Processor Testing (test_ldif_processor.py)**

```python
"""Unit tests for LDIF processor functionality."""

import pytest
import tempfile
import os
from pathlib import Path

from tap_ldap.ldif_processor import LDIFProcessor
from tap_ldap.exceptions import LDIFProcessingError

class TestLDIFProcessor:
    """Test LDIF file processing functionality."""

    @pytest.fixture
    def sample_ldif_content(self):
        """Sample LDIF content for testing."""
        return """dn: dc=example,dc=com
objectClass: top
objectClass: domain
dc: example

dn: ou=users,dc=example,dc=com
objectClass: top
objectClass: organizationalUnit
ou: users

dn: uid=john.doe,ou=users,dc=example,dc=com
objectClass: top
objectClass: person
objectClass: organizationalPerson
objectClass: inetOrgPerson
uid: john.doe
cn: John Doe
sn: Doe
givenName: John
mail: john.doe@example.com
userPassword:: cGFzc3dvcmQ=

dn: uid=jane.smith,ou=users,dc=example,dc=com
objectClass: top
objectClass: person
objectClass: organizationalPerson
objectClass: inetOrgPerson
uid: jane.smith
cn: Jane Smith
sn: Smith
givenName: Jane
mail: jane.smith@example.com
"""

    @pytest.fixture
    def ldif_file(self, sample_ldif_content):
        """Create temporary LDIF file for testing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ldif', delete=False) as f:
            f.write(sample_ldif_content)
            temp_file = f.name

        yield temp_file

        # Cleanup
        os.unlink(temp_file)

    @pytest.fixture
    def ldif_processor(self):
        """LDIF processor instance."""
        return LDIFProcessor()

    def test_parse_ldif_file_success(self, ldif_processor, ldif_file):
        """Test successful LDIF file parsing."""
        # Act
        entries = list(ldif_processor.parse_ldif_file(ldif_file))

        # Assert
        assert len(entries) == 4

        # Check first entry (domain)
        domain_entry = entries[0]
        assert domain_entry["dn"] == "dc=example,dc=com"
        assert "domain" in domain_entry["objectClass"]

        # Check user entry
        user_entries = [e for e in entries if "inetOrgPerson" in e.get("objectClass", [])]
        assert len(user_entries) == 2

        john_entry = next(e for e in user_entries if e["uid"] == ["john.doe"])
        assert john_entry["cn"] == ["John Doe"]
        assert john_entry["mail"] == ["john.doe@example.com"]

    def test_parse_ldif_file_not_found(self, ldif_processor):
        """Test LDIF file parsing with non-existent file."""
        # Act & Assert
        with pytest.raises(LDIFProcessingError):
            list(ldif_processor.parse_ldif_file("non_existent_file.ldif"))

    def test_base64_decoding(self, ldif_processor):
        """Test base64 encoded attribute decoding."""
        # Arrange
        ldif_content = """dn: uid=test,ou=users,dc=example,dc=com
uid: test
userPassword:: cGFzc3dvcmQ=
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.ldif', delete=False) as f:
            f.write(ldif_content)
            temp_file = f.name

        try:
            # Act
            entries = list(ldif_processor.parse_ldif_file(temp_file))

            # Assert
            assert len(entries) == 1
            entry = entries[0]
            assert entry["uid"] == ["test"]
            assert entry["userPassword"] == ["password"]  # base64 decoded
        finally:
            os.unlink(temp_file)

    def test_multi_value_attributes(self, ldif_processor):
        """Test handling of multi-value attributes."""
        # Arrange
        ldif_content = """dn: cn=group1,ou=groups,dc=example,dc=com
objectClass: top
objectClass: groupOfNames
cn: group1
member: uid=user1,ou=users,dc=example,dc=com
member: uid=user2,ou=users,dc=example,dc=com
member: uid=user3,ou=users,dc=example,dc=com
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.ldif', delete=False) as f:
            f.write(ldif_content)
            temp_file = f.name

        try:
            # Act
            entries = list(ldif_processor.parse_ldif_file(temp_file))

            # Assert
            assert len(entries) == 1
            entry = entries[0]
            assert len(entry["member"]) == 3
            assert "uid=user1,ou=users,dc=example,dc=com" in entry["member"]
        finally:
            os.unlink(temp_file)

    def test_filter_by_object_class(self, ldif_processor, ldif_file):
        """Test filtering entries by object class."""
        # Act
        user_entries = list(ldif_processor.parse_ldif_file(
            ldif_file,
            object_class_filter="inetOrgPerson"
        ))

        # Assert
        assert len(user_entries) == 2
        for entry in user_entries:
            assert "inetOrgPerson" in entry["objectClass"]

    def test_convert_to_singer_records(self, ldif_processor, ldif_file):
        """Test conversion of LDIF entries to Singer records."""
        # Act
        entries = list(ldif_processor.parse_ldif_file(ldif_file))
        singer_records = [ldif_processor.to_singer_record(entry) for entry in entries]

        # Assert
        assert len(singer_records) == 4

        # Check Singer record structure
        user_record = next(r for r in singer_records if r.get("uid") == "john.doe")
        assert user_record["dn"] == "uid=john.doe,ou=users,dc=example,dc=com"
        assert user_record["cn"] == "John Doe"
        assert user_record["mail"] == "john.doe@example.com"

        # Verify single-value attributes are strings, not lists
        assert isinstance(user_record["uid"], str)
        assert isinstance(user_record["cn"], str)
```

### **2. Integration Tests (integration/)**

#### **LDAP Integration Testing (test_ldap_integration.py)**

```python
"""Integration tests for LDAP directory integration."""

import pytest
import asyncio
from unittest.mock import patch, Mock

from tap_ldap.tap import TapLDAP
from tap_ldap.config import TapConfig

@pytest.mark.integration
class TestLDAPIntegration:
    """Test LDAP directory integration scenarios."""

    @pytest.fixture
    def integration_config(self):
        """Integration test configuration."""
        return TapConfig(
            ldap_host="ldap://test-ldap.example.com",
            ldap_port=389,
            bind_dn="cn=readonly,dc=example,dc=com",
            bind_password="integration_test_password",
            base_dn="dc=example,dc=com",
            search_scope="subtree",
            page_size=100
        )

    @pytest.fixture
    async def tap_with_auth(self, integration_config):
        """TAP instance with authenticated LDAP client."""
        tap = TapLDAP(config=integration_config)

        # Mock successful authentication
        with patch.object(tap.ldap_client, 'bind') as mock_bind:
            mock_bind.return_value = True
            tap.ldap_client.bind()

        return tap

    @pytest.mark.asyncio
    async def test_end_to_end_user_extraction(self, tap_with_auth):
        """Test end-to-end user data extraction from LDAP."""
        # Mock LDAP search results
        mock_user_results = [
            {
                "dn": "uid=john.doe,ou=users,dc=example,dc=com",
                "uid": ["john.doe"],
                "cn": ["John Doe"],
                "sn": ["Doe"],
                "givenName": ["John"],
                "mail": ["john.doe@example.com"],
                "objectClass": ["inetOrgPerson", "organizationalPerson", "person"]
            },
            {
                "dn": "uid=jane.smith,ou=users,dc=example,dc=com",
                "uid": ["jane.smith"],
                "cn": ["Jane Smith"],
                "sn": ["Smith"],
                "givenName": ["Jane"],
                "mail": ["jane.smith@example.com"],
                "objectClass": ["inetOrgPerson", "organizationalPerson", "person"]
            }
        ]

        with patch.object(tap_with_auth.ldap_client, 'search') as mock_search:
            mock_search.return_value = mock_user_results

            # Act
            catalog = tap_with_auth.discover_streams()
            user_stream = next(s for s in catalog.streams if "user" in s.tap_stream_id.lower())

            records = []
            for record in tap_with_auth.sync_stream(user_stream):
                records.append(record)

            # Assert
            assert len(records) >= 2

            # Check extracted user data
            john_record = next(r for r in records if r.get("uid") == "john.doe")
            assert john_record["cn"] == "John Doe"
            assert john_record["mail"] == "john.doe@example.com"

    @pytest.mark.asyncio
    async def test_schema_discovery_performance(self, tap_with_auth):
        """Test schema discovery performance with large directories."""
        # Mock large directory structure
        mock_schema_results = [
            {"dn": f"ou=department{i},dc=example,dc=com", "objectClass": ["organizationalUnit"]}
            for i in range(1000)
        ]

        with patch.object(tap_with_auth.ldap_client, 'search') as mock_search:
            mock_search.return_value = mock_schema_results

            # Act
            import time
            start_time = time.time()

            catalog = tap_with_auth.discover_streams()

            end_time = time.time()
            discovery_time = end_time - start_time

            # Assert
            assert len(catalog.streams) > 0
            assert discovery_time < 10.0  # Should discover schema in under 10 seconds
            mock_search.assert_called()

    @pytest.mark.asyncio
    async def test_incremental_extraction(self, tap_with_auth):
        """Test incremental data extraction based on modify timestamp."""
        # Mock entries with timestamps
        mock_results = [
            {
                "dn": "uid=user1,ou=users,dc=example,dc=com",
                "uid": ["user1"],
                "modifyTimestamp": ["20250619100000Z"],
                "objectClass": ["inetOrgPerson"]
            },
            {
                "dn": "uid=user2,ou=users,dc=example,dc=com",
                "uid": ["user2"],
                "modifyTimestamp": ["20250619110000Z"],
                "objectClass": ["inetOrgPerson"]
            }
        ]

        with patch.object(tap_with_auth.ldap_client, 'search') as mock_search:
            mock_search.return_value = mock_results

            # Act - Simulate incremental extraction
            state = {"bookmarks": {"users": {"modifyTimestamp": "20250619105000Z"}}}
            tap_with_auth.load_state(state)

            catalog = tap_with_auth.discover_streams()
            user_stream = next(s for s in catalog.streams if "user" in s.tap_stream_id.lower())

            records = list(tap_with_auth.sync_stream(user_stream))

            # Assert - Should only extract records modified after bookmark
            assert len(records) == 1
            assert records[0]["uid"] == "user2"
            assert records[0]["modifyTimestamp"] == "20250619110000Z"
```

---

## 🔧 **Test Configuration**

### **Pytest Configuration (conftest.py)**

```python
"""Pytest configuration and shared fixtures for TAP LDAP tests."""

import pytest
import asyncio
import os
from unittest.mock import Mock, patch
import tempfile

from tap_ldap.config import TapConfig
from tap_ldap.tap import TapLDAP

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def test_config():
    """Test configuration fixture."""
    return TapConfig(
        ldap_host=os.getenv("TEST_LDAP_HOST", "ldap://test-ldap.example.com"),
        ldap_port=int(os.getenv("TEST_LDAP_PORT", "389")),
        bind_dn=os.getenv("TEST_BIND_DN", "cn=readonly,dc=example,dc=com"),
        bind_password=os.getenv("TEST_BIND_PASSWORD", "readonly_password"),
        base_dn=os.getenv("TEST_BASE_DN", "dc=example,dc=com"),
        search_scope="subtree",
        page_size=1000
    )

@pytest.fixture
def mock_ldap_client():
    """Mock LDAP client."""
    client = Mock()
    client.bind.return_value = True
    client.search.return_value = [
        {
            "dn": "uid=test1,ou=users,dc=example,dc=com",
            "uid": ["test1"],
            "cn": ["Test User 1"],
            "objectClass": ["inetOrgPerson"]
        }
    ]
    return client

@pytest.fixture
def tap_instance(test_config, mock_ldap_client):
    """TAP instance with mocked LDAP client."""
    with patch('tap_ldap.tap.LDAPClient', return_value=mock_ldap_client):
        return TapLDAP(config=test_config)

@pytest.fixture
def sample_ldap_entries():
    """Sample LDAP entries for testing."""
    return [
        {
            "dn": "uid=john.doe,ou=users,dc=example,dc=com",
            "uid": ["john.doe"],
            "cn": ["John Doe"],
            "sn": ["Doe"],
            "givenName": ["John"],
            "mail": ["john.doe@example.com"],
            "objectClass": ["inetOrgPerson", "organizationalPerson", "person"]
        },
        {
            "dn": "uid=jane.smith,ou=users,dc=example,dc=com",
            "uid": ["jane.smith"],
            "cn": ["Jane Smith"],
            "sn": ["Smith"],
            "givenName": ["Jane"],
            "mail": ["jane.smith@example.com"],
            "objectClass": ["inetOrgPerson", "organizationalPerson", "person"]
        }
    ]

@pytest.fixture
def sample_ldif_file():
    """Sample LDIF file for testing."""
    ldif_content = """dn: dc=example,dc=com
objectClass: top
objectClass: domain
dc: example

dn: uid=john.doe,ou=users,dc=example,dc=com
objectClass: top
objectClass: person
objectClass: organizationalPerson
objectClass: inetOrgPerson
uid: john.doe
cn: John Doe
sn: Doe
mail: john.doe@example.com
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.ldif', delete=False) as f:
        f.write(ldif_content)
        temp_file = f.name

    yield temp_file

    # Cleanup
    os.unlink(temp_file)

@pytest.fixture
def singer_catalog():
    """Sample Singer catalog for testing."""
    return {
        "streams": [
            {
                "tap_stream_id": "users",
                "schema": {
                    "type": "object",
                    "properties": {
                        "dn": {"type": "string"},
                        "uid": {"type": "string"},
                        "cn": {"type": "string"},
                        "mail": {"type": "string"}
                    }
                },
                "metadata": [
                    {
                        "breadcrumb": [],
                        "metadata": {
                            "inclusion": "automatic",
                            "selected": True
                        }
                    }
                ]
            }
        ]
    }
```

---

## 🔗 **Cross-References**

### **Component Documentation**

- [Component Overview](../README.md) - Complete TAP LDAP documentation
- [Source Implementation](../src/README.md) - Source code structure and patterns
- [Configuration Guide](../docker-compose.yml) - Docker configuration examples

### **Testing Documentation**

- [Singer SDK Testing](https://sdk.meltano.com/en/latest/testing.html) - Singer SDK testing guidelines
- [PyTest Documentation](https://docs.pytest.org/) - Python testing framework
- [LDAP Testing Best Practices](https://ldapwiki.com/wiki/LDAP%20Testing) - LDAP testing patterns

### **LDAP References**

- [LDAP Protocol Documentation](https://ldapwiki.com/wiki/LDAP%20Protocol) - LDAP protocol reference
- [Python LDAP Documentation](https://python-ldap.readthedocs.io/) - Python LDAP library
- [LDIF Format Specification](https://tools.ietf.org/html/rfc2849) - LDIF format reference

---

**📂 Module**: Test Suite | **🏠 Component**: [TAP LDAP](../README.md) | **Framework**: PyTest 7.0+ | **Updated**: 2025-06-19
