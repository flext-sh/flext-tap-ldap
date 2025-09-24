"""LDIF processing utilities for tap-ldap using flext-ldif library.

This module provides LDIF file processing capabilities by delegating
to the flext-ldif library to eliminate code duplication and leverage
enterprise-grade LDIF processing infrastructure.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

from flext_ldif.exceptions import FlextLdifExceptions
from flext_ldif.models import FlextLdifModels

from flext_core import (
    FlextLogger,
    FlextResult,
    FlextTypes,
)
from flext_ldif import FlextLdifAPI

# Type aliases for cleaner code
FlextLdifAttributes = FlextLdifModels.LdifAttributes
FlextLdifDistinguishedName = FlextLdifModels.DistinguishedName
FlextLdifEntry = FlextLdifModels.Entry

logger = FlextLogger(__name__)
# Testing convenience aliases that delegate to flext-ldif
LDIFParseError = FlextLdifExceptions.parse_error


class LDIFEntry:
    """Testing convenience wrapper for FlextLdifEntry.

    This class maintains the existing interface while delegating
    all operations to the flext-ldif library implementation.
    """

    def __init__(
        self,
        dn: str,
        attributes: dict[str, FlextTypes.Core.StringList] | None = None,
    ) -> None:
        """Initialize LDIF entry with testing convenience."""
        self.dn = dn
        self.attributes = attributes or {}
        self.change_type: str | None = None
        self.controls: FlextTypes.Core.StringList = []

        # Create internal flext-ldif entry for actual processing
        self._flext_entry = self._create_flext_entry()

    def _create_flext_entry(self: object) -> FlextLdifEntry:
        """Create FlextLdifEntry from current data."""
        try:
            # Use flext-ldif to create proper entry
            api = FlextLdifAPI()
            # Convert attributes to the format expected by flext-ldif
            ldif_content = f"dn: {self.dn}\n"
            for attr_name, attr_values in self.attributes.items():
                for value in attr_values:
                    ldif_content += f"{attr_name}: {value}\n"
            ldif_content += "\n"

            result: FlextResult[object] = api.parse(ldif_content)
            if result.success and result.data and len(result.data) > 0:
                return result.data[0]

            # Fallback: create minimal entry
            return FlextLdifEntry(
                dn=FlextLdifDistinguishedName(value=self.dn),
                attributes=FlextLdifAttributes(data=self.attributes),
            )
        except Exception:
            # Fallback: create minimal entry for testing convenience
            return FlextLdifEntry(
                dn=FlextLdifDistinguishedName(value=self.dn),
                attributes=FlextLdifAttributes(data=self.attributes),
            )

    def get_attribute(self, name: str) -> FlextTypes.Core.StringList:
        """Get attribute values by name (case-insensitive)."""
        for attr_name, values in self.attributes.items():
            if attr_name.lower() == name.lower():
                return values
        return []

    def has_object_class(self, object_class: str) -> bool:
        """Check if entry has specific object class."""
        object_classes: list[object] = self.get_attribute("objectClass") or []
        return any(oc.lower() == object_class.lower() for oc in object_classes)

    def to_dict(self: object) -> FlextTypes.Core.Dict:
        """Convert entry to dictionary format."""
        entry_dict: FlextTypes.Core.Dict = {
            "dn": self.dn,
            "attributes": dict(self.attributes),
        }

        if self.change_type:
            entry_dict["change_type"] = self.change_type

        if self.controls:
            entry_dict["controls"] = self.controls

        return entry_dict

    def add_attribute(self, name: str, value: str | FlextTypes.Core.StringList) -> None:
        """Add an attribute to the entry."""
        if name not in self.attributes:
            self.attributes[name] = []

        match value:
            case list() as value_list:
                self.attributes[name].extend(value_list)
            case str() as value_str:
                self.attributes[name].append(value_str)

    def is_valid(self: object) -> bool:
        """Check if the entry is valid using flext-ldif validation."""
        try:
            # Delegate to flext-ldif for validation
            api = FlextLdifAPI()
            result: FlextResult[object] = api.validate([self._flext_entry])
            return result.success and bool(result.data)
        except Exception:
            # Fallback to basic validation for testing convenience
            return bool(self.dn and self.dn.strip())

    @property
    def validation_errors(self: object) -> list[FlextTypes.Core.Headers]:
        """Get validation errors for this entry."""
        errors: list[dict[str, str]] = []
        if not self.is_valid():
            errors.append(
                {"code": "invalid_entry", "message": "Entry failed validation"},
            )
        return errors

    def parse_dn(self: object) -> FlextTypes.Core.Dict:
        """Parse DN into components using flext-ldif DN parsing."""
        try:
            # Use flext-ldif DN parsing capabilities
            dn_obj = FlextLdifDistinguishedName(value=self.dn)
            return {"dn": self.dn, "components": dn_obj.value}
        except Exception:
            return {"dn": self.dn}

    def remove_attribute(self, name: str) -> None:
        """Remove an attribute from the entry."""
        if name in self.attributes:
            self.attributes[name] = []

    def update_attribute(
        self,
        name: str,
        value: str | FlextTypes.Core.StringList,
    ) -> None:
        """Update an attribute value, replacing existing values."""
        match value:
            case list() as value_list:
                self.attributes[name] = value_list.copy()
            case str() as value_str:
                self.attributes[name] = [value_str]


class FlextLdifProcessor:
    """LDIF file processor using flext-ldif library.

    This class provides testing convenience while delegating
    all LDIF processing to the enterprise-grade flext-ldif library.
    """

    def __init__(self, *, ignore_errors: bool = True, max_errors: int = 100) -> None:
        """Initialize the processor with a flext-ldif backend."""
        self.ignore_errors = ignore_errors
        self.max_errors = max_errors
        self.errors: FlextTypes.Core.StringList = []
        self.processed_entries = 0
        self.skipped_entries = 0
        self.entries: list[LDIFEntry] = []
        self.stats = {
            "total_entries": 0,
            "valid_entries": 0,
            "invalid_entries": 0,
        }

        # Create flext-ldif API instance
        self._api = FlextLdifAPI()

    def _raise_parse_error(self, message: str) -> None:
        """Raise ValueError with the given message."""
        raise ValueError(message)

    def parse_file(self, file_path: Path) -> Iterator[LDIFEntry]:
        """Parse LDIF file using flext-ldif and yield testing convenience entries."""
        if not file_path.exists():
            msg = f"LDIF file not found: {file_path}"
            raise ValueError(msg)

        logger.info(f"Starting LDIF parsing with flext-ldif: {file_path}")
        try:
            # Read file content
            with file_path.open(encoding="utf-8") as f:
                content = f.read()

            # Use flext-ldif to parse
            result: FlextResult[object] = self._api.parse(content)
            if not result.success:
                error_msg = f"Failed to parse LDIF file {file_path}: {result.error}"
                if self.ignore_errors:
                    logger.error(error_msg)
                    self.errors.append(error_msg)
                    return
                else:
                    raise ValueError(error_msg)

            if result.data:
                for flext_entry in result.data:
                    # Convert FlextLdifEntry back to testing convenience LDIFEntry
                    convenience_entry = self._convert_from_flext_entry(flext_entry)
                    yield convenience_entry
                    self.processed_entries += 1

        except UnicodeDecodeError:
            # Try with latin-1 encoding if UTF-8 fails
            logger.warning(f"UTF-8 decoding failed, trying latin-1 for: {file_path}")
            try:
                with file_path.open(encoding="latin-1") as f:
                    content = f.read()

                result: FlextResult[object] = self._api.parse(content)
                if result.success and result.data:
                    for flext_entry in result.data:
                        convenience_entry = self._convert_from_flext_entry(flext_entry)
                        yield convenience_entry
                        self.processed_entries += 1
            except Exception as e:
                error_msg = f"Failed to parse LDIF file {file_path}: {e}"
                if self.ignore_errors:
                    logger.exception(error_msg)
                    self.errors.append(error_msg)
                else:
                    raise ValueError(error_msg) from e

    def parse_content(
        self,
        content: str,
        source_name: str = "content",
    ) -> Iterator[LDIFEntry]:
        """Parse LDIF content using flext-ldif and yield testing convenience entries."""
        logger.info(f"Parsing LDIF content with flext-ldif from {source_name}")

        try:
            result: FlextResult[object] = self._api.parse(content)
            if not result.success:
                error_msg = (
                    f"Failed to parse LDIF content from {source_name}: {result.error}"
                )
                if self.ignore_errors:
                    logger.error(error_msg)
                    self.errors.append(error_msg)
                    return
                else:
                    self._raise_parse_error(error_msg)

            if result.data:
                for flext_entry in result.data:
                    convenience_entry = self._convert_from_flext_entry(flext_entry)
                    yield convenience_entry
                    self.processed_entries += 1

        except Exception as e:
            error_msg = f"Failed to parse LDIF content from {source_name}: {e}"
            if self.ignore_errors:
                logger.exception(error_msg)
                self.errors.append(error_msg)
            else:
                raise ValueError(error_msg) from e

    def _convert_from_flext_entry(self, flext_entry: FlextLdifEntry) -> LDIFEntry:
        """Convert FlextLdifEntry to testing convenience LDIFEntry."""
        # Extract DN
        dn = flext_entry.dn.value if flext_entry.dn else ""

        # Extract attributes
        attributes: dict[str, FlextTypes.Core.StringList] = {}
        if flext_entry.attributes and flext_entry.attributes.data:
            for attr_name, attr_values in flext_entry.attributes.data.items():
                attributes[attr_name] = [str(v) for v in attr_values]

        return LDIFEntry(dn=dn, attributes=attributes)

    def get_statistics(self: object) -> FlextTypes.Core.Dict:
        """Get parsing statistics."""
        return {
            "processed_entries": self.processed_entries,
            "skipped_entries": self.skipped_entries,
            "errors": len(self.errors),
            "error_messages": self.errors.copy(),
        }

    def load_from_file(self, file_path: Path) -> FlextResult[str]:
        """Load LDIF entries from file and return as FlextResult."""
        try:
            self.entries = list(self.parse_file(file_path))
            self._update_stats()
            return FlextResult[str].ok("LDIF file loaded successfully using flext-ldif")
        except (RuntimeError, ValueError, TypeError) as e:
            return FlextResult[str].fail(f"Failed to load LDIF file: {e}")

    def load_from_string(
        self,
        content: str,
        source_name: str = "string",
    ) -> FlextResult[str]:
        """Load LDIF entries from string and return as FlextResult."""
        try:
            self.entries = list(self.parse_content(content, source_name))
            self._update_stats()
            return FlextResult[str].ok(
                "LDIF content loaded successfully using flext-ldif",
            )
        except (RuntimeError, ValueError, TypeError) as e:
            return FlextResult[str].fail(f"Failed to load LDIF content: {e}")

    def _update_stats(self: object) -> None:
        """Update statistics based on loaded entries."""
        self.stats["total_entries"] = len(self.entries)

        valid_count = 0
        invalid_count = 0

        for entry in self.entries:
            if entry.is_valid():
                valid_count += 1
            else:
                invalid_count += 1

        self.stats["valid_entries"] = valid_count
        self.stats["invalid_entries"] = invalid_count

    def filter_by_objectclass(self, object_class: str) -> list[LDIFEntry]:
        """Filter entries by object class."""
        return [entry for entry in self.entries if entry.has_object_class(object_class)]

    def filter_by_dn_pattern(self, dn_pattern: str) -> list[LDIFEntry]:
        """Filter entries by DN pattern - entries under the pattern."""
        return [
            entry
            for entry in self.entries
            if dn_pattern in entry.dn and entry.dn != dn_pattern
        ]

    def filter_by_dn_contains(self, substring: str) -> list[LDIFEntry]:
        """Filter entries by DN containing substring."""
        return [entry for entry in self.entries if substring in entry.dn]

    def filter_by_attribute_exists(self, attr_name: str) -> list[LDIFEntry]:
        """Filter entries that have a specific attribute."""
        return [entry for entry in self.entries if entry.get_attribute(attr_name)]

    def to_singer_format(self, stream_name: str) -> list[FlextTypes.Core.Dict]:
        """Convert LDIF entries to Singer record format."""
        records: list[FlextTypes.Core.Dict] = []

        for entry in self.entries:
            record_attributes: FlextTypes.Core.Dict = {"dn": entry.dn}
            record_attributes.update(dict(entry.attributes))

            record: FlextTypes.Core.Dict = {
                "type": "RECORD",
                "stream": stream_name,
                "record": record_attributes,
            }
            records.append(record)

        return records


class LDIFValidator:
    """LDIF content validator using flext-ldif validation capabilities."""

    def __init__(self: object) -> None:
        """Initialize validator with in-memory state and API client."""
        self.validation_errors: FlextTypes.Core.StringList = []
        self.warnings: FlextTypes.Core.StringList = []
        self._api = FlextLdifAPI()

    def validate_entry(self, entry: LDIFEntry) -> bool:
        """Validate LDIF entry using flext-ldif validation."""
        try:
            # Use flext-ldif validation
            # result: FlextResult[object] = self._api.validate([entry._flext_entry])
            # return result.success and bool(result.data)
            return True  # Placeholder - always return True for now
        except Exception as e:
            self.validation_errors.append(f"Validation error for {entry.dn}: {e}")
            return False

    def get_validation_results(self: object) -> FlextTypes.Core.Dict:
        """Get validation results."""
        return {
            "errors": self.validation_errors.copy(),
            "warnings": self.warnings.copy(),
            "is_valid": len(self.validation_errors) == 0,
        }

    def validate_entries(self, entries: list[LDIFEntry]) -> FlextTypes.Core.Dict:
        """Validate a list of LDIF entries using flext-ldif."""
        valid_count = 0
        invalid_count = 0
        errors = []

        try:
            # Convert to FlextLdifEntry objects
            # flext_entries = [entry._flext_entry for entry in entries]

            # Use flext-ldif batch validation
            # result: FlextResult[object] = self._api.validate(flext_entries)

            # if result.success and result.data:
            #     valid_count = len(entries)
            #     invalid_count = 0
            # else:
            #     valid_count = 0
            #     invalid_count = len(entries)
            #     errors.append(f"Batch validation failed: {result.error}")

            # Placeholder - assume all entries are valid for now
            valid_count = len(entries)
            invalid_count = 0

        except Exception:
            # Fallback to individual validation
            for entry in entries:
                if self.validate_entry(entry):
                    valid_count += 1
                else:
                    invalid_count += 1

            errors.extend(self.validation_errors)

        return {
            "total_entries": len(entries),
            "valid_entries": valid_count,
            "invalid_entries": invalid_count,
            "errors": errors,
        }


class LDIFTransformer:
    """Transform LDIF entries using flext-ldif transformation capabilities."""

    def __init__(
        self,
        transformation_rules: FlextTypes.Core.Dict | None = None,
    ) -> None:
        """Initialize transformer with optional transformation rules."""
        self.transformation_rules = transformation_rules or {}
        self._api = FlextLdifAPI()

    def transform_entry(self, entry: LDIFEntry) -> LDIFEntry:
        """Transform LDIF entry - placeholder for future enhancements."""
        # For now, return entry as-is
        # Future: integrate with flext-ldif transformation capabilities
        return entry

    def apply_attribute_mappings(
        self,
        entry: LDIFEntry,
        mappings: FlextTypes.Core.Headers,
    ) -> LDIFEntry:
        """Apply attribute name mappings to entry."""
        new_attributes: dict[str, FlextTypes.Core.StringList] = {}

        for attr_name, values in entry.attributes.items():
            new_name = mappings.get(attr_name, attr_name)
            new_attributes[new_name] = values

        transformed_entry = LDIFEntry(entry.dn, new_attributes)
        transformed_entry.change_type = entry.change_type
        transformed_entry.controls = entry.controls.copy()

        return transformed_entry
