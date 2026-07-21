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
from flext_tests import tm

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

        tm.that(entry.dn, eq="cn=alice,dc=example,dc=com")
        tm.that(entry.attributes["cn"], eq=["alice"])
        # Entry owns an independent copy; mutating the source is not observable.
        source["cn"].append("mutated")
        tm.that(entry.attributes["cn"], eq=["alice"])

    def test_entry_creation_rejects_unparsed_entry_without_fallback(self) -> None:
        with pytest.raises(ValueError, match="parsed without entries"):
            u.TapLdap.Entry("", {})

    def test_resolve_attribute_values_is_case_insensitive(self) -> None:
        entry = u.TapLdap.Entry(
            "cn=alice,dc=example,dc=com",
            {"cn": ["alice"], "objectClass": ["person"]},
        )

        tm.that(entry.resolve_attribute_values("CN"), eq=["alice"])
        tm.that(entry.resolve_attribute_values("missing"), eq=[])

    def test_has_object_class_matches_case_insensitively(self) -> None:
        entry = u.TapLdap.Entry(
            "cn=alice,dc=example,dc=com",
            {"cn": ["alice"], "objectClass": ["person"]},
        )

        tm.that(entry.has_object_class("PERSON"), eq=True)
        tm.that(entry.has_object_class("group"), eq=False)

    def test_add_update_and_remove_attribute_change_public_state(self) -> None:
        entry = u.TapLdap.Entry(
            "cn=alice,dc=example,dc=com",
            {"cn": ["alice"], "objectClass": ["person"]},
        )

        entry.add_attribute("mail", "alice@example.com")
        tm.that(entry.resolve_attribute_values("mail"), eq=["alice@example.com"])

        entry.update_attribute("cn", "renamed")
        tm.that(entry.attributes["cn"], eq=["renamed"])

        entry.remove_attribute("objectClass")
        tm.that(entry.resolve_attribute_values("objectClass"), eq=[])

    def test_to_dict_exposes_dn_and_attribute_snapshot(self) -> None:
        entry = u.TapLdap.Entry(
            "cn=alice,dc=example,dc=com",
            {"cn": ["alice"], "objectClass": ["person"]},
        )
        entry.change_type = "add"
        entry.controls = ["ctrl-1"]

        payload = entry.to_dict()

        tm.that(payload["dn"], eq="cn=alice,dc=example,dc=com")
        tm.that(str(payload["attributes"]), has="alice")
        tm.that(payload["change_type"], eq="add")
        tm.that(payload["controls"], eq=["ctrl-1"])

    def test_parse_dn_returns_original_dn(self) -> None:
        entry = u.TapLdap.Entry(
            "cn=alice,dc=example,dc=com",
            {"cn": ["alice"], "objectClass": ["person"]},
        )

        parsed = entry.parse_dn()

        tm.that(parsed["dn"], eq="cn=alice,dc=example,dc=com")

    # ---- Processor.parse_content ----------------------------------------

    def test_parse_content_yields_entries_from_valid_ldif(self) -> None:
        processor = u.TapLdap.Processor()

        records = list(processor.parse_content(_PERSON_LDIF, "memory.ldif"))

        tm.that(len(records), eq=1)
        tm.that(records[0].dn.lower(), has="alice")
        tm.that(records[0].resolve_attribute_values("cn"), eq=["alice"])
        tm.that(processor.errors, eq=[])

    def test_parse_content_reports_non_empty_content_without_entries(self) -> None:
        processor = u.TapLdap.Processor()

        records = list(processor.parse_content("not ldif", "broken.ldif"))

        assert not records
        tm.that(
            processor.errors,
            eq=[
                "LDIF content from broken.ldif produced no entries",
            ],
        )

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
        tm.that(processor.errors, eq=[])

    def test_parse_file_records_decode_errors_without_encoding_fallback(
        self,
        tmp_path: Path,
    ) -> None:
        ldif_file = tmp_path / "invalid.ldif"
        ldif_file.write_bytes(b"\xff\xfe")
        processor = u.TapLdap.Processor()

        records = list(processor.parse_file(ldif_file))

        assert not records
        tm.that(len(processor.errors), eq=1)
        tm.that(processor.errors[0], has=str(ldif_file))
        tm.that(processor.errors[0], has="invalid start byte")

    def test_parse_file_missing_file_raises(self, tmp_path: Path) -> None:
        processor = u.TapLdap.Processor()

        with pytest.raises(ValueError, match="LDIF file not found"):
            list(processor.parse_file(tmp_path / "absent.ldif"))

    # ---- Processor loaders + reporting ----------------------------------

    def test_load_from_string_reports_success_and_updates_stats(self) -> None:
        processor = u.TapLdap.Processor()

        result = processor.load_from_string(_PERSON_LDIF, "memory.ldif")

        tm.ok(result)
        tm.that(processor.stats["total_entries"], eq=1)
        tm.that(processor.statistics()["processed_entries"], eq=1)

    def test_load_from_file_reports_success(self, tmp_path: Path) -> None:
        ldif_file = tmp_path / "load.ldif"
        ldif_file.write_text(_PERSON_LDIF, encoding="utf-8")
        processor = u.TapLdap.Processor()

        result = processor.load_from_file(ldif_file)

        tm.ok(result)
        tm.that(processor.stats["total_entries"], eq=1)

    def test_to_singer_format_wraps_loaded_entries_as_records(self) -> None:
        processor = u.TapLdap.Processor()
        tm.ok(processor.load_from_string(_PERSON_LDIF, "memory.ldif"))

        records = processor.to_singer_format("people")

        tm.that(len(records), eq=1)
        tm.that(records[0]["type"], eq="RECORD")
        tm.that(records[0]["stream"], eq="people")
        tm.that(str(records[0]["record"]).lower(), has="alice")

    def test_filters_select_loaded_entries_by_public_criteria(self) -> None:
        processor = u.TapLdap.Processor()
        tm.ok(
            processor.load_from_string(
                _PERSON_LDIF + _SECOND_LDIF,
                "memory.ldif",
            )
        )

        by_dn = processor.filter_by_dn_contains("alice")
        by_attr = processor.filter_by_attribute_exists("sn")
        by_class = processor.filter_by_objectclass("person")

        tm.that(len(by_dn), eq=1)
        tm.that(by_dn[0].dn.lower(), has="alice")
        tm.that(len(by_attr), eq=2)
        tm.that(len(by_class), eq=2)

    # ---- Validator -------------------------------------------------------

    def test_validator_reports_invalid_object_class(self) -> None:
        validator = u.TapLdap.Validator()
        entry = u.TapLdap.Entry(
            "cn=alice,dc=example,dc=com",
            {"objectClass": ["invalid class"], "cn": ["Alice"]},
        )

        result = validator.validate_entries([entry])

        tm.that(result["total_entries"], eq=1)
        tm.that(result["valid_entries"], eq=0)
        tm.that(result["invalid_entries"], eq=1)
        tm.that(
            result["errors"],
            eq=[
                "Entry cn=alice,dc=example,dc=com: Invalid objectClass 'invalid class'",
            ],
        )

    def test_validation_results_expose_valid_flag(self) -> None:
        validator = u.TapLdap.Validator()

        results = validator.validation_results()

        tm.that(results["valid"], eq=True)
        tm.that(results["errors"], eq=[])
        tm.that(results["warnings"], eq=[])

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
        tm.that(transformed.attributes["cn"], eq=["Alice"])
        tm.that(transformed.attributes["surname"], eq=["Smith"])
        tm.that(transformed.attributes["department"], eq=["Information Technology"])
        tm.that(transformed.attributes, lacks="obsolete")
        tm.that(transformed.attributes["status"], eq=["active"])
        tm.that(transformed.change_type, eq="modify")
        tm.that(transformed.controls, eq=["control-a"])
        # Source entry is left untouched (immutability of the transform).
        tm.that(entry.attributes, has="CN")
        tm.that(entry.attributes, has="obsolete")

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

        tm.that(transformed.attributes["uid"], eq=["1001"])
        tm.that(transformed.attributes["status"], eq=["active"])

    def test_transform_entry_without_rules_is_identity_copy(self) -> None:
        transformer = u.TapLdap.Transformer()
        entry = u.TapLdap.Entry(
            "cn=alice,dc=example,dc=com",
            {"cn": ["alice"], "objectClass": ["person"]},
        )

        transformed = transformer.transform_entry(entry)

        assert transformed is not entry
        tm.that(transformed.attributes["cn"], eq=["alice"])
        tm.that(transformed.dn, eq=entry.dn)


__all__ = ["TestsFlextTapLdapLdifProcessor"]
