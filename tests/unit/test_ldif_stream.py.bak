"""Behavioral tests for LDIF stream functionality.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest
from flext_tests import tm

from flext_tap_ldap import t
from flext_tap_ldap.ldif_streams import FlextTapLdapLdifStreams
from flext_tap_ldap.tap import FlextTapLdapTap

USER_LDIF = """dn: uid=jdoe,ou=people,dc=example,dc=com
objectClass: inetOrgPerson
cn: John Doe
sn: Doe
uid: jdoe

dn: cn=admins,ou=groups,dc=example,dc=com
objectClass: groupOfNames
cn: admins
member: uid=jdoe,ou=people,dc=example,dc=com
"""


class TestsFlextTapLdapLdifStream:
    """Contract tests for LDIF streams exercised through their public API."""

    @pytest.fixture
    def make_tap(self) -> Callable[[t.MutableConfigurationMapping], FlextTapLdapTap]:
        """Build a tap configured with the given tap_config mapping."""

        def _build(config: t.MutableConfigurationMapping) -> FlextTapLdapTap:
            tap = FlextTapLdapTap()
            tap.tap_config = dict(config)
            return tap

        return _build

    @pytest.fixture
    def ldif_dir(self, tmp_path: Path) -> Path:
        """Create a directory holding one LDIF file with a user and a group."""
        ldif_path = tmp_path / "entries.ldif"
        ldif_path.write_text(USER_LDIF, encoding="utf-8")
        return tmp_path

    def test_ldif_stream_exposes_singer_identity_contract(
        self,
        make_tap: Callable[[t.MutableConfigurationMapping], FlextTapLdapTap],
    ) -> None:
        """LdifStream advertises its Singer stream identity and primary key."""
        stream = FlextTapLdapLdifStreams.LdifStream(make_tap({}))

        tm.that(stream.name, eq="ldif_entries")
        tm.that(stream.tap_stream_id, eq="ldif_entries")
        tm.that(stream.primary_keys, eq=["dn"])
        tm.that(stream.schema["type"], eq="object")

    def test_analysis_stream_exposes_singer_identity_contract(
        self,
        make_tap: Callable[[t.MutableConfigurationMapping], FlextTapLdapTap],
    ) -> None:
        """LdifAnalysisStream advertises its own identity and primary key."""
        stream = FlextTapLdapLdifStreams.LdifAnalysisStream(make_tap({}))

        tm.that(stream.name, eq="ldif_analysis")
        tm.that(stream.tap_stream_id, eq="ldif_analysis")
        tm.that(stream.primary_keys, eq=["analysis_id"])
        tm.that(stream.schema["type"], eq="object")

    def test_get_records_emits_one_record_per_ldif_entry(
        self,
        make_tap: Callable[[t.MutableConfigurationMapping], FlextTapLdapTap],
        ldif_dir: Path,
    ) -> None:
        """Every parsed LDIF entry surfaces as a Singer record via get_records."""
        stream = FlextTapLdapLdifStreams.LdifStream(
            make_tap({"ldif_directory": str(ldif_dir)}),
        )

        records = list(stream.get_records())

        dns = {record["dn"] for record in records}
        tm.that(
            dns,
            eq={
                "uid=jdoe,ou=people,dc=example,dc=com",
                "cn=admins,ou=groups,dc=example,dc=com",
            },
        )

    def test_get_records_projects_expected_record_fields(
        self,
        make_tap: Callable[[t.MutableConfigurationMapping], FlextTapLdapTap],
        ldif_dir: Path,
    ) -> None:
        """Each record carries the documented public fields with real values."""
        stream = FlextTapLdapLdifStreams.LdifStream(
            make_tap({"ldif_directory": str(ldif_dir)}),
        )

        user = next(
            record
            for record in stream.get_records()
            if record["dn"] == "uid=jdoe,ou=people,dc=example,dc=com"
        )

        tm.that(set(user), eq={"dn", "entry_type", "object_classes", "attributes"})
        tm.that(user["entry_type"], eq="user")
        tm.that(user["object_classes"], eq=["inetOrgPerson"])
        tm.that(user["attributes"], is_=dict)

    @pytest.mark.parametrize(
        ("dn", "object_class", "expected_type"),
        [
            ("uid=p,dc=x", "inetOrgPerson", "user"),
            ("cn=g,dc=x", "groupOfNames", "group"),
            ("ou=o,dc=x", "organizationalUnit", "ou"),
            ("cn=d,dc=x", "device", "other"),
        ],
    )
    def test_get_records_classifies_entry_type_from_object_class(
        self,
        make_tap: Callable[[t.MutableConfigurationMapping], FlextTapLdapTap],
        tmp_path: Path,
        dn: str,
        object_class: str,
        expected_type: str,
    ) -> None:
        """entry_type is derived from the entry objectClass heuristics."""
        (tmp_path / "one.ldif").write_text(
            f"dn: {dn}\nobjectClass: {object_class}\ncn: x\n",
            encoding="utf-8",
        )
        stream = FlextTapLdapLdifStreams.LdifStream(
            make_tap({"ldif_directory": str(tmp_path)}),
        )

        records = list(stream.get_records())

        tm.that([record["entry_type"] for record in records], eq=[expected_type])

    def test_get_records_is_repeatable(
        self,
        make_tap: Callable[[t.MutableConfigurationMapping], FlextTapLdapTap],
        ldif_dir: Path,
    ) -> None:
        """Iterating get_records twice yields the same records (no state drift)."""
        stream = FlextTapLdapLdifStreams.LdifStream(
            make_tap({"ldif_directory": str(ldif_dir)}),
        )

        first = [record["dn"] for record in stream.get_records()]
        second = [record["dn"] for record in stream.get_records()]

        tm.that(first, eq=second)

    def test_get_records_yields_nothing_without_ldif_sources(
        self,
        make_tap: Callable[[t.MutableConfigurationMapping], FlextTapLdapTap],
    ) -> None:
        """With no LDIF files or directory, no LDIF records are produced."""
        stream = FlextTapLdapLdifStreams.LdifStream(make_tap({}))

        tm.that(list(stream.get_records()), eq=[])

    def test_get_records_yields_nothing_for_empty_directory(
        self,
        make_tap: Callable[[t.MutableConfigurationMapping], FlextTapLdapTap],
        tmp_path: Path,
    ) -> None:
        """A directory with no LDIF files produces no records."""
        stream = FlextTapLdapLdifStreams.LdifStream(
            make_tap({"ldif_directory": str(tmp_path)}),
        )

        tm.that(list(stream.get_records()), eq=[])

    def test_analysis_summary_aggregates_entry_counts(
        self,
        make_tap: Callable[[t.MutableConfigurationMapping], FlextTapLdapTap],
        ldif_dir: Path,
    ) -> None:
        """Analysis stream emits one summary counting entries and types."""
        stream = FlextTapLdapLdifStreams.LdifAnalysisStream(
            make_tap({"ldif_directory": str(ldif_dir)}),
        )

        summaries = list(stream.get_records())

        tm.that(len(summaries), eq=1)
        summary = summaries[0]
        tm.that(summary["analysis_id"], eq="ldif_summary")
        tm.that(summary["total_entries"], eq=2)
        tm.that(summary["entry_types"], eq={"user": 1, "group": 1})
        tm.that(
            summary["object_classes"],
            eq={
                "inetOrgPerson": 1,
                "groupOfNames": 1,
            },
        )

    def test_analysis_summary_reports_zero_without_sources(
        self,
        make_tap: Callable[[t.MutableConfigurationMapping], FlextTapLdapTap],
    ) -> None:
        """With no sources the analysis summary reports an empty aggregate."""
        stream = FlextTapLdapLdifStreams.LdifAnalysisStream(make_tap({}))

        summaries = list(stream.get_records())

        tm.that(len(summaries), eq=1)
        summary = summaries[0]
        tm.that(summary["analysis_id"], eq="ldif_summary")
        tm.that(summary["total_entries"], eq=0)
        tm.that(summary["entry_types"], eq={})
        tm.that(summary["object_classes"], eq={})


__all__: list[str] = ["TestsFlextTapLdapLdifStream"]
