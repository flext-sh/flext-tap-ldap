"""FLEXT Tap LDAP - LDIF stream processing."""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping, MutableMapping, Sequence
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

from flext_core import FlextLogger, p, t
from flext_ldap import FlextLdapConnection, m
from flext_ldif import FlextLdif
from pydantic import ConfigDict, TypeAdapter, ValidationError

if TYPE_CHECKING:
    from flext_meltano import FlextMeltanoAbstractions as Tap

_OBJECT_LIST_ADAPTER = TypeAdapter(
    Sequence[t.ContainerValueMapping],
    config=ConfigDict(strict=False),
)
_COUNTER_MAP_ADAPTER = TypeAdapter(
    Mapping[str, int | str],
    config=ConfigDict(strict=False),
)


def _as_object_list(
    value: t.ContainerValue,
) -> Sequence[Mapping[str, t.ContainerValue]]:
    try:
        if not isinstance(value, (dict, list)):
            return []
        result = _OBJECT_LIST_ADAPTER.validate_python(value)
        return [dict(item) if isinstance(item, Mapping) else item for item in result]
    except ValidationError:
        return []


def _as_counter_map(value: t.NormalizedValue) -> Mapping[str, int | str]:
    try:
        if not isinstance(value, dict):
            return {}
        return _COUNTER_MAP_ADAPTER.validate_python(value)
    except ValidationError:
        return {}


