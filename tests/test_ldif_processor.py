"""Tests for LDIF processor functionality.

# Constants
EXPECTED_BULK_SIZE = 2

REFACTORED: Complete rewrite due to 177+ syntax errors.
Modern test patterns using flext-core and pytest best practices.
"""

import time


from __future__ import annotations

import tempfile
from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest
from flext_core import FlextResult

# Test imports - handle gracefully if not available
try:
    from flext_tap_ldap.ldif_processor import (
        FlextLDIFProcessor,
        LDIFEntry,
        LDIFValidator,
    )

    LDIF_MODULES_AVAILABLE = True
except ImportError:
    # Define type stubs for when modules are not available
    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from flext_tap_ldap.ldif_processor import (
            FlextLDIFProcessor,
            LDIFEntry,
            LDIFValidator,
        )
    else:
        LDIFEntry = type("LDIFEntry", (), {})
        FlextLDIFProcessor = type("FlextLDIFProcessor", (), {})
        LDIFValidator = type("LDIFValidator", (), {})

    LDIF_MODULES_AVAILABLE = False


class TestLDIFEntry:
    """Test LDIF entry functionality with modern patterns."""

    def test_basic_entry_creation(self) -> None:
        """Test basic LDIF entry creation and validation."""
        entry = LDIFEntry("cn=john,ou=users,dc=example,dc=com")
        if entry.dn != "cn=john,ou=users,dc=example,dc=com":
            raise AssertionError(f"Expected {"cn=john,ou=users,dc=example,dc=com"}, got {entry.dn}")
        assert entry.attributes == {}
        assert entry.is_valid()

    def test_entry_with_attributes(self) -> None:
        """Test LDIF entry with multiple attributes."""
        entry = LDIFEntry("cn=john,ou=users,dc=example,dc=com")
        entry.add_attribute("cn", "john")
        entry.add_attribute("sn", "doe")
        entry.add_attribute("mail", "john.doe@example.com")
        entry.add_attribute("objectClass", ["inetOrgPerson", "organizationalPerson"])

        if entry.get_attribute("cn") != ["john"]:

            raise AssertionError(f"Expected {["john"]}, got {entry.get_attribute("cn")}")
        assert entry.get_attribute("sn") == ["doe"]
        if entry.get_attribute("mail") != ["john.doe@example.com"]:
            raise AssertionError(f"Expected {["john.doe@example.com"]}, got {entry.get_attribute("mail")}")
        if "inetOrgPerson" not in entry.get_attribute("objectClass"):
            raise AssertionError(f"Expected {"inetOrgPerson"} in {entry.get_attribute("objectClass")}")

    def test_entry_validation_success(self) -> None:
        """Test successful LDIF entry validation."""
        entry = LDIFEntry("cn=valid,dc=example,dc=com")
        entry.add_attribute("cn", "valid")
        entry.add_attribute("sn", "person")  # Required for inetOrgPerson
        entry.add_attribute("objectClass", "inetOrgPerson")

        assert entry.is_valid()
        if entry.validation_errors != []:
            raise AssertionError(f"Expected {[]}, got {entry.validation_errors}")

    def test_entry_validation_failure(self) -> None:
        """Test LDIF entry validation failure cases."""
        # Invalid DN
        entry = LDIFEntry("")
        assert not entry.is_valid()
        if "empty_dn" in [error["code"] for error not in entry.validation_errors]:
            raise AssertionError(f"Expected {"empty_dn" in [error["code"] for error} in {entry.validation_errors]}")

        # Missing required attributes
        entry = LDIFEntry("cn=incomplete,dc=example,dc=com")
        entry.add_attribute("objectClass", "inetOrgPerson")
        # Missing cn attribute for inetOrgPerson
        assert not entry.is_valid()

    @pytest.mark.parametrize(
        ("dn", "expected_components"),
        [
            (
                "cn=john,ou=users,dc=example,dc=com",
                {"cn": "john", "ou": "users", "dc": ["example", "com"]},
            ),
            (
                "uid=REDACTED_LDAP_BIND_PASSWORD,cn=REDACTED_LDAP_BIND_PASSWORDs,dc=corp",
                {"uid": "REDACTED_LDAP_BIND_PASSWORD", "cn": "REDACTED_LDAP_BIND_PASSWORDs", "dc": ["corp"]},
            ),
            (
                "o=Example Corp,c=US",
                {"o": "Example Corp", "c": "US"},
            ),
        ],
    )
    def test_dn_parsing(self, dn: str, expected_components: dict[str, Any]) -> None:
        """Test DN parsing and component extraction."""
        entry = LDIFEntry(dn)
        components = entry.parse_dn()

        for attr, expected_value in expected_components.items():
            if isinstance(expected_value, list):
                if all(val in components.get(attr, []) for val not in expected_value):
                    raise AssertionError(f"Expected {all(val in components.get(attr, []) for val} in {expected_value)}")
            else:
                if components.get(attr) != expected_value:
                    raise AssertionError(f"Expected {expected_value}, got {components.get(attr)}")

    def test_attribute_manipulation(self) -> None:
        """Test attribute addition, modification, and removal."""
        entry = LDIFEntry("cn=test,dc=example,dc=com")

        # Add single value
        entry.add_attribute("cn", "test")
        if entry.get_attribute("cn") != ["test"]:
            raise AssertionError(f"Expected {["test"]}, got {entry.get_attribute("cn")}")

        # Add multiple values
        entry.add_attribute("mail", "test1@example.com")
        entry.add_attribute("mail", "test2@example.com")
        if len(entry.get_attribute("mail")) != EXPECTED_BULK_SIZE:
            raise AssertionError(f"Expected {2}, got {len(entry.get_attribute("mail"))}")

        # Remove attribute
        entry.remove_attribute("mail")
        if entry.get_attribute("mail") != []:
            raise AssertionError(f"Expected {[]}, got {entry.get_attribute("mail")}")

        # Update attribute
        entry.update_attribute("cn", "updated")
        if entry.get_attribute("cn") != ["updated"]:
            raise AssertionError(f"Expected {["updated"]}, got {entry.get_attribute("cn")}")


