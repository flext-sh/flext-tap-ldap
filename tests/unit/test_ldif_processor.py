"""Behavioral tests for the LDIF processor utilities (u.TapLdap.*).

Exercises the PUBLIC contract of Entry, Processor, Validator and Transformer:
parsed entries, r[T]/error outcomes, raised exceptions, and public model state.
No private attributes, no internal-collaborator spying, no monkeypatching of the
unit under test.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests import u

if TYPE_CHECKING:
    from pathlib import Path

_PERSON_LDIF = (
    "dn: cn=alice,dc=example,dc=com\nobjectClass: person\ncn: alice\nsn: smith\n\n"
)
_SECOND_LDIF = (
    "dn: cn=bob,dc=example,dc=com\nobjectClass: person\ncn: bob\nsn: jones\n\n"
)


class TestsFlextTapLdapLdifProcessor:
    """Public-contract behavior of the LDIF processing utilities."""

    # ---- Entry -----------------------------------------------------------

    def test_entry_creation_copies_attributes_into_public_state(self) -> None:
        source = {"cn": ["alice"], "objectClass": ["person"]}
        entry = u.TapLdap.Entry("cn=alice,dc=example,dc=com", source)

        assert entry.dn == "cn=alice,dc=example,dc=com"
        assert entry.attributes["cn"] == ["alice"]
        # Entry owns an independent copy; mutating the source is not observable.
        source["cn"].append("mutated")
        assert entry.attributes["cn"] == ["alice"]

    def test_entry_creation_rejects_unparsed_entry_without_fallback(self) -> None:
        with pytest.raises(ValueError, match="parsed without entries"):
            u.TapLdap.Entry("", {})

    def test_resolve_attribute_values_is_case_insensitive(self) -> None:
        entry = u.TapLdap.Entry(
            "cn=alice,dc=example,dc=com",
            {"cn": ["alice"], "objectClass": ["person"]},
        )

        assert entry.resolve_attribute_values("CN") == ["alice"]
        assert entry.resolve_attribute_values("missing") == []

    def test_has_object_class_matches_case_insensitively(self) -> None:
        entry = u.TapLdap.Entry(
            "cn=alice,dc=example,dc=com",
            {"cn": ["alice"], "objectClass": ["person"]},
        )

        assert entry.has_object_class("PERSON") is True
        assert entry.has_object_class("group") is False

    def test_add_update_and_remove_attribute_change_public_state(self) -> None:
        entry = u.TapLdap.Entry(
            "cn=alice,dc=example,dc=com",
            {"cn": ["alice"], "objectClass": ["person"]},
        )

        entry.add_attribute("mail", "alice@example.com")
        assert entry.resolve_attribute_values("mail") == ["alice@example.com"]

        entry.update_attribute("cn", "renamed")
        assert entry.attributes["cn"] == ["renamed"]

        entry.remove_attribute("objectClass")
        assert entry.resolve_attribute_values("objectClass") == []

    def test_to_dict_exposes_dn_and_attribute_snapshot(self) -> None:
        entry = u.TapLdap.Entry(
            "cn=alice,dc=example,dc=com",
            {"cn": ["alice"], "objectClass": ["person"]},
        )
        entry.change_type = "add"
        entry.controls = ["ctrl-1"]

        payload = entry.to_dict()

        assert payload["dn"] == "cn=alice,dc=example,dc=com"
        assert "alice" in str(payload["attributes"])
        assert payload["change_type"] == "add"
        assert payload["controls"] == ["ctrl-1"]

    def test_parse_dn_returns_original_dn(self) -> None:
        entry = u.TapLdap.Entry(
            "cn=alice,dc=example,dc=com",
            {"cn": ["alice"], "objectClass": ["person"]},
        )

        parsed = entry.parse_dn()

        assert parsed["dn"] == "cn=alice,dc=example,dc=com"

    # ---- Processor.parse_content ----------------------------------------

    def test_parse_content_yields_entries_from_valid_ldif(self) -> None:
        processor = u.TapLdap.Processor()

        records = list(processor.parse_content(_PERSON_LDIF, "memory.ldif"))

        assert len(records) == 1
        assert "alice" in records[0].dn.lower()
        assert records[0].resolve_attribute_values("cn") == ["alice"]
        assert processor.errors == []

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

    # ---- Processor.parse_file -------------------------------------------

    def test_parse_file_yields_entries_from_real_files(
        self,
        tmp_path: Path,
    ) -> None:
        nested = tmp_path / "nested"
        nested.mkdir()
        file_a = tmp_path / "a.ldif"
        file_b = nested / "b.ldif"
        file_a.write_text(_PERSON_LDIF, encoding="utf-8")
        file_b.write_text(_SECOND_LDIF, encoding="utf-8")
        processor = u.TapLdap.Processor()

        dns = {
            entry.dn.lower()
            for ldif_file in (file_a, file_b)
            for entry in processor.parse_file(ldif_file)
        }

        assert any("alice" in dn for dn in dns)
        assert any("bob" in dn for dn in dns)
        assert processor.errors == []

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

    def test_parse_file_missing_file_raises(self, tmp_path: Path) -> None:
        processor = u.TapLdap.Processor()

        with pytest.raises(ValueError, match="LDIF file not found"):
            list(processor.parse_file(tmp_path / "absent.ldif"))

    # ---- Processor loaders + reporting ----------------------------------

    def test_load_from_string_reports_success_and_updates_stats(self) -> None:
        processor = u.TapLdap.Processor()

        result = processor.load_from_string(_PERSON_LDIF, "memory.ldif")

        assert result.success
        assert processor.stats["total_entries"] == 1
        assert processor.statistics()["processed_entries"] == 1

    def test_load_from_file_reports_success(self, tmp_path: Path) -> None:
        ldif_file = tmp_path / "load.ldif"
        ldif_file.write_text(_PERSON_LDIF, encoding="utf-8")
        processor = u.TapLdap.Processor()

        result = processor.load_from_file(ldif_file)

        assert result.success
        assert processor.stats["total_entries"] == 1

    def test_to_singer_format_wraps_loaded_entries_as_records(self) -> None:
        processor = u.TapLdap.Processor()
        assert processor.load_from_string(_PERSON_LDIF, "memory.ldif").success

        records = processor.to_singer_format("people")

        assert len(records) == 1
        assert records[0]["type"] == "RECORD"
        assert records[0]["stream"] == "people"
        assert "alice" in str(records[0]["record"]).lower()

    def test_filters_select_loaded_entries_by_public_criteria(self) -> None:
        processor = u.TapLdap.Processor()
        assert processor.load_from_string(
            _PERSON_LDIF + _SECOND_LDIF,
            "memory.ldif",
        ).success

        by_dn = processor.filter_by_dn_contains("alice")
        by_attr = processor.filter_by_attribute_exists("sn")
        by_class = processor.filter_by_objectclass("person")

        assert len(by_dn) == 1
        assert "alice" in by_dn[0].dn.lower()
        assert len(by_attr) == 2
        assert len(by_class) == 2

    # ---- Validator -------------------------------------------------------

    def test_validator_reports_invalid_object_class(self) -> None:
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

    def test_validation_results_expose_valid_flag(self) -> None:
        validator = u.TapLdap.Validator()

        results = validator.validation_results()

        assert results["valid"] is True
        assert results["errors"] == []
        assert results["warnings"] == []

    # ---- Transformer -----------------------------------------------------

    def test_transform_entry_applies_rules_and_returns_new_entry(self) -> None:
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
        # Source entry is left untouched (immutability of the transform).
        assert "CN" in entry.attributes
        assert "obsolete" in entry.attributes

    def test_transform_entry_applies_schema_mappings_with_defaults(self) -> None:
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

    def test_transform_entry_without_rules_is_identity_copy(self) -> None:
        transformer = u.TapLdap.Transformer()
        entry = u.TapLdap.Entry(
            "cn=alice,dc=example,dc=com",
            {"cn": ["alice"], "objectClass": ["person"]},
        )

        transformed = transformer.transform_entry(entry)

        assert transformed is not entry
        assert transformed.attributes["cn"] == ["alice"]
        assert transformed.dn == entry.dn


__all__ = ["TestsFlextTapLdapLdifProcessor"]
