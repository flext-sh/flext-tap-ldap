"""LDIF stream implementation for tap-ldap using flext-ldif and flext-ldap.

This module provides LDIF streams that delegate ALL processing to the
flext-ldif and flext-ldap libraries, eliminating code duplication.

REFACTORED: Uses flext-ldif for LDIF parsing and flext-ldap for entry classification.
NO local LDIF or LDAP logic - everything delegated to libraries.


Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextTypes

"""
Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""


from collections.abc import Iterable, Mapping
from pathlib import Path

from flext_core import FlextLogger
from flext_core.typings import FlextTypes
from flext_ldap import FlextLDAPApi
from flext_ldif import FlextLDIFAPI, FlextLDIFEntry
from flext_meltano import Stream, singer_typing as th

from flext_tap_ldap.tap import FlextTapLDAP

logger = FlextLogger(__name__)


class LDIFStream(Stream):
    """LDIF stream using flext-ldif for ALL processing."""

    def __init__(self, tap: FlextTapLDAP) -> None:
        """Initialize LDIF stream with library delegation."""
        # Set required attributes BEFORE calling super().__init__()
        self.name = "ldif_entries"
        self.path = "/ldif_entries"
        self.primary_keys = ["dn"]
        # Store tap reference
        self.tap = tap
        # Initialize flext-ldif API for processing
        self._ldif_api = FlextLDIFAPI()
        self._ldap_api = FlextLDAPApi()
        # Define schema
        schema = th.PropertiesList(
            th.Property("dn", th.StringType, description="Distinguished Name"),
            th.Property(
                "entry_type",
                th.StringType,
                description="Entry type classification",
            ),
            th.Property(
                "object_classes",
                th.ArrayType(th.StringType),
                description="Object classes",
            ),
            th.Property(
                "attributes",
                th.ObjectType(),
                description="Entry attributes",
            ),
        ).to_dict()
        super().__init__(tap, name=self.name, schema=schema)

    def get_records(
        self,
        _context: Mapping[str, object] | None = None,
    ) -> Iterable[FlextTypes.Core.Dict]:
        """Get LDIF records using flext-ldif processing."""
        logger.info("Processing LDIF files using flext-ldif library")
        # Get LDIF files from config
        ldif_files = self.tap.config.get("ldif_files", [])
        ldif_directory = self.tap.config.get("ldif_directory")
        if ldif_files:
            for ldif_file in ldif_files:
                yield from self._process_ldif_file(ldif_file)
        elif ldif_directory:
            # Directory processing should be implemented in flext-ldif library
            logger.warning(
                "Directory processing not yet implemented in flext-ldif library",
            )

    def _process_ldif_file(self, ldif_file: str) -> Iterable[FlextTypes.Core.Dict]:
        """Process single LDIF file using flext-ldif."""
        logger.info(f"Processing LDIF file: {ldif_file}")
        try:
            # Read file and delegate to flext-ldif
            with Path(ldif_file).open(encoding="utf-8") as f:
                content = f.read()
            result = self._ldif_api.parse(content)
            if result.success and result.data:
                for entry in result.data:
                    yield self._convert_entry_to_record(entry)
            else:
                logger.error(f"Failed to parse LDIF file {ldif_file}: {result.error}")
        except Exception:
            logger.exception(f"Error processing LDIF file {ldif_file}")

    def _convert_entry_to_record(
        self,
        flext_entry: FlextLDIFEntry,
    ) -> FlextTypes.Core.Dict:
        """Convert flext-ldif entry to Singer record."""
        # Delegate entry type classification to flext-ldap
        object_classes = flext_entry.attributes.get_values("objectClass")
        entry_type = self._classify_entry_type(object_classes)
        return {
            "dn": flext_entry.dn.value,
            "entry_type": entry_type,
            "object_classes": object_classes,
            "attributes": flext_entry.attributes.attributes,
        }

    def _classify_entry_type(self, object_classes: FlextTypes.Core.StringList) -> str:
        """Classify entry type by simple objectClass heuristics."""
        lowered = {oc.lower() for oc in object_classes}
        if "inetorgperson" in lowered or "person" in lowered:
            return "user"
        if "groupofnames" in lowered or "group" in lowered:
            return "group"
        if "organizationalunit" in lowered or "ou" in lowered:
            return "ou"
        return "other"


