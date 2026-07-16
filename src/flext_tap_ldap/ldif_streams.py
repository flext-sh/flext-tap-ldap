"""FLEXT FlextMeltanoAbstractions LDAP - LDIF stream processing."""

from __future__ import annotations

from collections.abc import (
    Iterable,
    Iterator,
)
from pathlib import Path
from typing import ClassVar

from flext_ldif import ldif

from flext_meltano.services.abstractions import FlextMeltanoAbstractions
from flext_tap_ldap import c, p, r, t, u


class FlextTapLdapLdifStreams:
    """LDIF stream processing container with nested stream classes.

    Consolidates all LDIF stream functionality following FlextTapLdap[Module] pattern.
    """

    @staticmethod
    def _as_object_list(
        value: t.JsonValue,
    ) -> t.SequenceOf[t.JsonMapping]:
        try:
            if not isinstance(value, (dict, list)):
                return []
            result = t.json_mapping_sequence_adapter().validate_python(value)
            return [dict(item) for item in result]
        except c.ValidationError as exc:
            u.fetch_logger(__name__).warning(
                "Invalid object list value ignored: %s",
                exc,
            )
            return []

    @staticmethod
    def _as_counter_map(value: t.JsonValue) -> t.HeaderMapping:
        try:
            if not isinstance(value, dict):
                return {}
            return t.header_mapping_adapter().validate_python(value)
        except c.ValidationError as exc:
            u.fetch_logger(__name__).warning(
                "Invalid counter map value ignored: %s",
                exc,
            )
            return {}

    class LdifStream:
        """LDIF stream using flext-ldif for ALL processing.

        Implements the inherited Singer stream protocol.
        """

        primary_keys: ClassVar[t.StrSequence] = ["dn"]
        # NOTE (multi-agent): mro-rn88 — declare the tap config attribute (set in __init__).
        _config: t.JsonMapping

        def __init__(self, tap: FlextMeltanoAbstractions) -> None:
            """Initialize LDIF stream with library delegation."""
            self.name = "ldif_entries"
            self.tap_stream_id = "ldif_entries"
            self.tap = tap
            # NOTE (multi-agent): mro-rn88 — retain the validated tap config; methods read
            # self._config.get(...) (was an undefined bare `settings`).
            self._config: t.JsonMapping = t.Cli.JSON_MAPPING_ADAPTER.validate_python(
                getattr(tap, "tap_config", {}),
            )
            self._ldif_api = ldif()
            self._logger_instance: p.Logger | None = None
            self.schema: t.JsonMapping = {
                "type": "object",
                "properties": {
                    "dn": {"type": "string", "description": "Distinguished Name"},
                    "entry_type": {
                        "type": "string",
                        "description": "Entry type classification",
                    },
                    "object_classes": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Object classes",
                    },
                    "attributes": {
                        "type": "object",
                        "description": "Entry attributes",
                    },
                },
            }

        def get_records(
            self,
            context: t.JsonMapping | None = None,
        ) -> Iterator[t.JsonMapping]:
            """Get LDIF records using flext-ldif processing."""
            _ = context
            self.logger.info("Processing LDIF files using flext-ldif library")
            raw_files = self._config.get("ldif_files", [])
            ldif_files = FlextTapLdapLdifStreams._as_object_list(raw_files)
            ldif_directory = self._config.get("ldif_directory")
            if ldif_files:
                for ldif_file in ldif_files:
                    yield from self._process_ldif_file(str(ldif_file))
            elif ldif_directory:
                for discovered_file in self._discover_ldif_files(str(ldif_directory)):
                    yield from self._process_ldif_file(str(discovered_file))
            else:
                yield from self._process_ldap_directory()

        def _classify_entry_type(self, object_classes: t.StrSequence) -> str:
            """Classify entry type by simple objectClass heuristics."""
            lowered = {oc.lower() for oc in object_classes}
            if "inetorgperson" in lowered or "person" in lowered:
                return "user"
            if "groupofnames" in lowered or "group" in lowered:
                return "group"
            if "organizationalunit" in lowered or "ou" in lowered:
                return "ou"
            return "other"

        def _convert_entry_to_record(
            self,
            flext_entry: p.Ldif.Entry,
        ) -> t.JsonMapping:
            """Convert flext-ldif entry to Singer record."""
            dn_value = flext_entry.dn.value if flext_entry.dn is not None else ""
            attrs = flext_entry.attributes
            object_classes: t.StrSequence = []
            entry_type = "other"
            entry_attrs: t.JsonMapping = {}
            if attrs is not None:
                object_classes = attrs.get("objectClass")
                entry_type = self._classify_entry_type(object_classes)
                entry_attrs = {
                    attr_name: u.normalize_to_json_value(list(attr_values))
                    for attr_name, attr_values in attrs.attributes.items()
                }
            return t.Cli.JSON_MAPPING_ADAPTER.validate_python({
                "dn": dn_value,
                "entry_type": entry_type,
                "object_classes": list(object_classes),
                "attributes": entry_attrs,
            })

        def _discover_ldif_files(self, ldif_directory: str) -> t.SequenceOf[Path]:
            directory = Path(ldif_directory)
            if not directory.exists() or not directory.is_dir():
                self.logger.warning("LDIF directory not found: %s", ldif_directory)
                return []
            pattern_raw = self._config.get("ldif_file_pattern", "*.ldif")
            pattern = pattern_raw if isinstance(pattern_raw, str) else "*.ldif"
            files = [path for path in directory.rglob(pattern) if path.is_file()]
            files.sort()
            return files

        def _normalize_object_classes(
            self,
            object_classes: t.JsonValue,
        ) -> t.StrSequence:
            if isinstance(object_classes, str):
                return [object_classes]
            object_values = FlextTapLdapLdifStreams._as_object_list(object_classes)
            if object_values:
                return [str(value) for value in object_values]
            return []

        def _process_ldap_directory(self) -> Iterator[t.JsonMapping]:
            host_raw = self._config.get("ldap_host")
            base_dn_raw = self._config.get("ldap_base_dn")
            if not isinstance(host_raw, str) or not host_raw:
                return iter(())
            if not isinstance(base_dn_raw, str) or not base_dn_raw:
                return iter(())
            self.logger.warning(
                "LDAP directory traversal is disabled; provide LDIF files or ldif_directory",
            )
            return iter(())

        def _process_ldif_file(
            self,
            ldif_file: str,
        ) -> Iterable[t.JsonMapping]:
            """Process single LDIF file using flext-ldif."""
            self.logger.info("Processing LDIF file: %s", ldif_file)
            try:
                result = self._parse_ldif_file(ldif_file)
            except c.Meltano.SINGER_SAFE_EXCEPTIONS:
                self.logger.exception("Error processing LDIF file %s", ldif_file)
                return
            if result.success and result.value.entries:
                for entry in result.value.entries:
                    yield self._convert_entry_to_record(entry)
                return
            self.logger.error(
                f"Failed to parse LDIF file {ldif_file}: {result.error}",
            )

        def _parse_ldif_file(self, ldif_file: str) -> p.Result[p.Ldif.ParseResponse]:
            """Parse one LDIF file through the LDIF facade."""
            read = u.Cli.files_read_text(Path(ldif_file))
            if read.failure:
                return r[p.Ldif.ParseResponse].fail(
                    f"Failed to read LDIF file {ldif_file}: {read.error}",
                )
            return self._ldif_api.parse_ldif(read.value)

    class LdifAnalysisStream:
        """LDIF analysis stream using flext-ldif for ALL analysis.

        Implements the inherited Singer stream protocol.
        """

        primary_keys: ClassVar[t.StrSequence] = ["analysis_id"]
        # NOTE (multi-agent): mro-rn88 — declare the tap config attribute (set in __init__).
        _config: t.JsonMapping

        def __init__(self, tap: FlextMeltanoAbstractions) -> None:
            """Initialize LDIF analysis stream with library delegation."""
            self.name = "ldif_analysis"
            self.tap_stream_id = "ldif_analysis"
            self.tap = tap
            # NOTE (multi-agent): mro-rn88 — retain the validated tap config (see above).
            self._config: t.JsonMapping = t.Cli.JSON_MAPPING_ADAPTER.validate_python(
                getattr(tap, "tap_config", {}),
            )
            self._ldif_api = ldif()
            self._logger_instance: p.Logger | None = None
            self.schema: t.JsonMapping = {
                "type": "object",
                "properties": {
                    "analysis_id": {
                        "type": "string",
                        "description": "Analysis identifier",
                    },
                    "total_entries": {
                        "type": "integer",
                        "description": "Total number of entries",
                    },
                    "entry_types": {
                        "type": "object",
                        "description": "Count by entry type",
                    },
                    "object_classes": {
                        "type": "object",
                        "description": "Count by object class",
                    },
                },
            }

        def get_records(
            self,
            context: t.JsonMapping | None = None,
        ) -> Iterator[t.JsonMapping]:
            """Get analysis records using flext-ldif analysis capabilities."""
            _ = context
            self.logger.info("Generating LDIF analysis using flext-ldif library")
            raw_files = self._config.get("ldif_files", [])
            ldif_files = FlextTapLdapLdifStreams._as_object_list(raw_files)
            ldif_directory = self._config.get("ldif_directory")
            try:
                summary = self._build_analysis_summary(ldif_files, ldif_directory)
            except c.Meltano.SINGER_SAFE_EXCEPTIONS:
                self.logger.exception("LDIF analysis error")
                yield t.Cli.JSON_MAPPING_ADAPTER.validate_python({
                    "analysis_id": "ldif_summary_error",
                    "total_entries": 0,
                    "entry_types": {},
                    "object_classes": {},
                })
                return
            yield summary

        def _build_analysis_summary(
            self,
            ldif_files: t.SequenceOf[t.JsonMapping],
            ldif_directory: t.JsonValue,
        ) -> t.JsonMapping:
            """Build the aggregate LDIF analysis summary."""
            total_entries = 0
            entry_types: t.MutableIntMapping = {}
            object_classes: t.MutableIntMapping = {}
            if ldif_files:
                stats_items = (
                    self._analyze_ldif_file(
                        str(ldif_file_map.get("path", ldif_file_map.get("file", ""))),
                    )
                    for ldif_file_map in ldif_files
                    if str(ldif_file_map.get("path", ldif_file_map.get("file", "")))
                )
            elif ldif_directory:
                stats_items = (
                    self._analyze_ldif_file(str(discovered_file))
                    for discovered_file in self._discover_ldif_files(
                        str(ldif_directory),
                    )
                )
            else:
                stats_items = iter(())
            for stats in stats_items:
                total_count = stats.get("total_entries", 0)
                if isinstance(total_count, int):
                    total_entries += total_count
                self._merge_counter_map(entry_types, stats.get("entry_types", {}))
                self._merge_counter_map(
                    object_classes,
                    stats.get("object_classes", {}),
                )
            return t.Cli.JSON_MAPPING_ADAPTER.validate_python({
                "analysis_id": "ldif_summary",
                "total_entries": total_entries,
                "entry_types": dict(entry_types),
                "object_classes": dict(object_classes),
            })

        @staticmethod
        def _merge_counter_map(
            target: t.MutableIntMapping,
            raw_counts: t.JsonValue,
        ) -> None:
            """Merge one raw counter mapping into an integer counter."""
            counts = FlextTapLdapLdifStreams._as_counter_map(raw_counts)
            for key, count in counts.items():
                target[key] = target.get(key, 0) + int(count)

        def _analyze_ldif_file(self, ldif_file: str) -> t.JsonMapping:
            """Analyze single LDIF file using flext-ldif."""
            self.logger.info("Analyzing LDIF file: %s", ldif_file)
            try:
                return self._analyze_ldif_file_payload(ldif_file)
            except c.Meltano.SINGER_SAFE_EXCEPTIONS:
                self.logger.exception("Error analyzing LDIF file %s", ldif_file)
                empty_dict: t.IntMapping = {}
                return t.Cli.JSON_MAPPING_ADAPTER.validate_python({
                    "total_entries": 0,
                    "entry_types": dict(empty_dict),
                    "object_classes": dict(empty_dict),
                })

        def _analyze_ldif_file_payload(self, ldif_file: str) -> t.JsonMapping:
            """Analyze one LDIF file without owning the exception boundary."""
            read = u.Cli.files_read_text(Path(ldif_file))
            if read.failure:
                self.logger.error(
                    "Failed to read LDIF file %s: %s",
                    ldif_file,
                    read.error,
                )
                return self._empty_analysis_payload()
            result: p.Result[p.Ldif.ParseResponse] = self._ldif_api.parse_ldif(
                read.value,
            )
            if result.success and result.value.entries:
                entry_types: t.MutableIntMapping = {}
                object_classes: t.MutableIntMapping = {}
                for entry in result.value.entries:
                    if entry.attributes is None:
                        continue
                    oc_list: t.StrSequence = entry.attributes.get("objectClass")
                    oc_strs = list(oc_list)
                    entry_type = self._classify_entry_type(oc_strs)
                    entry_types[entry_type] = entry_types.get(entry_type, 0) + 1
                    for oc in oc_strs:
                        object_classes[oc] = object_classes.get(oc, 0) + 1
                return t.Cli.JSON_MAPPING_ADAPTER.validate_python({
                    "total_entries": len(result.value.entries),
                    "entry_types": dict(entry_types),
                    "object_classes": dict(object_classes),
                })
            self.logger.error(
                f"Failed to analyze LDIF file {ldif_file}: {result.error}",
            )
            return self._empty_analysis_payload()

        @staticmethod
        def _empty_analysis_payload() -> t.JsonMapping:
            """Empty LDIF analysis payload."""
            empty: t.IntMapping = {}
            return t.Cli.JSON_MAPPING_ADAPTER.validate_python({
                "total_entries": 0,
                "entry_types": dict(empty),
                "object_classes": dict(empty),
            })

        def _classify_entry_type(self, object_classes: t.StrSequence) -> str:
            """Classify entry type by simple objectClass heuristics."""
            lowered = {oc.lower() for oc in object_classes}
            if "inetorgperson" in lowered or "person" in lowered:
                return "user"
            if "groupofnames" in lowered or "group" in lowered:
                return "group"
            if "organizationalunit" in lowered or "ou" in lowered:
                return "ou"
            return "other"

        def _discover_ldif_files(self, ldif_directory: str) -> t.SequenceOf[Path]:
            directory = Path(ldif_directory)
            if not directory.exists() or not directory.is_dir():
                self.logger.warning("LDIF directory not found: %s", ldif_directory)
                return []
            pattern_raw = self._config.get("ldif_file_pattern", "*.ldif")
            pattern = pattern_raw if isinstance(pattern_raw, str) else "*.ldif"
            files = [path for path in directory.rglob(pattern) if path.is_file()]
            files.sort()
            return files


__all__: list[str] = ["FlextTapLdapLdifStreams"]
