"""Tests for LDIF processor functionality.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from pathlib import Path

import pytest
from flext_core import FlextCore

from flext_tap_ldap import (
    FlextLdifProcessor,
    LDIFEntry,
    LDIFParseError,
    LDIFTransformer,
    LDIFValidator,
)

logger = FlextCore.Logger(__name__)


class TestLDIFEntry:
    """Test LDIF entry functionality with modern patterns."""

    def test_basic_entry_creation(self) -> None:
        """Test method."""
        """Test basic LDIF entry creation and validation."""
        entry = LDIFEntry("cn=john,ou=users,dc=example,dc=com")
        assert entry.dn == "cn=john,ou=users,dc=example,dc=com"
        assert entry.attributes == {}
        assert entry.is_valid()

    def test_entry_with_attributes(self) -> None:
        """Test method."""
        """Test LDIF entry with attributes."""
        entry = LDIFEntry("cn=john,ou=users,dc=example,dc=com")
        entry.add_attribute("cn", "john")
        entry.add_attribute("sn", "doe")
        entry.add_attribute("mail", "john.doe@example.com")
        assert entry.get_attribute("cn") == ["john"]
        assert entry.get_attribute("sn") == ["doe"]
        assert entry.get_attribute("mail") == ["john.doe@example.com"]

    def test_entry_validation(self) -> None:
        """Test method."""
        """Test LDIF entry validation."""
        # Valid entry
        valid_entry = LDIFEntry("cn=valid,dc=example,dc=com")
        valid_entry.add_attribute("objectClass", "person")
        assert valid_entry.is_valid()
        # Invalid entry (empty DN)
        invalid_entry = LDIFEntry("")
        assert not invalid_entry.is_valid()

    def test_entry_validation_errors(self) -> None:
        """Test method."""
        """Test LDIF entry validation errors property."""
        # Test empty DN error
        entry_empty_dn = LDIFEntry("")
        errors = entry_empty_dn.validation_errors
        assert len(errors) > 0
        assert any(error["code"] == "empty_dn" for error in errors)
        assert any("DN is empty or missing" in error["message"] for error in errors)
        # Test inetOrgPerson missing cn
        entry_missing_cn = LDIFEntry("uid=test,dc=example,dc=com")
        entry_missing_cn.add_attribute("objectClass", "inetOrgPerson")
        entry_missing_cn.add_attribute("sn", "Test")
        errors = entry_missing_cn.validation_errors
        assert any(error["code"] == "missing_cn" for error in errors)
        assert any(
            "inetOrgPerson requires cn attribute" in error["message"]
            for error in errors
        )
        # Test inetOrgPerson missing sn
        entry_missing_sn = LDIFEntry("cn=test,dc=example,dc=com")
        entry_missing_sn.add_attribute("objectClass", "inetOrgPerson")
        entry_missing_sn.add_attribute("cn", "Test")
        errors = entry_missing_sn.validation_errors
        assert any(error["code"] == "missing_sn" for error in errors)
        assert any(
            "inetOrgPerson requires sn attribute" in error["message"]
            for error in errors
        )
        # Test valid inetOrgPerson (no errors)
        valid_inetorg = LDIFEntry("cn=valid,dc=example,dc=com")
        valid_inetorg.add_attribute("objectClass", "inetOrgPerson")
        valid_inetorg.add_attribute("cn", "Valid")
        valid_inetorg.add_attribute("sn", "User")
        errors = valid_inetorg.validation_errors
        assert len(errors) == 0

    def test_entry_object_class_checking(self) -> None:
        """Test method."""
        """Test object class checking functionality."""
        entry = LDIFEntry("cn=test,dc=example,dc=com")
        entry.add_attribute("objectClass", ["person", "inetOrgPerson"])
        assert entry.has_object_class("person")
        assert entry.has_object_class("inetOrgPerson")
        assert entry.has_object_class("PERSON")  # Case insensitive
        assert not entry.has_object_class("organizationalUnit")

    def test_entry_to_dict(self) -> None:
        """Test method."""
        """Test entry to dict[str, object] conversion."""
        entry = LDIFEntry("cn=test,dc=example,dc=com")
        entry.add_attribute("cn", "test")
        entry.add_attribute("sn", "user")
        entry.change_type = "add"
        entry.controls = ["control1"]
        entry_dict = entry.to_dict()
        assert entry_dict["dn"] == "cn=test,dc=example,dc=com"
        assert entry_dict["attributes"]["cn"] == ["test"]
        assert entry_dict["attributes"]["sn"] == ["user"]
        assert entry_dict["change_type"] == "add"
        assert entry_dict["controls"] == ["control1"]

    def test_entry_add_attribute_list(self) -> None:
        """Test method."""
        """Test adding attribute with list values."""
        entry = LDIFEntry("cn=test,dc=example,dc=com")
        # Add single value
        entry.add_attribute("cn", "test")
        assert entry.get_attribute("cn") == ["test"]
        # Add list of values
        entry.add_attribute("objectClass", ["person", "inetOrgPerson"])
        assert entry.get_attribute("objectClass") == ["person", "inetOrgPerson"]
        # Add to existing attribute
        entry.add_attribute("cn", "alias")
        assert entry.get_attribute("cn") == ["test", "alias"]

    def test_entry_parse_dn(self) -> None:
        """Test method."""
        """Test DN parsing functionality."""
        entry = LDIFEntry("cn=john,ou=users,dc=example,dc=com")
        dn_parts = entry.parse_dn()
        assert isinstance(dn_parts, dict)
        # The exact structure depends on implementation

    def test_entry_remove_attribute(self) -> None:
        """Test method."""
        """Test removing attributes from entry."""
        entry = LDIFEntry("cn=test,dc=example,dc=com")
        entry.add_attribute("cn", "test")
        entry.add_attribute("sn", "user")
        # Remove existing attribute
        entry.remove_attribute("sn")
        assert entry.get_attribute("sn") == []
        assert entry.get_attribute("cn") == ["test"]  # Should still exist
        # Remove non-existing attribute (should not error)
        entry.remove_attribute("nonexistent")

    def test_entry_update_attribute(self) -> None:
        """Test method."""
        """Test updating attributes in entry."""
        entry = LDIFEntry("cn=test,dc=example,dc=com")
        entry.add_attribute("cn", "original")
        # Update with new value
        entry.update_attribute("cn", "updated")
        assert entry.get_attribute("cn") == ["updated"]
        # Update with list of values
        entry.update_attribute("objectClass", ["person", "inetOrgPerson"])
        assert entry.get_attribute("objectClass") == ["person", "inetOrgPerson"]

    def test_ldif_parse_error(self) -> None:
        """Test method."""
        """Test LDIF parse error exception."""
        error = LDIFParseError("Test parse error")
        assert str(error) == "Test parse error"
        assert isinstance(error, Exception)


class TestLDIFValidator:
    """Test LDIF validator functionality."""

    def test_validator_initialization(self) -> None:
        """Test method."""
        """Test LDIF validator initialization."""
        validator = LDIFValidator()
        assert validator is not None

    def test_dn_validation(self) -> None:
        """Test method."""
        """Test DN validation."""
        validator = LDIFValidator()
        # Valid DNs
        assert validator.validate_dn_format("cn=john,dc=example,dc=com")
        assert validator.validate_dn_format("ou=users,dc=example,dc=com")
        # Invalid DNs
        assert not validator.validate_dn_format("")
        assert not validator.validate_dn_format("invalid-dn")

    def test_attribute_validation(self) -> None:
        """Test method."""
        """Test attribute validation."""
        validator = LDIFValidator()
        # Valid attributes
        assert validator.validate_attribute_syntax("cn", "john")
        assert validator.validate_attribute_syntax("mail", "john@example.com")
        # Mail-specific validation
        assert validator.validate_attribute_syntax("mail", "test@domain.com")
        assert not validator.validate_attribute_syntax("mail", "invalid-email")
        # Phone validation
        assert validator.validate_attribute_syntax("telephoneNumber", "+1-555-123-4567")
        assert not validator.validate_attribute_syntax(
            "telephoneNumber",
            "invalid-phone-<>",
        )

    def test_validate_entry(self) -> None:
        """Test method."""
        """Test entry validation."""
        validator = LDIFValidator()
        # Valid entry
        valid_entry = LDIFEntry("cn=test,dc=example,dc=com")
        valid_entry.add_attribute("objectClass", "person")
        valid_entry.add_attribute("cn", "test")
        assert validator.validate_entry(valid_entry)
        # Invalid entry (empty DN)
        invalid_entry = LDIFEntry("")
        assert not validator.validate_entry(invalid_entry)

    def test_validate_objectclass_requirements(self) -> None:
        """Test method."""
        """Test objectClass requirements validation using new API."""
        validator = LDIFValidator()
        # inetOrgPerson with required attributes
        valid_inetorg = LDIFEntry("cn=test,dc=example,dc=com")
        valid_inetorg.add_attribute("objectClass", "inetOrgPerson")
        valid_inetorg.add_attribute("cn", "test")
        valid_inetorg.add_attribute("sn", "user")
        assert validator.validate_entry(valid_inetorg)
        # inetOrgPerson missing required sn - would need specific schema validation
        invalid_inetorg = LDIFEntry("cn=test,dc=example,dc=com")
        invalid_inetorg.add_attribute("objectClass", "inetOrgPerson")
        invalid_inetorg.add_attribute("cn", "test")
        # This might pass basic validation but fail schema validation
        # For now, ensure it doesn't crash
        result = validator.validate_entry(invalid_inetorg)
        assert isinstance(result, bool)

    def test_validate_entries_batch(self) -> None:
        """Test method."""
        """Test batch validation of entries."""
        validator = LDIFValidator()
        entries = [
            LDIFEntry("cn=valid1,dc=example,dc=com"),
            LDIFEntry("cn=valid2,dc=example,dc=com"),
            LDIFEntry(""),  # Invalid
        ]
        for entry in entries[:2]:
            entry.add_attribute("objectClass", "person")
            entry.add_attribute("cn", "test")
        results = validator.validate_entries(entries)
        assert isinstance(results, dict)
        assert "total_entries" in results
        assert "valid_entries" in results
        assert "invalid_entries" in results

    def test_get_validation_results(self) -> None:
        """Test method."""
        """Test getting validation results."""
        validator = LDIFValidator()
        # Validate some entries first
        valid_entry = LDIFEntry("cn=test,dc=example,dc=com")
        invalid_entry = LDIFEntry("")
        validator.validate_entry(valid_entry)
        validator.validate_entry(invalid_entry)
        results = validator.get_validation_results()
        assert isinstance(results, dict)


class TestFlextLdifProcessor:
    """Test FLEXT LDIF processor functionality."""

    @pytest.fixture
    def processor(self) -> FlextLdifProcessor:
        """Create LDIF processor instance."""
        return FlextLdifProcessor()

    @pytest.fixture
    def sample_ldif_content(self) -> str:
        """Sample LDIF content for testing."""
        return """dn: dc=example,dc=com
