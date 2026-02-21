"""FLEXT Tap LDAP - LDIF stream processing."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import override

from flext_core import FlextLogger
from flext_ldap import FlextLdapConnection
from flext_ldif import FlextLdif
from flext_ldif.models import m
from flext_meltano import FlextMeltanoStream as Stream
from flext_meltano.typings import t as t_meltano

from flext_tap_ldap.protocols import TapProtocol
from flext_tap_ldap.typings import t

logger = FlextLogger(__name__)

# Access Singer SDK typing through FLEXT domain namespace
typing_utils = t_meltano.Singer.Typing


class FlextTapLdapLdifStreams:
    """LDIF stream processing container with nested stream classes.

    Consolidates all LDIF stream functionality following FlextTapLdap[Module] pattern.
    """

    class LdifStream(Stream):
        """LDIF stream using flext-ldif for ALL processing."""

        @override
        def __init__(self, tap: TapProtocol) -> None:
            """Initialize LDIF stream with library delegation."""
            # Set required attributes BEFORE calling super().__init__()
            self.name = "ldif_entries"
            self.path = "/ldif_entries"
            self.primary_keys = ["dn"]
            # Store tap reference
            self.tap = tap
            # Initialize flext-ldif API for processing
            self._ldif_api = FlextLdif()
            self._ldap_api = FlextLdapConnection()
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
            super().__init__(tap, name=self.name, schema=schema)  # type: ignore[arg-type]

        def get_records(
            self,
            context: Mapping[str, object] | None = None,  # noqa: ARG002
        ) -> Iterable[dict[str, t.GeneralValueType]]:
            """Get LDIF records using flext-ldif processing."""
            logger.info("Processing LDIF files using flext-ldif library")
            # Get LDIF files from config
            raw_files = self.tap.config.get_config("ldif_files", [])
            ldif_files: list[t.GeneralValueType] = (
                list(raw_files) if isinstance(raw_files, list) else []
            )
            ldif_directory = self.tap.config.get_config("ldif_directory")
            if ldif_files:
                for ldif_file in ldif_files:
                    yield from self._process_ldif_file(str(ldif_file))
            elif ldif_directory:
                # Directory processing should be implemented in flext-ldif library
                logger.warning(
                    "Directory processing not yet implemented in flext-ldif library",
                )

        def _process_ldif_file(
            self,
            ldif_file: str,
        ) -> Iterable[dict[str, t.GeneralValueType]]:
            """Process single LDIF file using flext-ldif."""
            logger.info("Processing LDIF file: %s", ldif_file)
            try:
                # Read file and delegate to flext-ldif
                content = Path(ldif_file).read_text(encoding="utf-8")
                result = self._ldif_api.parse(content)
                if result.is_success and result.data:
                    for entry in result.data:
                        if isinstance(entry, m.Ldif.Entry):
                            yield self._convert_entry_to_record(entry)
                else:
                    logger.error(
                        f"Failed to parse LDIF file {ldif_file}: {result.error}",
                    )
            except Exception:
                logger.exception("Error processing LDIF file %s", ldif_file)

        def _convert_entry_to_record(
            self,
            flext_entry: m.Ldif.Entry,
        ) -> dict[str, t.GeneralValueType]:
            """Convert flext-ldif entry to Singer record."""
            # Guard against None dn/attributes (RFC violation entries)
            dn_value = flext_entry.dn.value if flext_entry.dn is not None else ""
            attrs = flext_entry.attributes
            if attrs is not None:
                object_classes = attrs.get_values("objectClass")
                self._classify_entry_type(object_classes)
                entry_attrs = attrs.attributes
            else:
                entry_attrs = {}
            return {
                "dn": dn_value,
                "entry_type": "entry_type",
                "object_classes": "object_classes",
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

        @override
        def __init__(self, tap: TapProtocol) -> None:
            """Initialize LDIF analysis stream with library delegation."""
            # Set required attributes BEFORE calling super().__init__()
            self.name = "ldif_analysis"
            self.path = "/ldif_analysis"
            self.primary_keys = ["analysis_id"]
            # Store tap reference
            self.tap = tap
            # Initialize flext-ldif API for analysis
            self._ldif_api = FlextLdif()
            self._ldap_api = FlextLdapConnection()
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
            super().__init__(tap, name=self.name, schema=schema)  # type: ignore[arg-type]

        def get_records(
            self,
            context: Mapping[str, object] | None = None,  # noqa: ARG002
        ) -> Iterable[dict[str, t.GeneralValueType]]:
            """Get analysis records using flext-ldif analysis capabilities."""
            logger.info("Generating LDIF analysis using flext-ldif library")
            # Get LDIF files from config
            raw_files = self.tap.config.get_config("ldif_files", [])
            ldif_files: list[t.GeneralValueType] = (
                list(raw_files) if isinstance(raw_files, list) else []
            )
            ldif_directory = self.tap.config.get_config("ldif_directory")
            # Delegate ALL analysis to flext-ldif library
            try:
                total_entries = 0
                entry_types: dict[str, int] = {}
                object_classes: dict[str, int] = {}
                if ldif_files:
                    for ldif_file in ldif_files:
                        if not isinstance(ldif_file, str):
                            continue
                        stats = self._analyze_ldif_file(ldif_file)
                        total_count = stats.get("total_entries", 0)
                        if isinstance(total_count, int):
                            total_entries += total_count
                        # Merge counts
                        raw_entry_types = stats.get("entry_types", {})
                        if isinstance(raw_entry_types, dict):
                            for entry_type, count in raw_entry_types.items():
                                if isinstance(count, (int, str)):
                                    entry_types[entry_type] = entry_types.get(
                                        entry_type,
                                        0,
                                    ) + int(count)
                        raw_object_classes = stats.get("object_classes", {})
                        if isinstance(raw_object_classes, dict):
                            for obj_class, count in raw_object_classes.items():
                                if isinstance(count, (int, str)):
                                    object_classes[obj_class] = object_classes.get(
                                        obj_class,
                                        0,
                                    ) + int(count)
                elif ldif_directory:
                    # This should be implemented in flext-ldif library
                    logger.warning(
                        "Directory analysis should be implemented in flext-ldif library",
                    )
                yield {
                    "analysis_id": "ldif_summary",
                    "total_entries": "total_entries",
                    "entry_types": "entry_types",
                    "object_classes": "object_classes",
                }
            except Exception:
                logger.exception("LDIF analysis error")
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
            logger.info("Analyzing LDIF file: %s", ldif_file)
            try:
                # Read file and delegate analysis to flext-ldif
                content = Path(ldif_file).read_text(encoding="utf-8")
                result = self._ldif_api.parse(content)
                if result.is_success and result.data:
                    # Generate statistics from parsed entries
                    entry_types: dict[str, int] = {}
                    object_classes: dict[str, int] = {}
                    for entry in result.data:
                        if not isinstance(entry, m.Ldif.Entry):
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
                        "total_entries": "total_entries",
                        "entry_types": "entry_types",
                        "object_classes": "object_classes",
                    }
                logger.error(f"Failed to analyze LDIF file {ldif_file}: {result.error}")
                return {"total_entries": 0, "entry_types": {}, "object_classes": {}}
            except Exception:
                logger.exception("Error analyzing LDIF file %s", ldif_file)
                return {"total_entries": 0, "entry_types": {}, "object_classes": {}}

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
