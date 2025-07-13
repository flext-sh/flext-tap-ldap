"""Tests for LDIF stream functionality.

from __future__ import annotations

from textwrap import dedent
from typing import TYPE_CHECKING

from flext_tap_ldap.ldif_stream import LDIFAnalysisStream
from flext_tap_ldap.ldif_stream import LDIFStream
from flext_tap_ldap.tap import TapLDAP

if TYPE_CHECKING:
            from pathlib import Path


class TestLDIFStream:
         """Test LDIF stream functionality."""

    def create_test_tap(self, config:
        dict) -> TapLDAP:
        tap = TapLDAP()
        tap._config = config
        return tap

    def test_ldif_stream_initialization(self) -> None:
        config = {
            "host": "localhost",
            "base_dn": "dc=example,dc=com",
            "enable_ldif_streams": True,
        }
        tap = self.create_test_tap(config)

        stream = LDIFStream(tap)

        assert stream.name == "ldif_entries"
        assert stream.tap_name == "tap-ldap"
        assert stream.primary_keys == ["dn", "source_file"]
        assert stream.replication_key == "processing_timestamp"

    def test_ldif_stream_get_ldif_files_from_list(self, tmp_path:
        Path) -> None:
        # Create test LDIF files
        ldif1 = tmp_path / "test1.ldif"
        ldif1.write_text("dn: cn =test1,dc=example,dc=com\ncn: test1\n")

        ldif2 = tmp_path / "test2.ldif"
        ldif2.write_text("dn: cn =test2,dc=example,dc=com\ncn: test2\n")

        config = {
            "host": "localhost",
            "base_dn": "dc=example,dc=com",
            "enable_ldif_streams": True,
            "ldif_files": [str(ldif1), str(ldif2)],
        }
        tap = self.create_test_tap(config)
        stream = LDIFStream(tap)

        files = stream._get_ldif_files()

        assert len(files) == 2
        assert ldif1 in files
        assert ldif2 in files

    def test_ldif_stream_get_ldif_files_from_directory(self, tmp_path:
        Path) -> None:
        # Create test LDIF files in directory
        (tmp_path / "file1.ldif").write_text(
            "dn: cn =file1,dc=example,dc=com\ncn: file1\n",
        )
        (tmp_path / "file2.ldif").write_text(
            "dn: cn =file2,dc=example,dc=com\ncn: file2\n",
        )
        (tmp_path / "other.txt").write_text("not an ldif file"):

        config = {
            "host":
             "localhost",
            "base_dn": "dc=example,dc=com",
            "enable_ldif_streams": True,
            "ldif_directory": str(tmp_path),
        }
        tap = self.create_test_tap(config)
        stream = LDIFStream(tap)

        files = stream._get_ldif_files()

        assert len(files) == 2
        file_names = [f.name for f in files]
        assert "file1.ldif" in file_names
        assert "file2.ldif" in file_names
        assert "other.txt" not in file_names

    def test_ldif_stream_process_records(self, tmp_path:
            Path) -> None:
        ldif_content = dedent(
            """
            dn: cn =john,ou=users,dc=example,dc=com
            cn: john
            objectClass: person
            objectClass: inetOrgPerson
            mail: john@example.com

            dn: cn =jane,ou=users,dc=example,dc=com
            cn: jane
            objectClass: person
            mail: jane@example.com
        ,"""
        ).strip()

        ldif_file = tmp_path / "test.ldif"
        ldif_file.write_text(ldif_content)

        config = {
            "host": "localhost",
            "base_dn": "dc=example,dc=com",
            "enable_ldif_streams": True,
            "ldif_files": [str(ldif_file)],
            "migration_batch": "test_batch",
        }
        tap = self.create_test_tap(config)
        stream = LDIFStream(tap)

        records = list(stream.get_records())

        assert len(records) == 2

        # Check first record
        record1 = records[0]
        assert record1["dn"] == "cn=john,ou=users,dc=example,dc=com"
        assert record1["source_file"] == str(ldif_file)
        assert record1["entry_type"] == "user"  # Should classify as user
        assert "person" in record1["object_classes"]
        assert "inetOrgPerson" in record1["object_classes"]
        assert record1["attributes"]["cn"] == ["john"]
        assert record1["attributes"]["mail"] == ["john@example.com"]
        assert record1["validation_status"] == "valid"
        assert record1["migration_batch"] == "test_batch"
        assert record1["hierarchy_level"] > 0

        # Check second record
        record2 = records[1]
        assert record2["dn"] == "cn=jane,ou=users,dc=example,dc=com"
        assert record2["entry_type"] == "user"

    def test_ldif_stream_classify_entry_types(self) -> None:
        config = {
            "host": "localhost",
            "base_dn": "dc=example,dc=com",
            "enable_ldif_streams": True,
        }
        tap = self.create_test_tap(config)
        stream = LDIFStream(tap)

        # Test user classification
        assert stream._classify_entry_type(["person", "inetOrgPerson"]) == "user"
        assert stream._classify_entry_type(["person"]) == "user"

        # Test group classification
        assert stream._classify_entry_type(["groupOfNames"]) == "group"
        assert stream._classify_entry_type(["groupOfUniqueNames"]) == "group"

        # Test OU classification
        assert (
            stream._classify_entry_type(["organizationalUnit"]) == "organizational_unit"
        )

        # Test Oracle-specific classifications
        assert stream._classify_entry_type(["orclUser"]) == "oracle_user"
        assert stream._classify_entry_type(["orclGroup"]) == "oracle_group"
        assert stream._classify_entry_type(["orclContext"]) == "oracle_context"

        # Test other
        assert stream._classify_entry_type(["unknownClass"]) == "other"

    def test_ldif_stream_error_handling(self, tmp_path:
        Path) -> None:
        # Create LDIF with some invalid content
        ldif_content = dedent(
            """
            dn: cn =valid,dc=example,dc=com
            cn: valid
            objectClass =another_valid,dc=example,dc=com
            cn: another_valid
            objectClass: person
        ,"""
        ).strip()

        ldif_file = tmp_path / "test_with_errors.ldif"
        ldif_file.write_text(ldif_content)

        config = {
            "host": "localhost",
            "base_dn": "dc=example,dc=com",
            "enable_ldif_streams": True,
            "ldif_files": [str(ldif_file)],
            "ldif_ignore_errors": True,
            "ldif_ignore_entry_errors": True,
        }
        tap = self.create_test_tap(config)
        stream = LDIFStream(tap)

        records = list(stream.get_records())

        # Should get valid records despite errors
        assert len(records) >= 1  # At least the valid entries
        assert stream.stats["errors"]  # Should have recorded errors


class TestLDIFAnalysisStream:
         """Test LDIF analysis stream functionality."""

    def create_test_tap(self, config:
        dict) -> TapLDAP:
        tap = TapLDAP()
        tap._config = config
        return tap

    def test_ldif_analysis_stream_initialization(self) -> None:
        config = {
            "host": "localhost",
            "base_dn": "dc=example,dc=com",
            "enable_ldif_streams": True,
        }
        tap = self.create_test_tap(config)

        stream = LDIFAnalysisStream(tap)

        assert stream.name == "ldif_analysis"
        assert stream.primary_keys == ["source_file"]

    def test_ldif_analysis_stream_analyze_file(self, tmp_path:
        Path) -> None:
        ldif_content = dedent(
            """
            dn: dc =example,dc=com
            dc: example
            objectClass =users,dc=example,dc=com
            ou: users
            objectClass =john,ou=users,dc=example,dc=com
            cn: john
            objectClass: person
            objectClass: inetOrgPerson
            mail: john@example.com

            dn: cn =jane,ou=users,dc=example,dc=com
            cn: jane
            objectClass: person
            mail: jane@example.com

            dn: cn =REDACTED_LDAP_BIND_PASSWORDs,ou=groups,dc=example,dc=com
            cn: REDACTED_LDAP_BIND_PASSWORDs
            objectClass =john,ou=users,dc=example,dc=com
        ,"""
        ).strip()

        ldif_file = tmp_path / "analysis_test.ldif"
        ldif_file.write_text(ldif_content)

        config = {
            "host": "localhost",
            "base_dn": "dc=example,dc=com",
            "enable_ldif_streams": True,
            "ldif_files": [str(ldif_file)],
        }
        tap = self.create_test_tap(config)
        stream = LDIFAnalysisStream(tap)

        records = list(stream.get_records())

        assert len(records) == 1
        analysis = records[0]

        assert analysis["source_file"] == str(ldif_file)
        assert analysis["total_entries"] == 5
        assert analysis["file_size_bytes"] > 0

        # Check entry type analysis
        entry_types = analysis["entry_types"]
        assert entry_types["user"] == 2  # john and jane
        assert entry_types["group"] == 1  # REDACTED_LDAP_BIND_PASSWORDs
        assert entry_types["organizational_unit"] == 1  # users
        assert entry_types["domain"] == 1  # example.com

        # Check object class analysis
        object_classes = analysis["object_classes"]
        assert object_classes["person"] == 2
        assert object_classes["inetOrgPerson"] == 1
        assert object_classes["groupOfNames"] == 1
        assert object_classes["organizationalUnit"] == 1
        assert object_classes["domain"] == 1

        # Check validation summary
        validation = analysis["validation_summary"]
        assert validation["valid_entries"] >= 0
        assert validation["errors"] >= 0
        assert validation["warnings"] >= 0

        # Check attributes summary
        attributes = analysis["attributes_summary"]
        assert attributes["total_attributes"] > 0
        assert "most_common" in attributes

        # Should have recommendations
        assert isinstance(analysis["recommendations"], list)

    def test_ldif_analysis_recommendations(self, tmp_path:
        Path) -> None:
        # Create LDIF with Oracle-specific objects
        ldif_content = dedent(
            """
            dn: cn =oracle_user,ou=users,dc=example,dc=com
            cn: oracle_user
            objectClass =oracle_group,ou=groups,dc=example,dc=com
            cn: oracle_group
            objectClass: orclGroup
        ,"""
        ).strip()

        ldif_file = tmp_path / "oracle_test.ldif"
        ldif_file.write_text(ldif_content)

        config = {
            "host": "localhost",
            "base_dn": "dc=example,dc=com",
            "enable_ldif_streams": True,
            "ldif_files": [str(ldif_file)],
        }
        tap = self.create_test_tap(config)
        stream = LDIFAnalysisStream(tap)

        records = list(stream.get_records())
        analysis = records[0]

        recommendations = analysis["recommendations"]

        # Should detect Oracle objects
        oracle_recommendation = any("Oracle-specific" in rec for rec in recommendations)
        assert oracle_recommendation

    def test_ldif_analysis_large_dataset_recommendations(self, tmp_path:
            Path) -> None:
        config = {
            "host": "localhost",
            "base_dn": "dc=example,dc=com",
            "enable_ldif_streams": True,
        }
        tap = self.create_test_tap(config)
        stream = LDIFAnalysisStream(tap)

        # Simulate large user count
        entry_types = {"user": 15000, "group": 100}
        object_classes = {"person": 15000, "groupOfNames": 100}
        recommendations = stream._generate_recommendations(
            entry_types,
            object_classes,
            15100,
            0,
        )

        # Should recommend batch processing for large datasets
        batch_recommendation = any("batch processing" in rec for rec in recommendations)
        assert batch_recommendation


class TestTapLDAPLDIFIntegration:
             """Test integration of LDIF streams with TapLDAP."""

    def test_tap_discovers_ldif_streams_when_enabled(self) -> None:
        config = {
            "host": "localhost",
            "base_dn": "dc=example,dc=com",
            "enable_ldif_streams": True,
        }

        tap = TapLDAP()
        tap._config = config

        streams = tap.discover_streams()
        stream_names = [stream.name for stream in streams]

        assert "ldif_entries" in stream_names
        assert "ldif_analysis" in stream_names

    def test_tap_discovers_standard_streams_when_ldif_disabled(self) -> None:
            config = {
            "host": "localhost",
            "base_dn": "dc=example,dc=com",
            "enable_ldif_streams": False,
        }

        tap = TapLDAP()
        tap._config = config

        streams = tap.discover_streams()
        stream_names = [stream.name for stream in streams]

        assert "users" in stream_names
        assert "groups" in stream_names
        assert "organizational_units" in stream_names
        assert "schema" in stream_names
        assert "ldif_entries" not in stream_names
        assert "ldif_analysis" not in stream_names