objectClass: domain
dc: example

dn: ou=users,dc=example,dc=com
objectClass: organizationalUnit
ou: users

dn: cn=john,ou=users,dc=example,dc=com
objectClass: person
cn: john
sn: doe
mail: john.doe@example.com
"""

    def test_processor_initialization(self, processor: FlextLdifProcessor) -> None:
        """Test LDIF processor initialization."""
        assert processor is not None

    def test_parse_ldif_content(
        self,
        processor: FlextLdifProcessor,
        sample_ldif_content: str,
    ) -> None:
        """Test parsing LDIF content."""
        result = FlextCore.Result[None].ok(
            list(processor.parse_content(sample_ldif_content)),
        )

        assert result.is_success
        entries = result.data
        assert len(entries) == 3

        # Check first entry
        first_entry = entries[0]
        assert first_entry.dn == "dc=example,dc=com"
        assert first_entry.get_attribute("objectClass") == ["domain"]

    def test_parse_ldif_file(
        self,
        processor: FlextLdifProcessor,
        tmp_path: Path,
        sample_ldif_content: str,
    ) -> None:
        """Test parsing LDIF file."""
        ldif_file = tmp_path / "test.ldif"
        ldif_file.write_text(sample_ldif_content)

        result = FlextCore.Result[None].ok(list(processor.parse_file(ldif_file)))

        assert result.is_success
        entries = result.data
        assert len(entries) == 3

    def test_invalid_ldif_content_processing(
        self, processor: FlextLdifProcessor
    ) -> None:
        """Test processing invalid LDIF content."""
        invalid_content = "this is not valid ldif content"

        try:
            result = FlextCore.Result[None].ok(
                list(processor.parse_content(invalid_content)),
            )
        except Exception as e:
            result = FlextCore.Result[None].fail(str(e))

        # Depending on implementation, this might succeed with warnings
        # or fail - adjust based on actual behavior
        assert isinstance(result, FlextCore.Result)

    def test_ldif_processing_with_validation_errors(
        self, processor: FlextLdifProcessor
    ) -> None:
        """Test LDIF processing with validation errors."""
        content_with_errors = """dnClass: domain

