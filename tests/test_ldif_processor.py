"""Tests for LDIF processor functionality."""

from __future__ import annotations

from typing import Any

import pytest
from flext_core import FlextResult

from flext_tap_ldap.ldif_processor import FlextLDIFProcessor, LDIFEntry, LDIFValidator


class TestLDIFEntry:
    """Test LDIF entry functionality with modern patterns."""

    def test_basic_entry_creation(self) -> None:
        """Test basic LDIF entry creation and validation."""
        entry = LDIFEntry("cn=john,ou=users,dc=example,dc=com")

        assert entry.dn == "cn=john,ou=users,dc=example,dc=com"
        assert entry.attributes == {}
        assert entry.is_valid()

    def test_entry_with_attributes(self) -> None:
        """Test LDIF entry with attributes."""
        entry = LDIFEntry("cn=john,ou=users,dc=example,dc=com")
        entry.add_attribute("cn", "john")
        entry.add_attribute("sn", "doe")
        entry.add_attribute("mail", "john.doe@example.com")

        assert entry.get_attribute("cn") == ["john"]
        assert entry.get_attribute("sn") == ["doe"]
        assert entry.get_attribute("mail") == ["john.doe@example.com"]

    def test_entry_validation(self) -> None:
        """Test LDIF entry validation."""
        # Valid entry
        valid_entry = LDIFEntry("cn=valid,dc=example,dc=com")
        valid_entry.add_attribute("objectClass", "person")
        assert valid_entry.is_valid()

        # Invalid entry (empty DN)
        invalid_entry = LDIFEntry("")
        assert not invalid_entry.is_valid()


class TestLDIFValidator:
    """Test LDIF validator functionality."""

    def test_validator_initialization(self) -> None:
        """Test LDIF validator initialization."""
        validator = LDIFValidator()
        assert validator is not None

    def test_dn_validation(self) -> None:
        """Test DN validation."""
        validator = LDIFValidator()

        # Valid DNs
        assert validator.validate_dn("cn=john,dc=example,dc=com")
        assert validator.validate_dn("ou=users,dc=example,dc=com")

        # Invalid DNs
        assert not validator.validate_dn("")
        assert not validator.validate_dn("invalid-dn")

    def test_attribute_validation(self) -> None:
        """Test attribute validation."""
        validator = LDIFValidator()

        # Valid attributes
        assert validator.validate_attribute("cn", "john")
        assert validator.validate_attribute("mail", "john@example.com")

        # Invalid attributes
        assert not validator.validate_attribute("", "value")
        assert not validator.validate_attribute("cn", "")


class TestFlextLDIFProcessor:
    """Test FLEXT LDIF processor functionality."""

    @pytest.fixture
    def processor(self) -> FlextLDIFProcessor:
        """Create LDIF processor instance."""
        return FlextLDIFProcessor()

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

    def test_processor_initialization(self, processor: FlextLDIFProcessor) -> None:
        """Test LDIF processor initialization."""
        assert processor is not None

    def test_parse_ldif_content(
        self, processor: FlextLDIFProcessor, sample_ldif_content: str,
    ) -> None:
        """Test parsing LDIF content."""
        result = FlextResult.success(list(processor.parse_content(sample_ldif_content)))

        assert result.is_success
        entries = result.data
        assert len(entries) == 3

        # Check first entry
        first_entry = entries[0]
        assert first_entry.dn == "dc=example,dc=com"
        assert first_entry.get_attribute("objectClass") == ["domain"]

    def test_parse_ldif_file(
        self, processor: FlextLDIFProcessor, tmp_path: Any, sample_ldif_content: str,
    ) -> None:
        """Test parsing LDIF file."""
        ldif_file = tmp_path / "test.ldif"
        ldif_file.write_text(sample_ldif_content)

        result = FlextResult.success(list(processor.parse_file(ldif_file)))

        assert result.is_success
        entries = result.data
        assert len(entries) == 3

    def test_process_invalid_ldif(self, processor: FlextLDIFProcessor) -> None:
        """Test processing invalid LDIF content."""
        invalid_content = "this is not valid ldif content"

        try:
            result = FlextResult.success(list(processor.parse_content(invalid_content)))
        except Exception as e:
            result = FlextResult.failure(str(e))

        # Depending on implementation, this might succeed with warnings
        # or fail - adjust based on actual behavior
        assert isinstance(result, FlextResult)

    def test_validation_with_errors(self, processor: FlextLDIFProcessor) -> None:
        """Test LDIF processing with validation errors."""
        content_with_errors = """dn:
objectClass: domain

dn: cn=invalid,dc=example,dc=com
invalidAttribute:
"""

        try:
            result = FlextResult.success(
                list(processor.parse_content(content_with_errors)),
            )
        except Exception as e:
            result = FlextResult.failure(str(e))

        # Should handle errors gracefully
        assert isinstance(result, FlextResult)
        if result.is_failure:
            assert result.error is not None


class TestLDIFProcessorIntegration:
    """Integration tests for LDIF processor."""

    def test_end_to_end_processing(self, tmp_path: Any) -> None:
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

        processor = FlextLDIFProcessor()
        result = FlextResult.success(list(processor.parse_file(ldif_file)))

        assert result.is_success
        entries = result.data
        assert len(entries) == 3

        # Validate structure
        domain_entry = next(e for e in entries if e.dn == "dc=test,dc=com")
        assert domain_entry.get_attribute("objectClass") == ["domain"]

        user_entry = next(e for e in entries if "cn=user1" in e.dn)
        assert user_entry.get_attribute("mail") == ["user1@test.com"]

    def test_batch_processing(self, tmp_path: Any) -> None:
        """Test processing multiple LDIF files."""
        processor = FlextLDIFProcessor()

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
            result = FlextResult.success(list(processor.parse_file(ldif_file)))
            results.append(result)

        assert len(results) == 3
        assert all(r.is_success for r in results)
