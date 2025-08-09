"""LDIF processing utilities for tap-ldap using flext-ldif library.

This module provides LDIF file processing capabilities by delegating
to the flext-ldif library to eliminate code duplication and leverage
enterprise-grade LDIF processing infrastructure.

Refactored to use flext-ldif exclusively, removing duplicated code
while maintaining backward compatibility for existing Singer streams.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path
else:
    from pathlib import Path

from flext_core import (
    FlextResult,
    get_logger,
)
from flext_ldif import (
    FlextLdifAPI,
    FlextLdifAttributes,
    FlextLdifDistinguishedName,
    FlextLdifEntry,
    FlextLdifParseError,
)

logger = get_logger(__name__)

# Backward compatibility aliases that delegate to flext-ldif
LDIFParseError = FlextLdifParseError


class LDIFEntry:
    """Backward compatibility wrapper for FlextLdifEntry.

    This class maintains the existing interface while delegating
    all operations to the flext-ldif library implementation.
    """

    def __init__(self, dn: str, attributes: dict[str, list[str]] | None = None) -> None:
        """Initialize LDIF entry with backward compatibility."""
        self.dn = dn
        self.attributes = attributes or {}
        self.change_type: str | None = None
        self.controls: list[str] = []

        # Create internal flext-ldif entry for actual processing
        self._flext_entry = self._create_flext_entry()

    def _create_flext_entry(self) -> FlextLdifEntry:
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

            result = api.parse(ldif_content)
            if result.success and result.data and len(result.data) > 0:
                return result.data[0]

            # Fallback: create minimal entry
            return FlextLdifEntry(
                id=str(uuid.uuid4()),
                dn=FlextLdifDistinguishedName(value=self.dn),
                attributes=FlextLdifAttributes(attributes=self.attributes),
            )
        except Exception:
            # Fallback: create minimal entry for backward compatibility
            return FlextLdifEntry(
                id=str(uuid.uuid4()),
                dn=FlextLdifDistinguishedName(value=self.dn),
                attributes=FlextLdifAttributes(attributes=self.attributes),
            )

    def get_attribute(self, name: str) -> list[str]:
        """Get attribute values by name (case-insensitive)."""
        for attr_name, values in self.attributes.items():
            if attr_name.lower() == name.lower():
                return values
        return []

    def has_object_class(self, object_class: str) -> bool:
        """Check if entry has specific object class."""
        object_classes = self.get_attribute("objectClass") or []
        return any(oc.lower() == object_class.lower() for oc in object_classes)

    def to_dict(self) -> dict[str, object]:
        """Convert entry to dictionary format."""
        entry_dict: dict[str, object] = {
            "dn": self.dn,
            "attributes": dict(self.attributes),
        }

        if self.change_type:
            entry_dict["change_type"] = self.change_type

        if self.controls:
            entry_dict["controls"] = self.controls

        return entry_dict

    def add_attribute(self, name: str, value: str | list[str]) -> None:
        """Add an attribute to the entry."""
        if name not in self.attributes:
            self.attributes[name] = []

        if isinstance(value, list):
            self.attributes[name].extend(value)
        else:
            self.attributes[name].append(value)

    def is_valid(self) -> bool:
        """Check if the entry is valid using flext-ldif validation."""
        try:
            # Delegate to flext-ldif for validation
            api = FlextLdifAPI()
            result = api.validate([self._flext_entry])
            return result.success and bool(result.data)
        except Exception:
            # Fallback to basic validation for backward compatibility
            return bool(self.dn and self.dn.strip())

    @property
    def validation_errors(self) -> list[dict[str, str]]:
        """Get validation errors for this entry."""
        errors = []
        if not self.is_valid():
            errors.append(
                {"code": "invalid_entry", "message": "Entry failed validation"}
            )
        return errors

    def parse_dn(self) -> dict[str, object]:
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

    def update_attribute(self, name: str, value: str | list[str]) -> None:
        """Update an attribute value, replacing existing values."""
        if isinstance(value, list):
            self.attributes[name] = value.copy()
        else:
            self.attributes[name] = [value]


class FlextLDIFProcessor:
    """LDIF file processor using flext-ldif library.

    This class provides backward compatibility while delegating
    all LDIF processing to the enterprise-grade flext-ldif library.
    """

    def __init__(self, *, ignore_errors: bool = True, max_errors: int = 100) -> None:
        """Initialize processor with flext-ldif backend."""
        self.ignore_errors = ignore_errors
        self.max_errors = max_errors
        self.errors: list[str] = []
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
        """Parse LDIF file using flext-ldif and yield backward-compatible entries."""
        if not file_path.exists():
            msg = f"LDIF file not found: {file_path}"
            raise ValueError(msg)

        logger.info(f"Starting LDIF parsing with flext-ldif: {file_path}")
        try:
            # Read file content
            with file_path.open(encoding="utf-8") as f:
                content = f.read()

            # Use flext-ldif to parse
            result = self._api.parse(content)
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
                    # Convert FlextLdifEntry back to backward-compatible LDIFEntry
                    compat_entry = self._convert_from_flext_entry(flext_entry)
                    yield compat_entry
                    self.processed_entries += 1

        except UnicodeDecodeError:
            # Try with latin-1 encoding if UTF-8 fails
            logger.warning(f"UTF-8 decoding failed, trying latin-1 for: {file_path}")
            try:
                with file_path.open(encoding="latin-1") as f:
                    content = f.read()

                result = self._api.parse(content)
                if result.success and result.data:
                    for flext_entry in result.data:
                        compat_entry = self._convert_from_flext_entry(flext_entry)
                        yield compat_entry
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
        """Parse LDIF content using flext-ldif and yield backward-compatible entries."""
        logger.info(f"Parsing LDIF content with flext-ldif from {source_name}")

        try:
            result = self._api.parse(content)
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
                    compat_entry = self._convert_from_flext_entry(flext_entry)
                    yield compat_entry
                    self.processed_entries += 1

        except Exception as e:
            error_msg = f"Failed to parse LDIF content from {source_name}: {e}"
            if self.ignore_errors:
                logger.exception(error_msg)
                self.errors.append(error_msg)
            else:
                raise ValueError(error_msg) from e

    def _convert_from_flext_entry(self, flext_entry: FlextLdifEntry) -> LDIFEntry:
        """Convert FlextLdifEntry to backward-compatible LDIFEntry."""
        # Extract DN
        dn = flext_entry.dn.value if flext_entry.dn else ""

        # Extract attributes
        attributes: dict[str, list[str]] = {}
        if flext_entry.attributes and flext_entry.attributes.attributes:
            for attr_name, attr_values in flext_entry.attributes.attributes.items():
                # attr_values is always list[str] from FlextLdifAttributes definition
                attributes[attr_name] = [str(v) for v in attr_values]

        return LDIFEntry(dn=dn, attributes=attributes)

    def get_statistics(self) -> dict[str, object]:
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
            return FlextResult.ok("LDIF file loaded successfully using flext-ldif")
        except (RuntimeError, ValueError, TypeError) as e:
            return FlextResult.fail(f"Failed to load LDIF file: {e}")

    def load_from_string(
        self,
        content: str,
        source_name: str = "string",
    ) -> FlextResult[str]:
        """Load LDIF entries from string and return as FlextResult."""
        try:
            self.entries = list(self.parse_content(content, source_name))
            self._update_stats()
            return FlextResult.ok("LDIF content loaded successfully using flext-ldif")
        except (RuntimeError, ValueError, TypeError) as e:
            return FlextResult.fail(f"Failed to load LDIF content: {e}")

    def _update_stats(self) -> None:
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

    def to_singer_format(self, stream_name: str) -> list[dict[str, object]]:
        """Convert LDIF entries to Singer record format."""
        records: list[dict[str, object]] = []

        for entry in self.entries:
            record_attributes: dict[str, object] = {"dn": entry.dn}
            for attr_name, attr_values in entry.attributes.items():
                record_attributes[attr_name] = (
                    attr_values
                    if isinstance(attr_values, (list, str))
                    else list(attr_values)
                )

            record: dict[str, object] = {
                "type": "RECORD",
                "stream": stream_name,
                "record": record_attributes,
            }
            records.append(record)

        return records


class LDIFValidator:
    """LDIF content validator using flext-ldif validation capabilities."""

    def __init__(self) -> None:
        self.validation_errors: list[str] = []
        self.warnings: list[str] = []
        self._api = FlextLdifAPI()

    def validate_entry(self, entry: LDIFEntry) -> bool:
        """Validate LDIF entry using flext-ldif validation."""
        try:
            # Use flext-ldif validation
            result = self._api.validate([entry._flext_entry])
            return result.success and bool(result.data)
        except Exception as e:
            self.validation_errors.append(f"Validation error for {entry.dn}: {e}")
            return False

    def get_validation_results(self) -> dict[str, object]:
        """Get validation results."""
        return {
            "errors": self.validation_errors.copy(),
            "warnings": self.warnings.copy(),
            "is_valid": len(self.validation_errors) == 0,
        }

    def validate_entries(self, entries: list[LDIFEntry]) -> dict[str, object]:
        """Validate a list of LDIF entries using flext-ldif."""
        valid_count = 0
        invalid_count = 0
        errors = []

        try:
            # Convert to FlextLdifEntry objects
            flext_entries = [entry._flext_entry for entry in entries]

            # Use flext-ldif batch validation
            result = self._api.validate(flext_entries)

            if result.success and result.data:
                valid_count = len(entries)
                invalid_count = 0
            else:
                valid_count = 0
                invalid_count = len(entries)
                errors.append(f"Batch validation failed: {result.error}")

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

    def __init__(self, transformation_rules: dict[str, object] | None = None) -> None:
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
        mappings: dict[str, str],
    ) -> LDIFEntry:
        """Apply attribute name mappings to entry."""
        new_attributes: dict[str, list[str]] = {}

        for attr_name, values in entry.attributes.items():
            new_name = mappings.get(attr_name, attr_name)
            new_attributes[new_name] = values

        transformed_entry = LDIFEntry(entry.dn, new_attributes)
        transformed_entry.change_type = entry.change_type
        transformed_entry.controls = entry.controls.copy()

        return transformed_entry
