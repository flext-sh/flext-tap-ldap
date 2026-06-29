"""Tests for LDIF processor functionality.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock

import pytest

from flext_tap_ldap.ldif_streams import FlextTapLdapLdifStreams
from tests.typings import t
from tests.utilities import u


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