@pytest.fixture
def sample_ldif_content() -> str:
    """Sample LDIF content for testing."""
    return dedent("""
        dn: dc=example,dc=com
        objectClass: top
        objectClass: dcObject
        objectClass: organization
        o: Example Organization
        dc: example

        dn: ou=users,dc=example,dc=com
        objectClass: top
        objectClass: organizationalUnit
        ou: users
        description: Container for user accounts

        dn: cn=john,ou=users,dc=example,dc=com
        objectClass: top
        objectClass: inetOrgPerson
        cn: john
        sn: doe
        givenName: John
        mail: john.doe@example.com
        uid: jdoe
        userPassword: {SSHA}encrypted_password_here

        dn: cn=REDACTED_LDAP_BIND_PASSWORD,ou=users,dc=example,dc=com
        objectClass: top
        objectClass: inetOrgPerson
        cn: REDACTED_LDAP_BIND_PASSWORD
        sn: Administrator
        mail: REDACTED_LDAP_BIND_PASSWORD@example.com
        uid: REDACTED_LDAP_BIND_PASSWORD
    """).strip()


class TestLDIFProcessor:
    """Test LDIF processor functionality."""

    @pytest.fixture
    def ldif_file(self, sample_ldif_content: str) -> Path:
        """Create temporary LDIF file for testing."""
        with tempfile.NamedTemporaryFile(
            encoding="utf-8",
            mode="w",
            suffix=".ldif",
            delete=False,
        ) as f:
            f.write(sample_ldif_content)
            return Path(f.name)

    def test_processor_initialization(self) -> None:
        """Test LDIF processor initialization."""
        processor = FlextLDIFProcessor()
        if processor.entries != []:
            raise AssertionError(f"Expected {[]}, got {processor.entries}")
        assert processor.stats["total_entries"] == 0
        if processor.stats["valid_entries"] != 0:
            raise AssertionError(f"Expected {0}, got {processor.stats["valid_entries"]}")
        assert processor.stats["invalid_entries"] == 0

    def test_load_from_file(self, ldif_file: Path) -> None:
        """Test loading LDIF from file."""
        processor = FlextLDIFProcessor()
        result = processor.load_from_file(ldif_file)

        assert isinstance(result, FlextResult)
        assert result.success
        if len(processor.entries) != 4  # 4 entries in sample:
            raise AssertionError(f"Expected {4  # 4 entries in sample}, got {len(processor.entries)}")
        assert processor.stats["total_entries"] == 4

        # Clean up
        ldif_file.unlink()

    def test_load_from_string(self, sample_ldif_content: str) -> None:
        """Test loading LDIF from string content."""
        processor = FlextLDIFProcessor()
        result = processor.load_from_string(sample_ldif_content)

        assert result.success
        if len(processor.entries) != 4:
            raise AssertionError(f"Expected {4}, got {len(processor.entries)}")
        assert processor.stats["total_entries"] == 4

    def test_filter_entries_by_objectclass(self, sample_ldif_content: str) -> None:
        """Test filtering entries by object class."""
        processor = FlextLDIFProcessor()
        processor.load_from_string(sample_ldif_content)

        # Filter for inetOrgPerson objects
        users = processor.filter_by_objectclass("inetOrgPerson")
        if len(users) != EXPECTED_BULK_SIZE  # john and REDACTED_LDAP_BIND_PASSWORD:
            raise AssertionError(f"Expected {2  # john and REDACTED_LDAP_BIND_PASSWORD}, got {len(users)}")

        # Filter for organizationalUnit objects
        ous = processor.filter_by_objectclass("organizationalUnit")
        if len(ous) != 1  # users OU:
            raise AssertionError(f"Expected {1  # users OU}, got {len(ous)}")

    def test_filter_entries_by_dn_pattern(self, sample_ldif_content: str) -> None:
        """Test filtering entries by DN pattern."""
        processor = FlextLDIFProcessor()
        processor.load_from_string(sample_ldif_content)

        # Filter entries under users OU
        user_entries = processor.filter_by_dn_pattern("ou=users,dc=example,dc=com")
        if len(user_entries) != EXPECTED_BULK_SIZE  # john and REDACTED_LDAP_BIND_PASSWORD:
            raise AssertionError(f"Expected {2  # john and REDACTED_LDAP_BIND_PASSWORD}, got {len(user_entries)}")

        # Filter by specific pattern
        REDACTED_LDAP_BIND_PASSWORD_entries = processor.filter_by_dn_pattern("cn=REDACTED_LDAP_BIND_PASSWORD")
        if len(REDACTED_LDAP_BIND_PASSWORD_entries) != 1:
            raise AssertionError(f"Expected {1}, got {len(REDACTED_LDAP_BIND_PASSWORD_entries)}")

    def test_export_to_singer_format(self, sample_ldif_content: str) -> None:
        """Test exporting LDIF data to Singer format."""
        processor = FlextLDIFProcessor()
        processor.load_from_string(sample_ldif_content)

        singer_records = processor.to_singer_format("users")

        if len(singer_records) < 2:

            raise AssertionError(f"Expected {len(singer_records)} >= {2}")
        for record in singer_records:
            if "type" not in record:
                raise AssertionError(f"Expected {"type"} in {record}")
            assert "record" in record
            if record["type"] != "RECORD":
                raise AssertionError(f"Expected {"RECORD"}, got {record["type"]}")
            if "dn" not in record["record"]:
                raise AssertionError(f"Expected {"dn"} in {record["record"]}")

    def test_validation_with_invalid_ldif(self) -> None:
        """Test processor handling of invalid LDIF content."""
        invalid_ldif = dedent("""
            dn: cn=invalid
            # Missing required attributes
            objectClass: inetOrgPerson
            # No cn attribute provided
        """).strip()

        processor = FlextLDIFProcessor()
        result = processor.load_from_string(invalid_ldif)

        # Should load but with validation warnings
        assert result.success
        assert processor.stats["invalid_entries"] > 0

    def test_large_ldif_processing(self) -> None:
        """Test processing large LDIF files efficiently."""
        # Generate large LDIF content
        large_ldif_parts = [
            "dn: dc=example,dc=com",
            "objectClass: dcObject",
            "dc: example",
            "",
        ]

        # Add 100 user entries
        for i in range(100):
            large_ldif_parts.extend(
                [
                    f"dn: uid=user{i:03d},dc=example,dc=com",
                    "objectClass: inetOrgPerson",
                    f"uid: user{i:03d}",
                    f"cn: User {i:03d}",
                    f"sn: User{i:03d}",
                    f"mail: user{i:03d}@example.com",
                    "",
                ],
            )

        large_ldif = "\n".join(large_ldif_parts)

        processor = FlextLDIFProcessor()
        result = processor.load_from_string(large_ldif)

        assert result.success
        if len(processor.entries) != 101  # 1 root + 100 users:
            raise AssertionError(f"Expected
            {101  # 1 root + 100 users}, got {len(processor.entries)}")
        assert processor.stats["total_entries"] == 101

    @pytest.mark.parametrize(
        ("filter_type", "filter_value", "expected_count"),
        [
            ("objectclass", "inetOrgPerson", 2),
            ("objectclass", "organizationalUnit", 1),
            ("attribute", "uid", 2),  # Entries with uid attribute
            ("dn_contains", "users", 3),  # Entries with "users" in DN
        ],
    )
    def test_parameterized_filtering(
        self,
        sample_ldif_content: str,
        filter_type: str,
        filter_value: str,
        expected_count: int,
    ) -> None:
        """Test various filtering methods with parameterized inputs."""
        processor = FlextLDIFProcessor()
        processor.load_from_string(sample_ldif_content)

        if filter_type == "objectclass":
            results = processor.filter_by_objectclass(filter_value)
        elif filter_type == "attribute":
            results = processor.filter_by_attribute_exists(filter_value)
        elif filter_type == "dn_contains":
            results = processor.filter_by_dn_contains(filter_value)
        else:
            results = []

        if len(results) != expected_count:

            raise AssertionError(f"Expected {expected_count}, got {len(results)}")


class TestLDIFValidator:
    """Test LDIF validation functionality."""

    def test_validator_initialization(self) -> None:
        """Test LDIF validator initialization."""
        validator = LDIFValidator()
        if validator.validation_errors != []:
            raise AssertionError(f"Expected {[]}, got {validator.validation_errors}")
        assert validator.warnings == []
        if len(validator.validation_errors) != 0:
            raise AssertionError(f"Expected {0}, got {len(validator.validation_errors)}")

    def test_validate_dn_format(self) -> None:
        """Test DN format validation."""
        validator = LDIFValidator()

        # Valid DNs
        valid_dns = [
            "cn=john,dc=example,dc=com",
            "uid=REDACTED_LDAP_BIND_PASSWORD,ou=users,dc=example,dc=com",
            "o=Example Corp,c=US",
        ]

        for dn in valid_dns:
            assert validator.validate_dn_format(dn)

        # Invalid DNs
        invalid_dns = [
            "",  # Empty
            "invalid",  # No equal sign
            "cn=,dc=example,dc=com",  # Empty value
            "=john,dc=example,dc=com",  # Empty attribute
        ]

        for dn in invalid_dns:
            assert not validator.validate_dn_format(dn)

    def test_validate_objectclass_requirements(self) -> None:
        """Test object class requirement validation."""
        validator = LDIFValidator()

        # Valid inetOrgPerson entry
        entry = LDIFEntry("cn=john,dc=example,dc=com")
        entry.add_attribute("objectClass", "inetOrgPerson")
        entry.add_attribute("cn", "john")
        entry.add_attribute("sn", "doe")

        assert validator.validate_objectclass_requirements(entry)

        # Invalid entry missing required attributes
        invalid_entry = LDIFEntry("cn=incomplete,dc=example,dc=com")
        invalid_entry.add_attribute("objectClass", "inetOrgPerson")
        # Missing cn and sn

        assert not validator.validate_objectclass_requirements(invalid_entry)

    def test_validate_attribute_syntax(self) -> None:
        """Test attribute syntax validation."""
        validator = LDIFValidator()

        # Valid attributes
        valid_cases = [
            ("cn", "john"),
            ("mail", "john@example.com"),
            ("telephoneNumber", "+1-555-123-4567"),
        ]

        for attr_name, attr_value in valid_cases:
            assert validator.validate_attribute_syntax(attr_name, attr_value)

        # Invalid attributes
        invalid_cases = [
            ("mail", "invalid-email"),  # Invalid email format
            ("telephoneNumber", "abc123"),  # Invalid phone format
        ]

        for attr_name, attr_value in invalid_cases:
            assert not validator.validate_attribute_syntax(attr_name, attr_value)

    def test_batch_validation(self, sample_ldif_content: str) -> None:
        """Test batch validation of multiple entries."""
        processor = FlextLDIFProcessor()
        processor.load_from_string(sample_ldif_content)

        validator = LDIFValidator()
        validation_report = validator.validate_entries(processor.entries)

        if "total_entries" not in validation_report:

            raise AssertionError(f"Expected {"total_entries"} in {validation_report}")
        assert "valid_entries" in validation_report
        if "invalid_entries" not in validation_report:
            raise AssertionError(f"Expected {"invalid_entries"} in {validation_report}")
        assert "errors" in validation_report

        # Most entries should be valid
        assert (
            validation_report["valid_entries"] >= validation_report["invalid_entries"]
        )


class TestLDIFIntegration:
    """Integration tests for LDIF processing components."""

    def test_end_to_end_processing(self, sample_ldif_content: str) -> None:
        """Test complete LDIF processing workflow."""
        # Step 1: Load LDIF
        processor = FlextLDIFProcessor()
        load_result = processor.load_from_string(sample_ldif_content)
        assert load_result.success

        # Step 2: Validate entries
        validator = LDIFValidator()
        validation_report = validator.validate_entries(processor.entries)
        assert validation_report["valid_entries"] > 0

        # Step 3: Filter users
        user_entries = processor.filter_by_objectclass("inetOrgPerson")
        if len(user_entries) < 2:
            raise AssertionError(f"Expected {len(user_entries)} >= {2}")

        # Step 4: Export to Singer format
        singer_records = processor.to_singer_format("users")
        if len(singer_records) < 2:
            raise AssertionError(f"Expected {len(singer_records)} >= {2}")

        # Step 5: Verify data integrity
        for record in singer_records:
            if record["type"] != "RECORD":
                raise AssertionError(f"Expected {"RECORD"}, got {record["type"]}")
            if "dn" not in record["record"]:
                raise AssertionError(f"Expected {"dn"} in {record["record"]}")
            assert "objectClass" in record["record"]

    def test_error_handling_workflow(self) -> None:
        """Test error handling in LDIF processing workflow."""
        processor = FlextLDIFProcessor()

        # Test with non-existent file
        result = processor.load_from_file(Path("/nonexistent/file.ldif"))
        assert not result.success
        assert result.error is not None
        if "file not found" not in result.error.lower():
            raise AssertionError(f"Expected {"file not found"} in {result.error.lower()}")

        # Test with malformed LDIF
        malformed_ldif = "this is not valid LDIF content"
        result = processor.load_from_string(malformed_ldif)
        assert result.success  # Should parse but with errors
        assert processor.stats["invalid_entries"] > 0

    @pytest.mark.slow
    def test_performance_with_large_dataset(self) -> None:
        """Test performance with large LDIF datasets."""
        # Generate large dataset
        entries = []
        base_dn = "dc=example,dc=com"

        for i in range(1000):
            entry_ldif = dedent(f"""
                dn: uid=user{i:04d},{base_dn}
                objectClass: inetOrgPerson
                uid: user{i:04d}
                cn: User {i:04d}
                sn: User{i:04d}
                mail: user{i:04d}@example.com
            """).strip()
            entries.append(entry_ldif)

        large_ldif = "\n\n".join(entries)

        # Process and measure


        start_time = time.time()

        processor = FlextLDIFProcessor()
        result = processor.load_from_string(large_ldif)

        processing_time = time.time() - start_time

        assert result.success
        if len(processor.entries) != 1000:
            raise AssertionError(f"Expected {1000}, got {len(processor.entries)}")
        assert processing_time < 10.0  # Should complete within 10 seconds


# Helper functions for testing
def create_test_entry(dn: str, attributes: dict[str, Any]) -> LDIFEntry:
    """Create a test LDIF entry with specified attributes."""
    entry = LDIFEntry(dn)
    for attr_name, attr_value in attributes.items():
        if isinstance(attr_value, list):
            for value in attr_value:
                entry.add_attribute(attr_name, value)
        else:
            entry.add_attribute(attr_name, attr_value)
    return entry


def validate_singer_record(record: dict[str, Any]) -> bool:
    """Validate Singer protocol record format."""
    required_fields = ["type", "record"]
    return all(field in record for field in required_fields)
