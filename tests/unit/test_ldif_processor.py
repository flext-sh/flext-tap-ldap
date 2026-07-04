"""Tests for LDIF processor functionality.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import Mock

import pytest

from flext_tap_ldap.ldif_streams import FlextTapLdapLdifStreams
from tests.utilities import u

if TYPE_CHECKING:
    from pathlib import Path

    from tests.typings import t


class TestsFlextTapLdapLdifProcessor:
    """Placeholder tests pending refactoring with proper FlextTapLdapProcessor API."""

    def test_placeholder(self) -> None:
        """Placeholder test to satisfy pytest collection."""
        assert u.TapLdap.Processor is not None

    def test_ldif_directory_processing_traverses_ldif_files(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        nested = tmp_path / "nested"
        nested.mkdir()
        file_a = tmp_path / "a.ldif"
        file_b = nested / "b.ldif"
        ignored = nested / "ignore.txt"
        file_a.write_text(
            "dn: cn=a,dc=example,dc=com\nobjectClass: person\ncn: a\n\n",
            encoding="utf-8",
        )
        file_b.write_text(
            "dn: cn=b,dc=example,dc=com\nobjectClass: person\ncn: b\n\n",
            encoding="utf-8",
        )
        ignored.write_text("not-ldif", encoding="utf-8")
        stream = object.__new__(FlextTapLdapLdifStreams.LdifStream)
        stream.tap = Mock()
        stream.settings = {
            "ldif_directory": str(tmp_path),
            "ldif_file_pattern": "*.ldif",
        }
        stream._logger_instance = None

        seen: list[str] = []

        def _process(ldif_file: str) -> t.SequenceOf[t.JsonMapping]:
            seen.append(ldif_file)
            return [{"dn": ldif_file}]

        monkeypatch.setattr(stream, "_process_ldif_file", _process)

        records = list(stream.get_records())
        assert len(records) == 2
        assert set(seen) == {str(file_a), str(file_b)}

    def test_transform_entry_applies_rules(self) -> None:
        transformer = u.TapLdap.Transformer(
            transformation_rules={
                "attribute_mappings": {"CN": "cn", "sn": "surname"},
                "attribute_value_mappings": {
                    "department": {"IT": "Information Technology"},
                },
                "remove_attributes": ["obsolete"],
                "add_attributes": {"status": "active"},
            },
        )
        entry = u.TapLdap.Entry(
            "cn=alice,dc=example,dc=com",
            {"CN": ["Alice"], "sn": ["Smith"], "department": ["IT"], "obsolete": ["x"]},
        )
        entry.change_type = "modify"
        entry.controls = ["control-a"]
        transformed = transformer.transform_entry(entry)
        assert transformed is not entry
        assert transformed.attributes["cn"] == ["Alice"]
        assert transformed.attributes["surname"] == ["Smith"]
        assert transformed.attributes["department"] == ["Information Technology"]
        assert "obsolete" not in transformed.attributes
        assert transformed.attributes["status"] == ["active"]
        assert transformed.change_type == "modify"
        assert transformed.controls == ["control-a"]

    def test_parse_content_reports_non_empty_content_without_entries(self) -> None:
        processor = u.TapLdap.Processor()

        records = list(processor.parse_content("not ldif", "broken.ldif"))

        assert not records
        assert processor.errors == [
            "LDIF content from broken.ldif produced no entries",
        ]

    def test_parse_content_raises_for_empty_result_when_strict(self) -> None:
        processor = u.TapLdap.Processor(ignore_errors=False)

        with pytest.raises(ValueError, match="produced no entries"):
            list(processor.parse_content("not ldif", "broken.ldif"))

    def test_parse_file_records_decode_errors_without_encoding_fallback(
        self,
        tmp_path: Path,
    ) -> None:
        ldif_file = tmp_path / "invalid.ldif"
        ldif_file.write_bytes(b"\xff\xfe")
        processor = u.TapLdap.Processor()

        records = list(processor.parse_file(ldif_file))

        assert not records
        assert len(processor.errors) == 1
        assert str(ldif_file) in processor.errors[0]
        assert "invalid start byte" in processor.errors[0]

    def test_entry_creation_rejects_unparsed_entry_without_fallback(self) -> None:
        with pytest.raises(ValueError, match="parsed without entries"):
            u.TapLdap.Entry("", {})

    def test_validator_uses_real_ldif_validation(self) -> None:
        validator = u.TapLdap.Validator()
        entry = u.TapLdap.Entry(
            "cn=alice,dc=example,dc=com",
            {"objectClass": ["invalid class"], "cn": ["Alice"]},
        )

        result = validator.validate_entries([entry])

        assert result["total_entries"] == 1
        assert result["valid_entries"] == 0
        assert result["invalid_entries"] == 1
        assert result["errors"] == [
            "Entry cn=alice,dc=example,dc=com: Invalid objectClass 'invalid class'",
        ]

    def test_directory_processing_returns_empty_when_no_ldif_files(self) -> None:
        """Test that _process_ldap_directory returns empty when disabled."""
        stream = object.__new__(FlextTapLdapLdifStreams.LdifStream)
        stream.tap = Mock()
        stream.settings = {
            "ldap_host": "ldap.example.com",
            "ldap_base_dn": "dc=example,dc=com",
        }
        stream._ldif_api = Mock()
        stream._logger_instance = None
        records = list(stream.get_records())
        assert not records

    def test_transform_entry_applies_schema_mappings(self) -> None:
        transformer = u.TapLdap.Transformer(
            transformation_rules={
                "schema_mappings": {
                    "uid": "employeeId",
                    "status": {"source": "employmentStatus", "default": "active"},
                },
            },
        )
        entry = u.TapLdap.Entry(
            "cn=alice,dc=example,dc=com",
            {"employeeId": ["1001"]},
        )
        transformed = transformer.transform_entry(entry)
        assert transformed.attributes["uid"] == ["1001"]
        assert transformed.attributes["status"] == ["active"]