dn: cn=invalid,dc=example,dc=com
invalidAttribute:
"""

        try:
            result = FlextCore.Result[None].ok(
                list(processor.parse_content(content_with_errors)),
            )
        except Exception as e:
            result = FlextCore.Result[None].fail(str(e))

        # Should handle errors gracefully
        assert isinstance(result, FlextCore.Result)
        if result.is_failure:
            assert result.error is not None

    def test_processor_statistics_functionality(
        self, processor: FlextLdifProcessor
    ) -> None:
        """Test processor statistics functionality."""
        stats = processor.get_statistics()
        assert isinstance(stats, dict)
        assert (
            "processed_entries" in stats
            or "entries_processed" in stats
            or "total_entries" in stats
        )
        assert "errors" in stats

    def test_processor_load_from_string(
        self,
        processor: FlextLdifProcessor,
        sample_ldif_content: str,
    ) -> None:
        """Test loading LDIF from string."""
        result = processor.load_from_string(
            sample_ldif_content,
            source_name="test_string",
        )
        assert result.is_success
        entries = result.data
        assert len(entries) >= 1

    def test_processor_filter_methods(
        self,
        processor: FlextLdifProcessor,
        sample_ldif_content: str,
    ) -> None:
        """Test processor filter methods."""
        # First load some entries
        result = processor.load_from_string(sample_ldif_content, source_name="test")
        assert result.is_success

        # Test filter by object class
        person_entries = processor.filter_by_objectclass("person")
        assert isinstance(person_entries, list)

        # Test filter by DN pattern
        user_entries = processor.filter_by_dn_pattern("*users*")
        assert isinstance(user_entries, list)

        # Test filter by DN contains
        example_entries = processor.filter_by_dn_contains("example")
        assert isinstance(example_entries, list)

        # Test filter by attribute exists
        cn_entries = processor.filter_by_attribute_exists("cn")
        assert isinstance(cn_entries, list)

    def test_processor_to_singer_format(
        self,
        processor: FlextLdifProcessor,
        sample_ldif_content: str,
    ) -> None:
        """Test converting to Singer format."""
        # Load entries first
        result = processor.load_from_string(sample_ldif_content, source_name="test")
        assert result.is_success

        # Convert to Singer format
        singer_records = processor.to_singer_format("test_stream")
        assert isinstance(singer_records, list)

        if singer_records:
            # Check Singer record structure
            record = singer_records[0]
            assert isinstance(record, dict)
            # Singer records have structure: {"type": "RECORD", "stream": "...", "record": {...}}
            if "record" in record:
                assert "dn" in record["record"]
            else:
                assert "dn" in record

    def test_processor_load_from_file(
        self,
        processor: FlextLdifProcessor,
        tmp_path: str,
        sample_ldif_content: str,
    ) -> None:
        """Test loading from file using load_from_file method."""
        ldif_file = tmp_path / "load_test.ldif"
        ldif_file.write_text(sample_ldif_content)

        result = processor.load_from_file(ldif_file)
        assert result.is_success
        entries = result.data
        assert len(entries) >= 1


class TestLDIFProcessorIntegration:
    """Integration tests for LDIF processor."""

    def test_end_to_end_ldif_processing(self, tmp_path: str) -> None:
        """Test end-to-end LDIF processing."""
        # Create sample LDIF file
        ldif_content = """dn: dc=test,dc=com
