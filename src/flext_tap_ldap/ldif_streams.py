"""FLEXT Tap LDAP - LDIF stream processing."""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping
from pathlib import Path
from typing import ClassVar, override

from flext_core.loggings import FlextLogger
from flext_ldap import FlextLdapConnection
from flext_ldif import FlextLdif, m
from flext_meltano import (
    FlextMeltanoStream as Stream,
    FlextMeltanoTap as Tap,
    t as t_meltano,
)
from ldap3 import SUBTREE, Connection, Server
from pydantic import BaseModel

from flext_tap_ldap.constants import c
from flext_tap_ldap.typings import t

# Access Singer SDK typing through FLEXT domain namespace
typing_utils = t_meltano.Singer.Typing


class _Guards:
    @staticmethod
    def is_list(value: t.GeneralValueType) -> bool:
        return isinstance(value, list)

    @staticmethod
    def is_type(value: t.GeneralValueType, expected: type | tuple[type, ...]) -> bool:
        return isinstance(value, expected)


class _Utilities:
    Guards = _Guards

    @staticmethod
    def is_dict_like(value: t.GeneralValueType) -> bool:
        return isinstance(value, Mapping)


class _Mixins:
    @staticmethod
    def is_base_model(value: t.GeneralValueType) -> bool:
        return isinstance(value, BaseModel)


u = _Utilities
x = _Mixins


