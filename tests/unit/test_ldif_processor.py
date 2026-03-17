"""Tests for LDIF processor functionality.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import types
from pathlib import Path
from typing import Self
from unittest.mock import Mock

import pytest

from flext_tap_ldap import FlextTapLdapLdifStreams, FlextTapLdapProcessor
from flext_tap_ldap.processor import Entry, Transformer
from tests import t


class TestLdifProcessor:
    """Placeholder tests pending refactoring with proper FlextTapLdapProcessor API."""

    def test_placeholder(self) -> None:
        """Placeholder test to satisfy pytest collection."""
        assert FlextTapLdapProcessor is not None

    def test_ldif_directory_processing_traverses_ldif_files(
        self, tmp_path: Path
    ) -> None:
        nested = tmp_path / "nested"
        nested.mkdir()
        file_a = tmp_path / "a.ldif"
        file_b = nested / "b.ldif"
        ignored = nested / "ignore.txt"
        file_a.write_text("dn: cn=a,dc=example,dc=com\n", encoding="utf-8")
        file_b.write_text("dn: cn=b,dc=example,dc=com\n", encoding="utf-8")
        ignored.write_text("not-ldif", encoding="utf-8")
        stream = object.__new__(FlextTapLdapLdifStreams.LdifStream)
        stream.tap = Mock()
        stream.tap.config = {
            "ldif_directory": str(tmp_path),
            "ldif_file_pattern": "*.ldif",
        }
        seen: list[str] = []

        def _process(ldif_file: str) -> list[dict[str, object]]:
            seen.append(ldif_file)
            return [{"dn": ldif_file}]

        stream._process_ldif_file = _process
        records = list(stream.get_records())
        assert len(records) == 2
        assert set(seen) == {str(file_a), str(file_b)}

    def test_transform_entry_applies_rules(self) -> None:
        transformer = Transformer(
            transformation_rules={
                "attribute_mappings": {"CN": "cn", "sn": "surname"},
                "attribute_value_mappings": {
                    "department": {"IT": "Information Technology"}
                },
                "remove_attributes": ["obsolete"],
                "add_attributes": {"status": "active"},
            }
        )
        entry = Entry(
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

    def test_directory_processing_traverses_ldap_dit_with_mock_connection(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:

        class _FakeConnection:
            def __init__(self, *args: t.Scalar, **kwargs: t.Scalar) -> None:
                self.extend = Mock()
                self.extend.standard = Mock()
                self.extend.standard.paged_search.return_value = [
                    {
                        "type": "searchResEntry",
                        "dn": "cn=alice,dc=example,dc=com",
                        "attributes": {
                            "cn": ["alice"],
                            "objectClass": ["person", "inetOrgPerson"],
                        },
                    }
                ]

            def __enter__(self) -> Self:
                return self

            def __exit__(
                self,
                exc_type: type[BaseException] | None,
                exc: BaseException | None,
                tb: types.TracebackType | None,
            ) -> None:
                _ = exc_type
                _ = exc
                _ = tb

        monkeypatch.setattr("flext_tap_ldap.ldif_streams.Server", Mock())
        monkeypatch.setattr("flext_tap_ldap.ldif_streams.Connection", _FakeConnection)
        stream = object.__new__(FlextTapLdapLdifStreams.LdifStream)
        stream.tap = Mock()
        stream.tap.config = {
            "ldap_host": "ldap.example.com",
            "ldap_port": 389,
            "ldap_base_dn": "dc=example,dc=com",
            "ldap_bind_dn": "cn=admin,dc=example,dc=com",
            "ldap_bind_password": "secret",
            "ldap_search_filter": "(objectClass=*)",
            "ldap_page_size": 100,
        }
        records = list(stream.get_records())
        assert len(records) == 1
        assert records[0]["dn"] == "cn=alice,dc=example,dc=com"
        assert records[0]["entry_type"] == "user"

    def test_transform_entry_applies_schema_mappings(self) -> None:
        transformer = Transformer(
            transformation_rules={
                "schema_mappings": {
                    "uid": "employeeId",
                    "status": {"source": "employmentStatus", "default": "active"},
                }
            }
        )
        entry = Entry("cn=alice,dc=example,dc=com", {"employeeId": ["1001"]})
        transformed = transformer.transform_entry(entry)
        assert transformed.attributes["uid"] == ["1001"]
        assert transformed.attributes["status"] == ["active"]