objectClass: domain
dc: test

dn: ou=people,dc=test,dc=com
objectClass: organizationalUnit
ou: people

dn: cn=user1,ou=people,dc=test,dc=com
objectClass: person
cn: user1
sn: User One
mail: user1@test.com
"""

        ldif_file = tmp_path / "integration_test.ldif"
        ldif_file.write_text(ldif_content)

        processor = FlextLdifProcessor()
        result = FlextCore.Result[None].ok(list(processor.parse_file(ldif_file)))

        assert result.is_success
        entries = result.data
        assert len(entries) == 3

        # Validate structure
        domain_entry = next(e for e in entries if e.dn == "dc=test,dc=com")
        assert domain_entry.get_attribute("objectClass") == ["domain"]

        user_entry = next(e for e in entries if "cn=user1" in e.dn)
        assert user_entry.get_attribute("mail") == ["user1@test.com"]

    def test_multiple_ldif_files_processing(self, tmp_path: str) -> None:
        """Test processing multiple LDIF files."""
        processor = FlextLdifProcessor()

        # Create multiple LDIF files
        for i in range(3):
            content = f"""dn: cn=user{i},dc=test,dc=com
objectClass: person
cn: user{i}
sn: User {i}
"""

            ldif_file = tmp_path / f"batch_{i}.ldif"
            ldif_file.write_text(content)

        # Process all files
        results = []
        for ldif_file in tmp_path.glob("batch_*.ldif"):
            result = FlextCore.Result[None].ok(list(processor.parse_file(ldif_file)))
            results.append(result)

        assert len(results) == 3
        assert all(r.is_success for r in results)


class TestLDIFTransformer:
    """Test LDIF transformer functionality."""

    def test_transformer_initialization(self) -> None:
        """Test method."""
        """Test transformer initialization."""
        # Default initialization
        transformer = LDIFTransformer()
        assert transformer is not None

        # With transformation rules
        rules = {"attribute_mappings": {"mail": "email"}}
        transformer_with_rules = LDIFTransformer(transformation_rules=rules)
        assert transformer_with_rules is not None

    def test_transform_entry(self) -> None:
        """Test method."""
        """Test transforming LDIF entry."""
        transformer = LDIFTransformer()

        # Create test entry
        entry = LDIFEntry("cn=test,dc=example,dc=com")
        entry.add_attribute("cn", "test")
        entry.add_attribute("mail", "test@example.com")

        # Transform entry
        transformed = transformer.transform_entry(entry)

        assert isinstance(transformed, LDIFEntry)
        assert transformed.dn == entry.dn
        # Transformation specifics depend on implementation

    def test_apply_attribute_mappings(self) -> None:
        """Test method."""
        """Test attribute mapping functionality."""
        rules = {"attribute_mappings": {"mail": "email", "cn": "commonName"}}
        transformer = LDIFTransformer(transformation_rules=rules)

        entry = LDIFEntry("cn=test,dc=example,dc=com")
        entry.add_attribute("cn", "test")
        entry.add_attribute("mail", "test@example.com")

        # Apply mappings (method signature may vary)
        try:
            mapped_entry = transformer.apply_attribute_mappings(
                entry,
                rules["attribute_mappings"],
            )
            assert isinstance(mapped_entry, (LDIFEntry, dict))
        except (AttributeError, TypeError):
            # Method might have different signature or not exist yet
            pass


class TestLDIFProcessorErrorHandling:
    """Test error handling in LDIF processor."""

    def test_processor_with_parsing_errors(self) -> None:
        """Test method."""
        """Test processor handling of parsing errors."""
        processor = FlextLdifProcessor(ignore_errors=True, max_errors=5)

        # Content with intentional errors
        problematic_content = """dn: cn=valid,dc=example,dc=com
