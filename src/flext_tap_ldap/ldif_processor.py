"""LDIF processing utilities for tap-ldap.

This module provides comprehensive LDIF file processing capabilities
for the brutal simplification migration project.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar

if TYPE_CHECKING:
    from collections.abc import Iterator


logger = logging.getLogger(__name__)


class LDIFParseError(Exception):
    """Exception raised during LDIF parsing."""


class LDIFEntry:
    """Represents a single LDIF entry."""

    def __init__(self, dn: str, attributes: dict[str, list[str]] | None = None) -> None:
        """Initialize LDIF entry.

        Args:
        ----
            dn: Distinguished Name
            attributes: Entry attributes

        """
        self.dn = dn
        self.attributes = attributes or {}
        self.change_type: str | None = None
        self.controls: list[str] = []

    def get_attribute(self, name: str) -> list[str] | None:
        """Get attribute values by name (case-insensitive).

        Args:
        ----
            name: Attribute name

        Returns:
        -------
            List of attribute values or None if not found

        """
        for attr_name, values in self.attributes.items():
            if attr_name.lower() == name.lower():
                return values
        return None

    def has_object_class(self, object_class: str) -> bool:
        """Check if entry has specific object class.

        Args:
        ----
            object_class: Object class name

        Returns:
        -------
            True if entry has the object class

        """
        object_classes = self.get_attribute("objectClass") or []
        return any(oc.lower() == object_class.lower() for oc in object_classes)

    def to_dict(self) -> dict[str, Any]:
        """Convert entry to dictionary format.

        Returns
        -------
            Dictionary representation of the entry

        """
        entry_dict = {
            "dn": self.dn,
            "attributes": self.attributes,
        }

        if self.change_type:
            entry_dict["change_type"] = self.change_type

        if self.controls:
            entry_dict["controls"] = self.controls

        return entry_dict


class LDIFProcessor:
    """LDIF file processor with comprehensive parsing capabilities."""

    # Common LDIF line patterns
    DN_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"^dn:\s*(.+)$", re.IGNORECASE)
    ATTR_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"^([^:]+):\s*(.*)$")
    BASE64_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"^([^:]+)::\s*(.*)$")
    CONTROL_PATTERN: ClassVar[re.Pattern[str]] = re.compile(
        r"^control:\s*(.+)$",
        re.IGNORECASE,
    )
    CHANGETYPE_PATTERN: ClassVar[re.Pattern[str]] = re.compile(
        r"^changetype:\s*(.+)$",
        re.IGNORECASE,
    )

    def __init__(self, *, ignore_errors: bool = False, max_errors: int = 100) -> None:
        """Initialize LDIF processor.

        Args:
        ----
            ignore_errors: Whether to continue processing on errors
            max_errors: Maximum number of errors before stopping

        """
        self.ignore_errors = ignore_errors
        self.max_errors = max_errors
        self.errors: list[str] = []
        self.processed_entries = 0
        self.skipped_entries = 0

    def parse_file(self, file_path: Path) -> Iterator[LDIFEntry]:
        """Parse LDIF file and yield entries.

        Args:
        ----
            file_path: Path to LDIF file

        Yields:
        ------
            LDIFEntry objects

        Raises:
        ------
            LDIFParseError: If parsing fails and ignore_errors is False

        """
        if not file_path.exists():
            msg = f"LDIF file not found: {file_path}"
            raise LDIFParseError(msg)

        logger.info("Starting LDIF parsing: %s", file_path)

        try:
            with Path(file_path).open(encoding="utf-8") as f:
                yield from self._parse_lines(f.readlines(), str(file_path))
        except UnicodeDecodeError:
            # Try with latin-1 encoding if UTF-8 fails
            logger.warning("UTF-8 decoding failed, trying latin-1 for: %s", file_path)
            try:
                with Path(file_path).open(encoding="latin-1") as f:
                    yield from self._parse_lines(f.readlines(), str(file_path))
            except Exception as e:
                error_msg = f"Failed to parse LDIF file {file_path}: {e}"
                if self.ignore_errors:
                    logger.exception(error_msg)
                    self.errors.append(error_msg)
                    raise LDIFParseError(error_msg) from e

    def parse_content(
        self,
        content: str,
        source_name: str = "content",
    ) -> Iterator[LDIFEntry]:
        """Parse LDIF content from string.

        Args:
        ----
            content: LDIF content as string
            source_name: Name for error reporting

        Yields:
        ------
            LDIFEntry objects

        """
        lines = content.splitlines()
        yield from self._parse_lines(lines, source_name)

    def _parse_lines(self, lines: list[str], source_name: str) -> Iterator[LDIFEntry]:
        """Parse LDIF lines and yield entries.

        Args:
        ----
            lines: List of LDIF lines
            source_name: Source name for error reporting

        Yields:
        ------
            LDIFEntry objects

        """
        current_entry: LDIFEntry | None = None
        line_number = 0
        continuation_line = ""

        for line in lines:
            line_number += 1

            # Handle line continuation (lines starting with space)
            if line.startswith(" ") and continuation_line:
                continuation_line += line[1:]  # Remove leading space
                continue

            # Process the previous line if we have a continuation
            if continuation_line:
                self._process_line(
                    continuation_line,
                    current_entry,
                    line_number - 1,
                    source_name,
                )
                continuation_line = ""

            line = line.rstrip("\r\n")

            # Skip empty lines and comments
            if not line or line.startswith("#"):
                # Empty line might indicate end of entry
                if not line and current_entry and current_entry.dn:
                    yield current_entry
                    current_entry = None
                    self.processed_entries += 1
                continue

            # Check if this might be a continuation line for next iteration
            if any(
                lines[i : i + 1] and lines[i].startswith(" ")
                for i in range(line_number, min(line_number + 1, len(lines)))
            ):
                continuation_line = line
                continue

            # Process the line immediately if no continuation
            current_entry = self._process_line(
                line,
                current_entry,
                line_number,
                source_name,
            )

        # Handle any remaining continuation line
        if continuation_line:
            self._process_line(
                continuation_line,
                current_entry,
                line_number,
                source_name,
            )

        # Yield the last entry if exists
        if current_entry and current_entry.dn:
            yield current_entry
            self.processed_entries += 1

        logger.info(
            "LDIF parsing completed: %s entries processed, %s skipped, %s errors",
            self.processed_entries,
            self.skipped_entries,
            len(self.errors),
        )

    def _process_line(
        self,
        line: str,
        current_entry: LDIFEntry | None,
        line_number: int,
        source_name: str,
    ) -> LDIFEntry | None:
        """Process a single LDIF line.

        Args:
        ----
            line: LDIF line to process
            current_entry: Current entry being built
            line_number: Line number for error reporting
            source_name: Source name for error reporting

        Returns:
        -------
            Updated or new LDIFEntry

        """
        try:
            # Check for DN line (start of new entry)
            dn_match = self.DN_PATTERN.match(line)
            if dn_match:
                # Yield previous entry if exists
                if current_entry and current_entry.dn:
                    return current_entry  # Caller will yield this

                # Start new entry
                dn = dn_match.group(1).strip()
                return LDIFEntry(dn)

            # Ensure we have an entry to work with
            if not current_entry:
                error_msg = f"Line {line_number}: Attribute line without DN in {source_name}: {line}"
                self._handle_error(error_msg)
                return None

            # Check for changetype
            changetype_match = self.CHANGETYPE_PATTERN.match(line)
            if changetype_match:
                current_entry.change_type = changetype_match.group(1).strip()
                return current_entry

            # Check for control
            control_match = self.CONTROL_PATTERN.match(line)
            if control_match:
                current_entry.controls.append(control_match.group(1).strip())
                return current_entry

            # Check for base64 encoded attribute
            base64_match = self.BASE64_PATTERN.match(line)
            if base64_match:
                attr_name = base64_match.group(1).strip()
                attr_value_b64 = base64_match.group(2).strip()

                try:
                    import base64

                    attr_value = base64.b64decode(attr_value_b64).decode("utf-8")
                except Exception as e:
                    error_msg = f"Line {line_number}: Failed to decode base64 value in {source_name}: {e}"
                    self._handle_error(error_msg)
                    return current_entry

                self._add_attribute(current_entry, attr_name, attr_value)
                return current_entry

            # Check for regular attribute
            attr_match = self.ATTR_PATTERN.match(line)
            if attr_match:
                attr_name = attr_match.group(1).strip()
                attr_value = attr_match.group(2).strip()

                self._add_attribute(current_entry, attr_name, attr_value)
                return current_entry

            # Unrecognized line format
            error_msg = (
                f"Line {line_number}: Unrecognized line format in {source_name}: {line}"
            )
            self._handle_error(error_msg)
            return current_entry

        except Exception as e:
            error_msg = (
                f"Line {line_number}: Error processing line in {source_name}: {e}"
            )
            self._handle_error(error_msg)
            return current_entry

    def _add_attribute(self, entry: LDIFEntry, name: str, value: str) -> None:
        """Add attribute to entry.

        Args:
        ----
            entry: LDIFEntry to add attribute to
            name: Attribute name
            value: Attribute value

        """
        if name not in entry.attributes:
            entry.attributes[name] = []
        entry.attributes[name].append(value)

    def _handle_error(self, error_msg: str) -> None:
        """Handle parsing error.

        Args:
        ----
            error_msg: Error message

        Raises:
        ------
            LDIFParseError: If ignore_errors is False

        """
        self.errors.append(error_msg)

        if len(self.errors) > self.max_errors:
            msg = f"Too many errors (>{self.max_errors}), stopping"
            raise LDIFParseError(msg)

        if self.ignore_errors:
            logger.warning(error_msg)
            raise LDIFParseError(error_msg)

    def get_statistics(self) -> dict[str, Any]:
        """Get processing statistics.

        Returns
        -------
            Dictionary with processing statistics

        """
        return {
            "processed_entries": self.processed_entries,
            "skipped_entries": self.skipped_entries,
            "errors": len(self.errors),
            "error_messages": self.errors.copy(),
        }


class LDIFValidator:
    """LDIF content validator for migration scenarios."""

    def __init__(self) -> None:
        """Initialize LDIF validator."""
        self.validation_errors: list[str] = []
        self.warnings: list[str] = []

    def validate_entry(self, entry: LDIFEntry) -> bool:
        """Validate a single LDIF entry.

        Args:
        ----
            entry: LDIFEntry to validate

        Returns:
        -------
            True if entry is valid

        """
        is_valid = True

        # Check for required DN
        if not entry.dn or not entry.dn.strip():
            self.validation_errors.append("Entry missing DN")
            is_valid = False

        # Check for object classes
        object_classes = entry.get_attribute("objectClass")
        if not object_classes:
            self.validation_errors.append(f"Entry {entry.dn}: Missing objectClass")
            is_valid = False

        # Check for structural object class
        if object_classes:
            has_structural = any(
                oc.lower()
                in {"top", "person", "organizationalunit", "organization", "domain"}
                for oc in object_classes
            )
            if not has_structural:
                self.warnings.append(
                    f"Entry {entry.dn}: No structural objectClass found",
                )

        # Validate DN format
        if entry.dn and not self._is_valid_dn(entry.dn):
            self.validation_errors.append(f"Entry {entry.dn}: Invalid DN format")
            is_valid = False

        return is_valid

    def _is_valid_dn(self, dn: str) -> bool:
        """Validate DN format.

        Args:
        ----
            dn: Distinguished Name to validate

        Returns:
        -------
            True if DN format is valid

        """
        # Basic DN validation - should contain at least one component
        return bool(dn and "=" in dn)

    def get_validation_results(self) -> dict[str, Any]:
        """Get validation results.

        Returns
        -------
            Dictionary with validation results

        """
        return {
            "errors": self.validation_errors.copy(),
            "warnings": self.warnings.copy(),
            "is_valid": len(self.validation_errors) == 0,
        }


class LDIFTransformer:
    """Transform LDIF entries for target directory compatibility."""

    def __init__(self, transformation_rules: dict[str, Any] | None = None) -> None:
        """Initialize LDIF transformer.

        Args:
        ----
            transformation_rules: Rules for transforming entries

        """
        self.transformation_rules = transformation_rules or {}

    def transform_entry(self, entry: LDIFEntry) -> LDIFEntry:
        """Transform LDIF entry based on rules.

        Args:
        ----
            entry: Original LDIFEntry

        Returns:
        -------
            Transformed LDIFEntry

        """
        # For now, return entry as-is
        # In the future, this will apply complex transformation rules
        return entry

    def apply_attribute_mappings(
        self,
        entry: LDIFEntry,
        mappings: dict[str, str],
    ) -> LDIFEntry:
        """Apply attribute name mappings to entry.

        Args:
        ----
            entry: LDIFEntry to transform
            mappings: Dictionary of old_name -> new_name mappings

        Returns:
        -------
            Transformed LDIFEntry

        """
        new_attributes: dict[str, Any] = {}

        for attr_name, values in entry.attributes.items():
            new_name = mappings.get(attr_name, attr_name)
            new_attributes[new_name] = values

        transformed_entry = LDIFEntry(entry.dn, new_attributes)
        transformed_entry.change_type = entry.change_type
        transformed_entry.controls = entry.controls.copy()

        return transformed_entry