class FlextTapLdapLdifStreams:
    """LDIF stream processing container with nested stream classes.

    Consolidates all LDIF stream functionality following FlextTapLdap[Module] pattern.
    """

    class LdifStream:
        """LDIF stream using flext-ldif for ALL processing.

        Implements FlextMeltanoProtocols.Singer.Stream protocol.
        """

        primary_keys: ClassVar[t.StrSequence] = ["dn"]

        def __init__(self, tap: Tap) -> None:
            """Initialize LDIF stream with library delegation."""
            self.name = "ldif_entries"
            self.tap_stream_id = "ldif_entries"
            self.tap = tap
            self.config: Mapping[str, t.ContainerValue] = getattr(tap, "config", {})
            self._ldif_api = FlextLdif()
            self._ldap_api = FlextLdapConnection()
            self._logger_instance: FlextLogger | None = None
            self.schema = {
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

        @property
        def logger(self) -> FlextLogger:
            """Lazy logger."""
            if self._logger_instance is None:
                self._logger_instance = FlextLogger.create_module_logger(__name__)
            return self._logger_instance

        def get_records(
            self,
            context: t.ContainerMapping | None = None,
        ) -> Iterator[t.ContainerMapping]:
            """Get LDIF records using flext-ldif processing."""
            _ = context
            self.logger.info("Processing LDIF files using flext-ldif library")
            raw_files = self.config.get("ldif_files", [])
            ldif_files = _as_object_list(raw_files)
            ldif_directory = self.config.get("ldif_directory")
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
            flext_entry: m.Ldif.Entry,
        ) -> t.ContainerMapping:
            """Convert flext-ldif entry to Singer record."""
            dn_value = flext_entry.dn.value if flext_entry.dn is not None else ""
            attrs = flext_entry.attributes
            object_classes: t.StrSequence = []
            entry_type = "other"
            entry_attrs: t.ContainerMapping = {}
            if attrs is not None:
                object_classes = attrs.get_values("objectClass")
                entry_type = self._classify_entry_type(object_classes)
                entry_attrs = dict(attrs.attributes)
            return {
                "dn": dn_value,
                "entry_type": entry_type,
                "object_classes": object_classes,
                "attributes": entry_attrs,
            }

        def _discover_ldif_files(self, ldif_directory: str) -> Sequence[Path]:
            directory = Path(ldif_directory)
            if not directory.exists() or not directory.is_dir():
                self.logger.warning("LDIF directory not found: %s", ldif_directory)
                return []
            pattern_raw = self.config.get("ldif_file_pattern", "*.ldif")
            pattern = str(pattern_raw) if isinstance(pattern_raw, str) else "*.ldif"
            files = [path for path in directory.rglob(pattern) if path.is_file()]
            files.sort()
            return files

        def _normalize_object_classes(
            self,
            object_classes: Mapping[str, t.ContainerValue],
        ) -> t.StrSequence:
            if isinstance(object_classes, str):
                return [object_classes]
            object_values = _as_object_list(object_classes)
            if object_values:
                return [str(value) for value in object_values if value is not None]
            return []

        def _process_ldap_directory(self) -> Iterator[t.ContainerMapping]:
            host_raw = self.config.get("ldap_host")
            base_dn_raw = self.config.get("ldap_base_dn")
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
        ) -> Iterable[t.ContainerMapping]:
            """Process single LDIF file using flext-ldif."""
            self.logger.info("Processing LDIF file: %s", ldif_file)
            try:
                content = Path(ldif_file).read_text(encoding="utf-8")
                result = self._ldif_api.parse(content)
                if result.is_success and result.value:
                    for entry in result.value:
                        if isinstance(entry, m.Ldif.Entry):
                            yield self._convert_entry_to_record(entry)
                else:
                    self.logger.error(
                        f"Failed to parse LDIF file {ldif_file}: {result.error}",
                    )
            except (
                ValueError,
                TypeError,
                KeyError,
                AttributeError,
                OSError,
                RuntimeError,
                ImportError,
            ):
                self.logger.exception("Error processing LDIF file %s", ldif_file)

    class LdifAnalysisStream:
        """LDIF analysis stream using flext-ldif for ALL analysis.

        Implements FlextMeltanoProtocols.Singer.Stream protocol.
        """

        primary_keys: ClassVar[t.StrSequence] = ["analysis_id"]

        def __init__(self, tap: Tap) -> None:
            """Initialize LDIF analysis stream with library delegation."""
            self.name = "ldif_analysis"
            self.tap_stream_id = "ldif_analysis"
            self.tap = tap
            self.config: Mapping[str, t.ContainerValue] = getattr(tap, "config", {})
            self._ldif_api = FlextLdif()
            self._ldap_api = FlextLdapConnection()
            self._logger_instance: p.Logger | None = None
            self.schema: t.ContainerMapping = {
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
                        "description": "Count by t.NormalizedValue class",
                    },
                },
            }

        @property
        def logger(self) -> p.Logger:
            """Lazy logger."""
            if self._logger_instance is None:
                self._logger_instance = FlextLogger.create_module_logger(__name__)
            return self._logger_instance

        def get_records(
            self,
            context: t.ContainerMapping | None = None,
        ) -> Iterator[t.ContainerMapping]:
            """Get analysis records using flext-ldif analysis capabilities."""
            _ = context
            self.logger.info("Generating LDIF analysis using flext-ldif library")
            raw_files = self.config.get("ldif_files", [])
            ldif_files = _as_object_list(raw_files)
            ldif_directory = self.config.get("ldif_directory")
            try:
                total_entries = 0
                entry_types: MutableMapping[str, int] = {}
                object_classes: MutableMapping[str, int] = {}
                if ldif_files:
                    for ldif_file in ldif_files:
                        match ldif_file:
                            case str() as ldif_file_value:
                                pass
                            case _:
                                continue
                        stats = self._analyze_ldif_file(ldif_file_value)
                        total_count = stats.get("total_entries", 0)
                        match total_count:
                            case int() as total_count_value:
                                total_entries += total_count_value
                            case _:
                                pass
                        validated_entry_types = _as_counter_map(
                            stats.get("entry_types", {}),
                        )
                        for entry_type, count in validated_entry_types.items():
                            object_count = int(count)
                            entry_types[entry_type] = (
                                entry_types.get(entry_type, 0) + object_count
                            )
                        validated_object_classes = _as_counter_map(
                            stats.get("object_classes", {}),
                        )
                        for obj_class, count in validated_object_classes.items():
                            object_count = int(count)
                            object_classes[obj_class] = (
                                object_classes.get(obj_class, 0) + object_count
                            )
                elif ldif_directory:
                    for discovered_file in self._discover_ldif_files(
                        str(ldif_directory),
                    ):
                        stats = self._analyze_ldif_file(str(discovered_file))
                        total_count = stats.get("total_entries", 0)
                        match total_count:
                            case int() as total_count_value:
                                total_entries += total_count_value
                            case _:
                                pass
                        validated_entry_types = _as_counter_map(
                            stats.get("entry_types", {}),
                        )
                        for entry_type, count in validated_entry_types.items():
                            object_count = int(count)
                            entry_types[entry_type] = (
                                entry_types.get(entry_type, 0) + object_count
                            )
                        validated_object_classes = _as_counter_map(
                            stats.get("object_classes", {}),
                        )
                        for obj_class, count in validated_object_classes.items():
                            object_count = int(count)
                            object_classes[obj_class] = (
                                object_classes.get(obj_class, 0) + object_count
                            )
                yield {
                    "analysis_id": "ldif_summary",
                    "total_entries": total_entries,
                    "entry_types": entry_types,
                    "object_classes": object_classes,
                }
            except (
                ValueError,
                TypeError,
                KeyError,
                AttributeError,
                OSError,
                RuntimeError,
                ImportError,
            ):
                self.logger.exception("LDIF analysis error")
                yield {
                    "analysis_id": "ldif_summary_error",
                    "total_entries": 0,
                    "entry_types": {},
                    "object_classes": {},
                }

        def _analyze_ldif_file(self, ldif_file: str) -> t.ContainerMapping:
            """Analyze single LDIF file using flext-ldif."""
            self.logger.info("Analyzing LDIF file: %s", ldif_file)
            try:
                content = Path(ldif_file).read_text(encoding="utf-8")
                result = self._ldif_api.parse(content)
                if result.is_success and result.value:
                    entry_types: MutableMapping[str, int] = {}
                    object_classes: MutableMapping[str, int] = {}
                    for entry in result.value:
                        if not isinstance(entry, m.Ldif.Entry):
                            continue
                        if entry.attributes is None:
                            continue
                        oc_list: t.StrSequence = entry.attributes.get_values(
                            "objectClass"
                        )
                        oc_strs = [str(oc_val) for oc_val in oc_list]
                        entry_type = self._classify_entry_type(oc_strs)
                        entry_types[entry_type] = entry_types.get(entry_type, 0) + 1
                        for oc in oc_strs:
                            object_classes[oc] = object_classes.get(oc, 0) + 1
                    return {
                        "total_entries": len(result.value),
                        "entry_types": entry_types,
                        "object_classes": object_classes,
                    }
                self.logger.error(
                    f"Failed to analyze LDIF file {ldif_file}: {result.error}",
                )
                return {"total_entries": 0, "entry_types": {}, "object_classes": {}}
            except (
                ValueError,
                TypeError,
                KeyError,
                AttributeError,
                OSError,
                RuntimeError,
                ImportError,
            ):
                self.logger.exception("Error analyzing LDIF file %s", ldif_file)
                return {"total_entries": 0, "entry_types": {}, "object_classes": {}}

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

        def _discover_ldif_files(self, ldif_directory: str) -> Sequence[Path]:
            directory = Path(ldif_directory)
            if not directory.exists() or not directory.is_dir():
                self.logger.warning("LDIF directory not found: %s", ldif_directory)
                return []
            pattern_raw = self.config.get("ldif_file_pattern", "*.ldif")
            pattern = str(pattern_raw) if isinstance(pattern_raw, str) else "*.ldif"
            files = [path for path in directory.rglob(pattern) if path.is_file()]
            files.sort()
            return files


__all__ = ["FlextTapLdapLdifStreams"]