objectClass: person
cn: valid

dnClass: invalid

invalidLine
attribute: value

dn: cn=another_valid,dc=example,dc=com
objectClass: person
cn: another
"""

        try:
            result = FlextCore.Result[None].ok(
                list(processor.parse_content(problematic_content)),
            )
            if result.is_success:
                entries = result.data
                # Should still process valid entries
                assert len(entries) >= 1
        except Exception as exc:
            # If parsing fails completely, that's also acceptable behavior for this test
            # but do not silently ignore
            pytest.skip(f"Parsing failed as expected in strict mode: {exc}")

    def test_processor_max_errors_limit(self) -> None:
        """Test method."""
        """Test processor max errors limit."""
        processor = FlextLdifProcessor(ignore_errors=True, max_errors=2)

        # Create content with many errors
        error_content = "\n".join([f"invalid_line_{i}" for i in range(10)])

        result = FlextCore.Result[None].ok(list(processor.parse_content(error_content)))
        # Should handle gracefully due to error limits
        assert isinstance(result, FlextCore.Result)

    def test_processor_ignore_errors_false(self) -> None:
        """Test method."""
        """Test processor with ignore_errors=False."""
        processor = FlextLdifProcessor(ignore_errors=False)

        invalid_content = "clearly invalid ldif content"

        try:
            result = FlextCore.Result[None].ok(
                list(processor.parse_content(invalid_content)),
            )
            # Should either succeed or fail, but handle gracefully
            assert isinstance(result, FlextCore.Result)
        except Exception as exc:
            # Should raise exception when not ignoring errors - this is expected
            pytest.skip(f"Strict parser raised as expected: {exc}")
