"""Tests for LDIF processor functionality."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest

from tap_ldap.ldif_processor import LDIFEntry, LDIFProcessor, LDIFValidator


class TestLDIFEntry:
    """Test LDIF entry functionality."""

    def test_basic_entry_creation(self) -> None:
        """Test basic LDIF entry creation."""
        entry = LDIFEntry("cn=john,ou=users,dc=example,dc=com")
        assert entry.dn == "cn=john,ou=users,dc=example,dc=com"
        assert entry.attributes == {}
        assert entry.change_type is None
        assert entry.controls == []

    def test_entry_with_attributes(self) -> None:
        """Test LDIF entry with attributes."""
        attributes = {
            "cn": ["john"],
            "objectClass": ["person", "inetOrgPerson"],
            "mail": ["john@example.com"],
        }
        entry = LDIFEntry("cn=john,ou=users,dc=example,dc=com", attributes)

        assert entry.get_attribute("cn") == ["john"]
        assert entry.get_attribute("mail") == ["john@example.com"]
        assert entry.get_attribute("nonexistent") is None

    def test_case_insensitive_attribute_access(self) -> None:
        """Test case-insensitive attribute access."""
        attributes = {"cn": ["john"], "Mail": ["john@example.com"]}
        entry = LDIFEntry("cn=john,ou=users,dc=example,dc=com", attributes)

        assert entry.get_attribute("CN") == ["john"]
        assert entry.get_attribute("mail") == ["john@example.com"]
        assert entry.get_attribute("MAIL") == ["john@example.com"]

    def test_has_object_class(self) -> None:
        """Test object class checking."""
        attributes = {"objectClass": ["person", "inetOrgPerson"]}
        entry = LDIFEntry("cn=john,ou=users,dc=example,dc=com", attributes)

        assert entry.has_object_class("person") is True
        assert entry.has_object_class("PERSON") is True
        assert entry.has_object_class("inetOrgPerson") is True
        assert entry.has_object_class("group") is False

    def test_to_dict(self) -> None:
        """Test entry to dictionary conversion."""
        attributes = {"cn": ["john"], "objectClass": ["person"]}
        entry = LDIFEntry("cn=john,ou=users,dc=example,dc=com", attributes)
        entry.change_type = "add"
        entry.controls = ["critical"]

        result = entry.to_dict()

        assert result["dn"] == "cn=john,ou=users,dc=example,dc=com"
        assert result["attributes"] == attributes
        assert result["change_type"] == "add"
        assert result["controls"] == ["critical"]


class TestLDIFProcessor:
    """Test LDIF processor functionality."""

    def test_parse_simple_entry(self) -> None:
        """Test parsing a simple LDIF entry."""
        ldif_content = dedent(
            """
            dn: cn=john,ou=users,dc=example,dc=com
            cn: john
            objectClass: person
            objectClass: inetOrgPerson
            mail: john@example.com
        """,
        ).strip()

        processor = LDIFProcessor()
        entries = list(processor.parse_content(ldif_content))

        assert len(entries) == 1
        entry = entries[0]

        assert entry.dn == "cn=john,ou=users,dc=example,dc=com"
        assert entry.get_attribute("cn") == ["john"]
        assert entry.get_attribute("objectClass") == ["person", "inetOrgPerson"]
        assert entry.get_attribute("mail") == ["john@example.com"]

    def test_parse_multiple_entries(self) -> None:
        """Test parsing multiple LDIF entries."""
        ldif_content = dedent(
            """
            dn: cn=john,ou=users,dc=example,dc=com
            cn: john
            objectClass: person

            dn: cn=jane,ou=users,dc=example,dc=com
            cn: jane
            objectClass: person
            mail: jane@example.com
        """,
        ).strip()

        processor = LDIFProcessor()
        entries = list(processor.parse_content(ldif_content))

        assert len(entries) == 2

        assert entries[0].dn == "cn=john,ou=users,dc=example,dc=com"
        assert entries[0].get_attribute("cn") == ["john"]
        assert entries[0].get_attribute("mail") is None

        assert entries[1].dn == "cn=jane,ou=users,dc=example,dc=com"
        assert entries[1].get_attribute("cn") == ["jane"]
        assert entries[1].get_attribute("mail") == ["jane@example.com"]

    def test_parse_with_comments_and_empty_lines(self) -> None:
        """Test parsing LDIF with comments and empty lines."""
        ldif_content = dedent(
            """
            # This is a comment

            dn: cn=john,ou=users,dc=example,dc=com
            # Another comment
            cn: john
            objectClass: person

            # Empty line above should not break parsing
        """,
        ).strip()

        processor = LDIFProcessor()
        entries = list(processor.parse_content(ldif_content))

        assert len(entries) == 1
        entry = entries[0]

        assert entry.dn == "cn=john,ou=users,dc=example,dc=com"
        assert entry.get_attribute("cn") == ["john"]
        assert entry.get_attribute("objectClass") == ["person"]

    def test_parse_with_line_continuation(self) -> None:
        """Test parsing LDIF with line continuation."""
        ldif_content = dedent(
            """
            dn: cn=john,ou=users,dc=example,dc=com
            cn: john
            description: This is a very long description that spans
             multiple lines using line continuation
            objectClass: person
        """,
        ).strip()

        processor = LDIFProcessor()
        entries = list(processor.parse_content(ldif_content))

        assert len(entries) == 1
        entry = entries[0]

        description = entry.get_attribute("description")
        assert description is not None
        assert len(description) == 1
        assert "multiple lines using line continuation" in description[0]

    def test_parse_with_changetype(self) -> None:
        """Test parsing LDIF with changetype."""
        ldif_content = dedent(
            """
            dn: cn=john,ou=users,dc=example,dc=com
            changetype: add
            cn: john
            objectClass: person
        """,
        ).strip()

        processor = LDIFProcessor()
        entries = list(processor.parse_content(ldif_content))

        assert len(entries) == 1
        entry = entries[0]

        assert entry.dn == "cn=john,ou=users,dc=example,dc=com"
        assert entry.change_type == "add"
        assert entry.get_attribute("cn") == ["john"]

    def test_parse_with_controls(self) -> None:
        """Test parsing LDIF with controls."""
        ldif_content = dedent(
            """
            dn: cn=john,ou=users,dc=example,dc=com
            control: 1.2.3.4 critical
            cn: john
            objectClass: person
        """,
        ).strip()

        processor = LDIFProcessor()
        entries = list(processor.parse_content(ldif_content))

        assert len(entries) == 1
        entry = entries[0]

        assert entry.dn == "cn=john,ou=users,dc=example,dc=com"
        assert entry.controls == ["1.2.3.4 critical"]
        assert entry.get_attribute("cn") == ["john"]

    def test_parse_with_base64_values(self) -> None:
        """Test parsing LDIF with base64 encoded values."""
        # Base64 encoded test value
        ldif_content = dedent(
            """
            dn: cn=john,ou=users,dc=example,dc=com
            cn: john
            description:: dGVzdCB2YWx1ZQ==
            objectClass: person
        """,
        ).strip()

        processor = LDIFProcessor()
        entries = list(processor.parse_content(ldif_content))

        assert len(entries) == 1
        entry = entries[0]

        assert entry.dn == "cn=john,ou=users,dc=example,dc=com"
        assert entry.get_attribute("description") == ["test value"]

    def test_parse_file(self, tmp_path: Path) -> None:
        """Test parsing LDIF from file."""
        ldif_content = dedent(
            """
            dn: cn=john,ou=users,dc=example,dc=com
            cn: john
            objectClass: person
        """,
        ).strip()

        ldif_file = tmp_path / "test.ldif"
        ldif_file.write_text(ldif_content, encoding="utf-8")

        processor = LDIFProcessor()
        entries = list(processor.parse_file(ldif_file))

        assert len(entries) == 1
        assert entries[0].dn == "cn=john,ou=users,dc=example,dc=com"

    def test_parse_nonexistent_file(self) -> None:
        """Test parsing nonexistent file raises error."""
        processor = LDIFProcessor()

        with pytest.raises(FileNotFoundError):
            list(processor.parse_file(Path("/nonexistent/file.ldif")))

    def test_error_handling_ignore_errors(self) -> None:
        """Test error handling with ignore_errors=True."""
        ldif_content = dedent(
            """
            dn: cn=john,ou=users,dc=example,dc=com
            cn: john
            invalid_line_without_colon
            objectClass: person
        """,
        ).strip()

        processor = LDIFProcessor(ignore_errors=True)
        entries = list(processor.parse_content(ldif_content))

        assert len(entries) == 1  # Should still parse the valid entry
        assert len(processor.errors) > 0  # Should have recorded the error

    def test_statistics(self) -> None:
        """Test processor statistics."""
        ldif_content = dedent(
            """
            dn: cn=john,ou=users,dc=example,dc=com
            cn: john
            objectClass: person

            dn: cn=jane,ou=users,dc=example,dc=com
            cn: jane
            objectClass: person
        """,
        ).strip()

        processor = LDIFProcessor()
        entries = list(processor.parse_content(ldif_content))
        stats = processor.get_statistics()

        assert len(entries) == 2
        assert stats["processed_entries"] == 2
        assert stats["errors"] == 0


class TestLDIFValidator:
    """Test LDIF validator functionality."""

    def test_validate_valid_entry(self) -> None:
        """Test validating a valid entry."""
        attributes = {
            "cn": ["john"],
            "objectClass": ["person", "inetOrgPerson"],
            "mail": ["john@example.com"],
        }
        entry = LDIFEntry("cn=john,ou=users,dc=example,dc=com", attributes)

        validator = LDIFValidator()
        is_valid = validator.validate_entry(entry)

        assert is_valid is True

    def test_validate_entry_missing_dn(self) -> None:
        """Test validating entry with missing DN."""
        attributes = {"cn": ["john"], "objectClass": ["person"]}
        entry = LDIFEntry("", attributes)

        validator = LDIFValidator()
        is_valid = validator.validate_entry(entry)

        assert is_valid is False
        results = validator.get_validation_results()
        assert len(results["errors"]) > 0

    def test_validate_entry_missing_objectclass(self) -> None:
        """Test validating entry without objectClass."""
        attributes = {"cn": ["john"]}
        entry = LDIFEntry("cn=john,ou=users,dc=example,dc=com", attributes)

        validator = LDIFValidator()
        is_valid = validator.validate_entry(entry)

        assert is_valid is False
        results = validator.get_validation_results()
        assert len(results["errors"]) > 0

    def test_validate_entry_invalid_dn(self) -> None:
        """Test validating entry with invalid DN format."""
        attributes = {"cn": ["john"], "objectClass": ["person"]}
        entry = LDIFEntry("invalid_dn_format", attributes)

        validator = LDIFValidator()
        is_valid = validator.validate_entry(entry)

        assert is_valid is False
        results = validator.get_validation_results()
        assert len(results["errors"]) > 0

    def test_validation_results(self) -> None:
        """Test getting validation results."""
        validator = LDIFValidator()

        # Test valid entry
        valid_attributes = {"cn": ["john"], "objectClass": ["person"]}
        valid_entry = LDIFEntry("cn=john,ou=users,dc=example,dc=com", valid_attributes)
        validator.validate_entry(valid_entry)

        # Test invalid entry
        invalid_attributes = {"cn": ["jane"]}  # Missing objectClass
        invalid_entry = LDIFEntry(
            "cn=jane,ou=users,dc=example,dc=com",
            invalid_attributes,
        )
        validator.validate_entry(invalid_entry)

        results = validator.get_validation_results()

        assert results["is_valid"] is False  # Overall validation failed
        assert len(results["errors"]) > 0
        assert len(results.get("warnings", [])) >= 0