class LDIFAnalysisStream(Stream):
    """LDIF analysis stream using flext-ldif for ALL analysis."""

    def __init__(self, tap: FlextTapLDAP) -> None:
        """Initialize LDIF analysis stream with library delegation."""
        # Set required attributes BEFORE calling super().__init__()
        self.name = "ldif_analysis"
        self.path = "/ldif_analysis"
        self.primary_keys = ["analysis_id"]
        # Store tap reference
        self.tap = tap
        # Initialize flext-ldif API for analysis
        self._ldif_api = FlextLDIFAPI()
        self._ldap_api = FlextLDAPApi()
        # Define schema
        schema = th.PropertiesList(
            th.Property(
                "analysis_id",
                th.StringType,
                description="Analysis identifier",
            ),
            th.Property(
                "total_entries",
                th.IntegerType,
                description="Total number of entries",
            ),
            th.Property(
                "entry_types",
                th.ObjectType(),
                description="Count by entry type",
            ),
            th.Property(
                "object_classes",
                th.ObjectType(),
                description="Count by object class",
            ),
        ).to_dict()
        super().__init__(tap, name=self.name, schema=schema)

    def get_records(
        self,
        _context: Mapping[str, object] | None = None,
    ) -> Iterable[FlextTypes.Core.Dict]:
        """Get analysis records using flext-ldif analysis capabilities."""
        logger.info("Generating LDIF analysis using flext-ldif library")
        # Get LDIF files from config
        ldif_files = self.tap.config.get("ldif_files", [])
        ldif_directory = self.tap.config.get("ldif_directory")
        # Delegate ALL analysis to flext-ldif library
        try:
            total_entries = 0
            entry_types: dict[str, int] = {}
            object_classes: dict[str, int] = {}
            if ldif_files:
                for ldif_file in ldif_files:
                    stats = self._analyze_ldif_file(ldif_file)
                    total_count = stats.get("total_entries", 0)
                    if isinstance(total_count, int):
                        total_entries += total_count
                    # Merge counts
                    stats_entry_types = stats.get("entry_types", {})
                    if isinstance(stats_entry_types, dict):
                        for entry_type, count in stats_entry_types.items():
                            entry_types[entry_type] = entry_types.get(
                                entry_type,
                                0,
                            ) + int(count)
                    stats_object_classes = stats.get("object_classes", {})
                    if isinstance(stats_object_classes, dict):
                        for obj_class, count in stats_object_classes.items():
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
                "total_entries": total_entries,
                "entry_types": entry_types,
                "object_classes": object_classes,
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

    def _analyze_ldif_file(self, ldif_file: str) -> FlextTypes.Core.Dict:
        """Analyze single LDIF file using flext-ldif."""
        logger.info(f"Analyzing LDIF file: {ldif_file}")
        try:
            # Read file and delegate analysis to flext-ldif
            with Path(ldif_file).open(encoding="utf-8") as f:
                content = f.read()
            result = self._ldif_api.parse(content)
            if result.success and result.data:
                # Generate statistics from parsed entries
                total_entries = len(result.data)
                entry_types: dict[str, int] = {}
                object_classes: dict[str, int] = {}
                for entry in result.data:
                    # Use library delegation for classification
                    oc_list = entry.attributes.get_values("objectClass")
                    entry_type = self._classify_entry_type(oc_list)
                    entry_types[entry_type] = entry_types.get(entry_type, 0) + 1
                    # Count object classes
                    for oc in oc_list:
                        object_classes[oc] = object_classes.get(oc, 0) + 1
                return {
                    "total_entries": total_entries,
                    "entry_types": entry_types,
                    "object_classes": object_classes,
                }
            logger.error(f"Failed to analyze LDIF file {ldif_file}: {result.error}")
            return {"total_entries": 0, "entry_types": {}, "object_classes": {}}
        except Exception:
            logger.exception(f"Error analyzing LDIF file {ldif_file}")
            return {"total_entries": 0, "entry_types": {}, "object_classes": {}}

    def _classify_entry_type(self, object_classes: FlextTypes.Core.StringList) -> str:
        """Classify entry type by simple objectClass heuristics."""
        lowered = {oc.lower() for oc in object_classes}
        if "inetorgperson" in lowered or "person" in lowered:
            return "user"
        if "groupofnames" in lowered or "group" in lowered:
            return "group"
        if "organizationalunit" in lowered or "ou" in lowered:
            return "ou"
        return "other"


# Export what we can
__all__: FlextTypes.Core.StringList = ["LDIFAnalysisStream", "LDIFStream"]