class FlextTapLdapLdifStreams:
    """LDIF stream processing container with nested stream classes.

    Consolidates all LDIF stream functionality following FlextTapLdap[Module] pattern.
    """

    class LdifStream(Stream):
        """LDIF stream using flext-ldif for ALL processing."""

        primary_keys: ClassVar[list[str]] = ["dn"]

        @override
        def __init__(self, tap: Tap) -> None:
            """Initialize LDIF stream with library delegation."""
            # Set required attributes BEFORE calling super().__init__()
            self.name = "ldif_entries"
            self.path = "/ldif_entries"
            # Store tap reference
            self.tap = tap
            # Initialize flext-ldif API for processing
            self._ldif_api = FlextLdif()
            self._ldap_api = FlextLdapConnection()
            self._logger_instance: FlextLogger | None = None
            # Define schema
            schema = typing_utils.PropertiesList(
                typing_utils.Property(
                    "dn",
                    typing_utils.StringType,
                    description="Distinguished Name",
                ),
                typing_utils.Property(
                    "entry_type",
                    typing_utils.StringType,
                    description="Entry type classification",
                ),
                typing_utils.Property(
                    "object_classes",
                    typing_utils.ArrayType(typing_utils.StringType),
                    description="Object classes",
                ),
                typing_utils.Property(
                    "attributes",
                    typing_utils.ObjectType(),
                    description="Entry attributes",
                ),
            ).to_dict()
            super().__init__(tap, name=self.name, schema=schema)

        @property
        def logger(self) -> FlextLogger:
            """Lazy logger."""
            if self._logger_instance is None:
                self._logger_instance = FlextLogger.create_module_logger(__name__)
            return self._logger_instance

        def get_records(
            self,
            context: Mapping[str, object] | None = None,
        ) -> Iterator[dict[str, t.GeneralValueType]]:
            """Get LDIF records using flext-ldif processing."""
            _ = context
            self.logger.info("Processing LDIF files using flext-ldif library")
            # Get LDIF files from config
            raw_files = self.config.get("ldif_files", [])
            ldif_files: list[t.GeneralValueType] = (
                list(raw_files) if u.Guards.is_list(raw_files) else []
            )
            ldif_directory = self.config.get("ldif_directory")
            if ldif_files:
                for ldif_file in ldif_files:
                    yield from self._process_ldif_file(str(ldif_file))
            elif ldif_directory:
                for discovered_file in self._discover_ldif_files(str(ldif_directory)):
                    yield from self._process_ldif_file(str(discovered_file))
            else:
                yield from self._process_ldap_directory()

        def _process_ldap_directory(self) -> Iterable[dict[str, t.GeneralValueType]]:
            host_raw = self.config.get("ldap_host")
            base_dn_raw = self.config.get("ldap_base_dn")
            if not isinstance(host_raw, str) or not host_raw:
                return
            if not isinstance(base_dn_raw, str) or not base_dn_raw:
                return

            port_raw = self.config.get("ldap_port", c.TapLdap.DEFAULT_PORT)
            port = (
                int(port_raw)
                if isinstance(port_raw, int | str)
                else c.TapLdap.DEFAULT_PORT
            )
            use_ssl_raw = self.config.get("ldap_use_ssl", False)
            use_ssl = bool(use_ssl_raw)
            bind_dn_raw = self.config.get("ldap_bind_dn")
            bind_password_raw = self.config.get("ldap_bind_password")
            bind_dn = bind_dn_raw if isinstance(bind_dn_raw, str) else None
            bind_password = (
                bind_password_raw if isinstance(bind_password_raw, str) else None
            )
            search_filter_raw = self.config.get("ldap_search_filter", "(objectClass=*)")
            search_filter = (
                search_filter_raw
                if isinstance(search_filter_raw, str)
                else "(objectClass=*)"
            )
            attributes_raw = self.config.get("ldap_attributes")
            attributes = ["*"]
            if isinstance(attributes_raw, list):
                parsed_attributes = [
                    str(item) for item in attributes_raw if item is not None
                ]
                if parsed_attributes:
                    attributes = parsed_attributes
            page_size_raw = self.config.get(
                "ldap_page_size",
                c.TapLdap.DEFAULT_PAGE_SIZE,
            )
            page_size = (
                int(page_size_raw)
                if isinstance(page_size_raw, int | str)
                else c.TapLdap.DEFAULT_PAGE_SIZE
            )

            try:
                server = Server(
                    host_raw,
                    port=port,
                    use_ssl=use_ssl,
                    get_info="NO_INFO",
                )
                connection = Connection(
                    server=server,
                    user=bind_dn,
                    password=bind_password,
                    auto_bind=True,
                )
                try:
                    search_result = connection.extend.standard.paged_search(
                        search_base=base_dn_raw,
                        search_filter=search_filter,
                        search_scope=SUBTREE,
                        attributes=attributes,
                        paged_size=page_size,
                        generator=True,
                    )
                    for entry in search_result:
                        if not u.is_dict_like(entry):
                            continue
                        entry_type_raw = entry.get("type")
                        if entry_type_raw != "searchResEntry":
                            continue
                        dn_raw = entry.get("dn")
                        attrs_raw = entry.get("attributes")
                        if not isinstance(dn_raw, str) or not u.is_dict_like(attrs_raw):
                            continue
                        object_classes_raw = attrs_raw.get("objectClass")
                        object_classes = self._normalize_object_classes(
                            object_classes_raw,
                        )
                        yield {
                            "dn": dn_raw,
                            "entry_type": self._classify_entry_type(object_classes),
                            "object_classes": object_classes,
                            "attributes": dict(attrs_raw),
                        }
                finally:
                    connection.unbind()
            except (
                ValueError,
                TypeError,
                KeyError,
                AttributeError,
                OSError,
                RuntimeError,
                ImportError,
            ):
                self.logger.exception("Error traversing LDAP directory")

        def _normalize_object_classes(
            self,
            object_classes: t.GeneralValueType,
        ) -> list[str]:
            if isinstance(object_classes, str):
                return [object_classes]
            if isinstance(object_classes, list):
                return [str(value) for value in object_classes if value is not None]
            return []

        def _discover_ldif_files(self, ldif_directory: str) -> list[Path]:
            directory = Path(ldif_directory)
            if not directory.exists() or not directory.is_dir():
                self.logger.warning("LDIF directory not found: %s", ldif_directory)
                return []
            pattern_raw = self.config.get("ldif_file_pattern", "*.ldif")
            pattern = (
                str(pattern_raw) if u.Guards.is_type(pattern_raw, str) else "*.ldif"
            )
            files = [path for path in directory.rglob(pattern) if path.is_file()]
            files.sort()
            return files

        def _process_ldif_file(
            self,
            ldif_file: str,
        ) -> Iterable[dict[str, t.GeneralValueType]]:
            """Process single LDIF file using flext-ldif."""
            self.logger.info("Processing LDIF file: %s", ldif_file)
            try:
                # Read file and delegate to flext-ldif
                content = Path(ldif_file).read_text(encoding="utf-8")
                result = self._ldif_api.parse(content)
                if result.is_success and result.data:
                    for entry in result.data:
                        if x.is_base_model(entry):
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

        def _convert_entry_to_record(
            self,
            flext_entry: m.Ldif.Entry,
        ) -> dict[str, t.GeneralValueType]:
            """Convert flext-ldif entry to Singer record."""
            # Guard against None dn/attributes (RFC violation entries)
            dn_value = flext_entry.dn.value if flext_entry.dn is not None else ""
            attrs = flext_entry.attributes
            object_classes: list[str] = []
            entry_type = "other"
            if attrs is not None:
                object_classes = attrs.get_values("objectClass")
                entry_type = self._classify_entry_type(object_classes)
                entry_attrs: Mapping[str, t.GeneralValueType] = attrs.attributes
            else:
                entry_attrs: Mapping[str, t.GeneralValueType] = {}
            return {
                "dn": dn_value,
                "entry_type": entry_type,
                "object_classes": object_classes,
                "attributes": entry_attrs,
            }

        def _classify_entry_type(
            self,
            object_classes: list[str],
        ) -> str:
            """Classify entry type by simple objectClass heuristics."""
            lowered = {oc.lower() for oc in object_classes}
            if "inetorgperson" in lowered or "person" in lowered:
                return "user"
            if "groupofnames" in lowered or "group" in lowered:
                return "group"
            if "organizationalunit" in lowered or "ou" in lowered:
                return "ou"
            return "other"

    class LdifAnalysisStream(Stream):
        """LDIF analysis stream using flext-ldif for ALL analysis."""

        primary_keys: ClassVar[list[str]] = ["analysis_id"]

        @override
        def __init__(self, tap: Tap) -> None:
            """Initialize LDIF analysis stream with library delegation."""
            # Set required attributes BEFORE calling super().__init__()
            self.name = "ldif_analysis"
            self.path = "/ldif_analysis"
            # Store tap reference
            self.tap = tap
            # Initialize flext-ldif API for analysis
            self._ldif_api = FlextLdif()
            self._ldap_api = FlextLdapConnection()
            self._logger_instance: FlextLogger | None = None
            # Define schema
            schema = typing_utils.PropertiesList(
                typing_utils.Property(
                    "analysis_id",
                    typing_utils.StringType,
                    description="Analysis identifier",
                ),
                typing_utils.Property(
                    "total_entries",
                    typing_utils.IntegerType,
                    description="Total number of entries",
                ),
                typing_utils.Property(
                    "entry_types",
                    typing_utils.ObjectType(),
                    description="Count by entry type",
                ),
                typing_utils.Property(
                    "object_classes",
                    typing_utils.ObjectType(),
                    description="Count by object class",
                ),
            ).to_dict()
            super().__init__(tap, name=self.name, schema=schema)

        @property
        def logger(self) -> FlextLogger:
            """Lazy logger."""
            if self._logger_instance is None:
                self._logger_instance = FlextLogger.create_module_logger(__name__)
            return self._logger_instance

        def get_records(
            self,
            context: Mapping[str, object] | None = None,
        ) -> Iterator[dict[str, t.GeneralValueType]]:
            """Get analysis records using flext-ldif analysis capabilities."""
            _ = context
            self.logger.info("Generating LDIF analysis using flext-ldif library")
            # Get LDIF files from config
            raw_files = self.config.get("ldif_files", [])
            ldif_files: list[t.GeneralValueType] = (
                list(raw_files) if u.Guards.is_list(raw_files) else []
            )
            ldif_directory = self.config.get("ldif_directory")
            # Delegate ALL analysis to flext-ldif library
            try:
                total_entries = 0
                entry_types: dict[str, int] = {}
                object_classes: dict[str, int] = {}
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
                        # Merge counts
                        raw_entry_types = stats.get("entry_types", {})
                        if isinstance(raw_entry_types, Mapping):
                            for entry_type, count in raw_entry_types.items():
                                if isinstance(entry_type, str) and isinstance(
                                    count,
                                    int | str,
                                ):
                                    entry_types[entry_type] = entry_types.get(
                                        entry_type,
                                        0,
                                    ) + int(count)
                        raw_object_classes = stats.get("object_classes", {})
                        if isinstance(raw_object_classes, Mapping):
                            for obj_class, count in raw_object_classes.items():
                                if isinstance(obj_class, str) and isinstance(
                                    count,
                                    int | str,
                                ):
                                    object_classes[obj_class] = object_classes.get(
                                        obj_class,
                                        0,
                                    ) + int(count)
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
                        raw_entry_types = stats.get("entry_types", {})
                        if isinstance(raw_entry_types, Mapping):
                            for entry_type, count in raw_entry_types.items():
                                if isinstance(entry_type, str) and isinstance(
                                    count,
                                    int | str,
                                ):
                                    entry_types[entry_type] = entry_types.get(
                                        entry_type,
                                        0,
                                    ) + int(count)
                        raw_object_classes = stats.get("object_classes", {})
                        if isinstance(raw_object_classes, Mapping):
                            for obj_class, count in raw_object_classes.items():
                                if isinstance(obj_class, str) and isinstance(
                                    count,
                                    int | str,
                                ):
                                    object_classes[obj_class] = object_classes.get(
                                        obj_class,
                                        0,
                                    ) + int(count)
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
                # Return empty stats on error
                yield {
                    "analysis_id": "ldif_summary_error",
                    "total_entries": 0,
                    "entry_types": {},
                    "object_classes": {},
                }

        def _analyze_ldif_file(
            self,
            ldif_file: str,
        ) -> dict[str, t.GeneralValueType]:
            """Analyze single LDIF file using flext-ldif."""
            self.logger.info("Analyzing LDIF file: %s", ldif_file)
            try:
                # Read file and delegate analysis to flext-ldif
                content = Path(ldif_file).read_text(encoding="utf-8")
                result = self._ldif_api.parse(content)
                if result.is_success and result.data:
                    # Generate statistics from parsed entries
                    entry_types: dict[str, int] = {}
                    object_classes: dict[str, int] = {}
                    for entry in result.data:
                        if not x.is_base_model(entry):
                            continue
                        if entry.attributes is None:
                            continue
                        # Use library delegation for classification
                        oc_list: list[str] = entry.attributes.get_values(
                            "objectClass",
                        )
                        oc_strs = [str(x) for x in oc_list if x is not None]
                        entry_type = self._classify_entry_type(oc_strs)
                        entry_types[entry_type] = entry_types.get(entry_type, 0) + 1
                        for oc in oc_strs:
                            object_classes[oc] = object_classes.get(oc, 0) + 1
                    return {
                        "total_entries": len(result.data),
                        "entry_types": entry_types,
                        "object_classes": object_classes,
                    }
                self.logger.error(
                    f"Failed to analyze LDIF file {ldif_file}: {result.error}"
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

        def _discover_ldif_files(self, ldif_directory: str) -> list[Path]:
            directory = Path(ldif_directory)
            if not directory.exists() or not directory.is_dir():
                self.logger.warning("LDIF directory not found: %s", ldif_directory)
                return []
            pattern_raw = self.config.get("ldif_file_pattern", "*.ldif")
            pattern = (
                str(pattern_raw) if u.Guards.is_type(pattern_raw, str) else "*.ldif"
            )
            files = [path for path in directory.rglob(pattern) if path.is_file()]
            files.sort()
            return files

        def _classify_entry_type(
            self,
            object_classes: list[str],
        ) -> str:
            """Classify entry type by simple objectClass heuristics."""
            lowered = {oc.lower() for oc in object_classes}
            if "inetorgperson" in lowered or "person" in lowered:
                return "user"
            if "groupofnames" in lowered or "group" in lowered:
                return "group"
            if "organizationalunit" in lowered or "ou" in lowered:
                return "ou"
            return "other"


__all__ = [
    "FlextTapLdapLdifStreams",
]
