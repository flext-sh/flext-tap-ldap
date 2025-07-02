"""LDIF stream implementation for tap-ldap.

This module implements the LDIF stream for processing LDIF files directly,
which is critical for the brutal simplification migration project.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

from singer_sdk import typing as th

from tap_ldap.ldif_processor import LDIFProcessor, LDIFTransformer, LDIFValidator
from tap_ldap.streams import LDAPStream

# Import from ldap-core-shared
try:
    from flext_ldap.utils.simple_dn_utils import simple_parse_dn

    LDAP_CORE_AVAILABLE = True
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.warning("ldap-core-shared not available: %s", e)
    LDAP_CORE_AVAILABLE = False

if TYPE_CHECKING:
    from tap_ldap.tap import TapLDAP

logger = logging.getLogger(__name__)


class LDIFStream(LDAPStream):
    """Stream for processing LDIF files directly.

    This stream is essential for the brutal simplification project as it allows
    processing of exported LDIF files without requiring live LDAP connections.
    """

    name = "ldif_entries"
    schema: ClassVar[dict[str, Any]] = th.PropertiesList(
        th.Property(
            "dn",
            th.StringType,
            required=True,
            description="Distinguished Name",
        ),
        th.Property("source_file", th.StringType, description="Source LDIF file"),
        th.Property("entry_type", th.StringType, description="Type of LDAP entry"),
        th.Property(
            "object_classes",
            th.ArrayType(th.StringType),
            description="Object Classes",
        ),
        th.Property("attributes", th.ObjectType(), description="All LDAP attributes"),
        th.Property("change_type", th.StringType, description="LDIF change type"),
        th.Property(
            "controls",
            th.ArrayType(th.StringType),
            description="LDIF controls",
        ),
        th.Property(
            "validation_status",
            th.StringType,
            description="Entry validation status",
        ),
        th.Property(
            "transformation_applied",
            th.BooleanType,
            description="Whether transformation was applied",
        ),
        th.Property(
            "processing_timestamp",
            th.DateTimeType,
            description="When entry was processed",
        ),
        th.Property(
            "migration_batch",
            th.StringType,
            description="Migration batch identifier",
        ),
        th.Property(
            "hierarchy_level",
            th.IntegerType,
            description="DN hierarchy level",
        ),
        th.Property("parent_dn", th.StringType, description="Parent DN"),
        th.Property("rdn", th.StringType, description="Relative DN"),
    ).to_dict()

    primary_keys: ClassVar[list[str]] = ["dn", "source_file"]
    replication_key = "processing_timestamp"
    is_sorted = False

    def __init__(self, tap: TapLDAP, name: str | None = None) -> None:
        """Initialize LDIF stream."""
        super().__init__(tap, name=name)

        # Initialize processors
        self.ldif_processor = LDIFProcessor(
            ignore_errors=self.config.get("ldif_ignore_errors", True),
            max_errors=self.config.get("ldif_max_errors", 100),
        )
        self.validator = LDIFValidator()
        self.transformer = LDIFTransformer(
            transformation_rules=self.config.get("ldif_transformation_rules", {}),
        )

        # Statistics
        self.stats = {
            "files_processed": 0,
            "entries_processed": 0,
            "entries_valid": 0,
            "entries_invalid": 0,
            "entries_transformed": 0,
            "errors": [],
        }

    def get_records(
        self,
        context: Mapping[str, Any] | None = None,  # noqa: ARG002
    ) -> Iterable[dict[str, Any]]:
        """Get records from LDIF files.

        Args:
        ----
            context: Stream context

        Yields:
        ------
            LDIF entry records in Singer format

        """
        ldif_files = self._get_ldif_files()
        processing_timestamp = datetime.now(timezone.utc)
        migration_batch = self.config.get(
            "migration_batch",
            f"batch_{processing_timestamp.strftime('%Y%m%d_%H%M%S')}",
        )

        logger.info("Starting LDIF processing: %d files found", len(ldif_files))

        for file_path in ldif_files:
            logger.info("Processing LDIF file: %s", file_path)

            try:
                yield from self._process_ldif_file(
                    file_path,
                    processing_timestamp,
                    migration_batch,
                )
                self.stats["files_processed"] += 1

            except Exception as e:
                error_msg = f"Failed to process LDIF file {file_path}: {e}"
                logger.exception(error_msg)
                self.stats["errors"].append(error_msg)

                if not self.config.get("ldif_ignore_file_errors", True):
                    raise

        # Log final statistics
        logger.info("LDIF processing completed: %s", self.stats)

    def _get_ldif_files(self) -> list[Path]:
        """Get list of LDIF files to process.

        Returns
        -------
            List of LDIF file paths

        """
        ldif_paths = self.config.get("ldif_files", [])
        ldif_directory = self.config.get("ldif_directory")

        files: list[Any] = []

        # Add explicit file paths
        for file_path in ldif_paths:
            path = Path(file_path)
            if path.exists():
                files.append(path)
                logger.warning("LDIF file not found: %s", file_path)

        # Scan directory for LDIF files
        if ldif_directory:
            directory = Path(ldif_directory)
            if directory.exists() and directory.is_dir():
                pattern = self.config.get("ldif_file_pattern", "*.ldif")
                found_files = list(directory.glob(pattern))
                files.extend(found_files)
                logger.info(
                    "Found %d LDIF files in directory: %s",
                    len(found_files),
                    directory,
                )
                logger.warning("LDIF directory not found: %s", ldif_directory)

        # Sort files to ensure consistent processing order
        files.sort()

        if not files:
            logger.warning("No LDIF files found to process")

        return files

    def _process_ldif_file(
        self,
        file_path: Path,
        processing_timestamp: datetime,
        migration_batch: str,
    ) -> Iterable[dict[str, Any]]:
        """Process a single LDIF file.

        Args:
        ----
            file_path: Path to LDIF file
            processing_timestamp: When processing started
            migration_batch: Migration batch identifier

        Yields:
        ------
            Processed LDIF entry records

        """
        source_file = str(file_path)

        for ldif_entry in self.ldif_processor.parse_file(file_path):
            try:
                # Validate entry
                is_valid = self.validator.validate_entry(ldif_entry)
                validation_status = "valid" if is_valid else "invalid"

                if is_valid:
                    self.stats["entries_valid"] += 1
                    self.stats["entries_invalid"] += 1

                # Transform entry if needed
                transformation_applied = False
                if self.config.get("ldif_apply_transformations", False):
                    ldif_entry = self.transformer.transform_entry(ldif_entry)
                    transformation_applied = True
                    self.stats["entries_transformed"] += 1

                # Extract entry metadata
                entry_metadata = self._extract_entry_metadata(ldif_entry)

                # Create Singer record
                record = {
                    "dn": ldif_entry.dn,
                    "source_file": source_file,
                    "entry_type": entry_metadata["entry_type"],
                    "object_classes": ldif_entry.get_attribute("objectClass") or [],
                    "attributes": ldif_entry.attributes,
                    "change_type": ldif_entry.change_type,
                    "controls": ldif_entry.controls,
                    "validation_status": validation_status,
                    "transformation_applied": transformation_applied,
                    "processing_timestamp": processing_timestamp.isoformat(),
                    "migration_batch": migration_batch,
                    "hierarchy_level": entry_metadata["hierarchy_level"],
                    "parent_dn": entry_metadata["parent_dn"],
                    "rdn": entry_metadata["rdn"],
                }

                yield record
                self.stats["entries_processed"] += 1

            except Exception as e:
                error_msg = f"Error processing entry {ldif_entry.dn}: {e}"
                logger.exception(error_msg)
                self.stats["errors"].append(error_msg)

                if not self.config.get("ldif_ignore_entry_errors", True):
                    raise

    def _extract_entry_metadata(self, ldif_entry: Any) -> dict[str, Any]:
        """Extract metadata from LDIF entry.

        Args:
        ----
            ldif_entry: LDIFEntry to analyze

        Returns:
        -------
            Dictionary with entry metadata

        """
        # Determine entry type based on object classes
        object_classes = ldif_entry.get_attribute("objectClass") or []
        entry_type = self._classify_entry_type(object_classes)

        # Extract DN components if ldap-core-shared is available
        hierarchy_level = 0
        parent_dn = None
        rdn = ldif_entry.dn

        if LDAP_CORE_AVAILABLE:
            try:
                dn_components = simple_parse_dn(ldif_entry.dn)
                hierarchy_level = len(dn_components)

                if len(dn_components) > 1:
                    parent_components = dn_components[1:]
                    parent_dn = ",".join(
                        f"{attr}={value}" for attr, value in parent_components
                    )

                if dn_components:
                    rdn = f"{dn_components[0][0]}={dn_components[0][1]}"

            except Exception as e:
                logger.debug("Failed to parse DN %s: %s", ldif_entry.dn, e)

        return {
            "entry_type": entry_type,
            "hierarchy_level": hierarchy_level,
            "parent_dn": parent_dn,
            "rdn": rdn,
        }

    def _classify_entry_type(self, object_classes: list[str]) -> str:
        """Classify entry type based on object classes.

        Args:
        ----
            object_classes: List of object class names

        Returns:
        -------
            Entry type classification

        """
        oc_lower = [oc.lower() for oc in object_classes]

        # Check for common entry types
        if "inetorgperson" in oc_lower or "person" in oc_lower:
            return "user"
        if "groupofnames" in oc_lower or "groupofuniquenames" in oc_lower:
            return "group"
        if "organizationalunit" in oc_lower:
            return "organizational_unit"
        if "organization" in oc_lower:
            return "organization"
        if "domain" in oc_lower:
            return "domain"
        if "orcluser" in oc_lower:
            return "oracle_user"
        if "orclgroup" in oc_lower:
            return "oracle_group"
        if "orclcontext" in oc_lower:
            return "oracle_context"
        if "orclcontainer" in oc_lower:
            return "oracle_container"
        return "other"

    def get_search_filter(self) -> str:
        """Get search filter (not used for LDIF stream)."""
        return "(objectClass=*)"

    def get_attributes(self) -> list[str] | None:
        """Get attributes (not used for LDIF stream)."""
        return None


class LDIFAnalysisStream(LDAPStream):
    """Stream for analyzing LDIF file structure and content.

    Provides high-level analysis of LDIF files for migration planning.
    """

    name = "ldif_analysis"
    schema: ClassVar[dict[str, Any]] = th.PropertiesList(
        th.Property(
            "source_file",
            th.StringType,
            required=True,
            description="Source LDIF file",
        ),
        th.Property(
            "file_size_bytes",
            th.IntegerType,
            description="File size in bytes",
        ),
        th.Property(
            "total_entries",
            th.IntegerType,
            description="Total number of entries",
        ),
        th.Property("entry_types", th.ObjectType(), description="Count by entry type"),
        th.Property(
            "object_classes",
            th.ObjectType(),
            description="Count by object class",
        ),
        th.Property(
            "hierarchy_levels",
            th.ObjectType(),
            description="Count by hierarchy level",
        ),
        th.Property(
            "validation_summary",
            th.ObjectType(),
            description="Validation results summary",
        ),
        th.Property(
            "attributes_summary",
            th.ObjectType(),
            description="Attribute usage summary",
        ),
        th.Property(
            "analysis_timestamp",
            th.DateTimeType,
            description="When analysis was performed",
        ),
        th.Property(
            "processing_errors",
            th.IntegerType,
            description="Number of processing errors",
        ),
        th.Property(
            "recommendations",
            th.ArrayType(th.StringType),
            description="Migration recommendations",
        ),
    ).to_dict()

    primary_keys: ClassVar[list[str]] = ["source_file"]

    def get_records(
        self,
        context: Mapping[str, Any] | None = None,  # noqa: ARG002
    ) -> Iterable[dict[str, Any]]:
        """Get LDIF analysis records.

        Args:
        ----
            context: Stream context

        Yields:
        ------
            LDIF analysis records

        """
        ldif_files = self._get_ldif_files()
        analysis_timestamp = datetime.now(timezone.utc)

        for file_path in ldif_files:
            try:
                analysis = self._analyze_ldif_file(file_path, analysis_timestamp)
                yield analysis
            except Exception as e:
                logger.exception("Failed to analyze LDIF file %s: %s", file_path, e)

    def _get_ldif_files(self) -> list[Path]:
        """Get list of LDIF files to analyze."""
        # Reuse the same logic as LDIFStream
        ldif_stream = LDIFStream(self.tap)
        return ldif_stream._get_ldif_files()

    def _analyze_ldif_file(
        self,
        file_path: Path,
        analysis_timestamp: datetime,
    ) -> dict[str, Any]:
        """Analyze a single LDIF file.

        Args:
        ----
            file_path: Path to LDIF file
            analysis_timestamp: When analysis was performed

        Returns:
        -------
            Analysis results

        """
        logger.info("Analyzing LDIF file: %s", file_path)

        # Initialize counters
        entry_types: dict[str, Any] = {}
        object_classes: dict[str, Any] = {}
        hierarchy_levels: dict[str, Any] = {}
        attributes_used: dict[str, Any] = {}
        total_entries = 0
        validation_errors = 0
        validation_warnings = 0

        processor = LDIFProcessor(ignore_errors=True, max_errors=1000)
        validator = LDIFValidator()

        # Process file
        for ldif_entry in processor.parse_file(file_path):
            total_entries += 1

            # Analyze entry type
            ocs = ldif_entry.get_attribute("objectClass") or []
            entry_type = self._classify_entry_type(ocs)
            entry_types[entry_type] = entry_types.get(entry_type, 0) + 1

            # Count object classes
            for oc in ocs:
                object_classes[oc] = object_classes.get(oc, 0) + 1

            # Analyze hierarchy level
            if LDAP_CORE_AVAILABLE:
                try:
                    dn_components = simple_parse_dn(ldif_entry.dn)
                    level = len(dn_components)
                    hierarchy_levels[str(level)] = (
                        hierarchy_levels.get(str(level), 0) + 1
                    )
                except Exception:
                    # Skip entries with invalid DN hierarchy
                    continue

            # Count attribute usage
            for attr_name in ldif_entry.attributes:
                attributes_used[attr_name] = attributes_used.get(attr_name, 0) + 1

            # Validate entry
            if not validator.validate_entry(ldif_entry):
                validation_errors += 1

        # Get validation results
        validation_results = validator.get_validation_results()
        validation_warnings = len(validation_results.get("warnings", []))

        # Generate recommendations
        recommendations = self._generate_recommendations(
            entry_types,
            object_classes,
            total_entries,
            validation_errors,
        )

        return {
            "source_file": str(file_path),
            "file_size_bytes": file_path.stat().st_size,
            "total_entries": total_entries,
            "entry_types": entry_types,
            "object_classes": object_classes,
            "hierarchy_levels": hierarchy_levels,
            "validation_summary": {
                "errors": validation_errors,
                "warnings": validation_warnings,
                "valid_entries": total_entries - validation_errors,
            },
            "attributes_summary": {
                "total_attributes": len(attributes_used),
                "most_common": dict(
                    sorted(attributes_used.items(), key=lambda x: x[1], reverse=True)[
                        :10
                    ],
                ),
            },
            "analysis_timestamp": analysis_timestamp.isoformat(),
            "processing_errors": len(processor.errors),
            "recommendations": recommendations,
        }

    def _classify_entry_type(self, object_classes: list[str]) -> str:
        """Classify entry type (reuse from LDIFStream)."""
        ldif_stream = LDIFStream(self.tap)
        return ldif_stream._classify_entry_type(object_classes)

    def _generate_recommendations(
        self,
        entry_types: dict[str, int],
        object_classes: dict[str, int],
        total_entries: int,
        validation_errors: int,
    ) -> list[str]:
        """Generate migration recommendations based on analysis.

        Args:
        ----
            entry_types: Entry type counts
            object_classes: Object class counts
            total_entries: Total number of entries
            validation_errors: Number of validation errors

        Returns:
        -------
            List of recommendations

        """
        recommendations: list[Any] = []

        # Check for Oracle-specific objects
        oracle_objects = sum(
            count
            for oc, count in object_classes.items()
            if oc.lower().startswith("orcl")
        )
        if oracle_objects > 0:
            recommendations.append(
                f"Found {oracle_objects} Oracle-specific objects that may need transformation",
            )

        # Check validation error rate
        if validation_errors > 0:
            error_rate = (validation_errors / total_entries) * 100
            if error_rate > 10:
                recommendations.append(
                    f"High validation error rate ({error_rate:.1f}%) - review data quality",
                )
                recommendations.append(
                    f"Some validation errors ({error_rate:.1f}%) - minor cleanup needed",
                )

        # Check for complex hierarchy
        max_users = entry_types.get("user", 0)
        if max_users > 10000:
            recommendations.append(
                "Large number of users - consider batch processing strategy",
            )

        # Check for groups
        groups = entry_types.get("group", 0)
        if groups > 0:
            recommendations.append(
                f"Found {groups} groups - verify membership migration strategy",
            )

        return recommendations
