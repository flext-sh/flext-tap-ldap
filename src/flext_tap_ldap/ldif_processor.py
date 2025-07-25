"""LDIF processing utilities for tap-ldap.

This module provides comprehensive LDIF file processing capabilities
for the brutal simplification migration project.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar

if TYPE_CHECKING:
    from collections.abc import Iterator

from flext_core import (
    FlextResult,
    get_logger,
)

logger = get_logger(__name__)


class LDIFParseError(Exception):
    """Exception raised during LDIF parsing."""


class LDIFEntry:
    """Represents a single LDIF entry."""

    def __init__(self, dn: str, attributes: dict[str, list[str]] | None = None) -> None:
        self.dn = dn
        self.attributes = attributes or {}
        self.change_type: str | None = None
        self.controls: list[str] = []

    def get_attribute(self, name: str) -> list[str]:
        for attr_name, values in self.attributes.items():
            if attr_name.lower() == name.lower():
                return values
        return []

    def has_object_class(self, object_class: str) -> bool:
        object_classes = self.get_attribute("objectClass") or []
        return any(oc.lower() == object_class.lower() for oc in object_classes)

    def to_dict(self) -> dict[str, Any]:
        entry_dict = {
            "dn": self.dn,
            "attributes": self.attributes,
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
        """Check if the entry is valid."""
        # Check basic DN validity
        if not (self.dn and self.dn.strip()):
            return False

        # Check objectClass-specific requirements
        object_classes = self.get_attribute("objectClass")
        if object_classes:
            for oc in object_classes:
                oc_lower = oc.lower()
                if oc_lower == "inetorgperson":
                    # inetOrgPerson requires cn and sn
                    if not self.get_attribute("cn") or not self.get_attribute("sn"):
                        return False
                elif oc_lower == "organizationalunit" and not self.get_attribute("ou"):
                    # organizationalUnit requires ou
                    return False

        return True

    @property
    def validation_errors(self) -> list[dict[str, str]]:
        """Get validation errors for this entry."""
        errors = []

        if not self.dn or not self.dn.strip():
            errors.append({"code": "empty_dn", "message": "DN is empty or missing"})

        # Check for basic objectClass requirements
        object_classes = self.get_attribute("objectClass") or []
        for oc in object_classes:
            oc_lower = oc.lower()
            if oc_lower == "inetorgperson":
                if not self.get_attribute("cn"):
                    errors.append(
                        {
                            "code": "missing_cn",
                            "message": "inetOrgPerson requires cn attribute",
                        },
                    )
                if not self.get_attribute("sn"):
                    errors.append(
                        {
                            "code": "missing_sn",
                            "message": "inetOrgPerson requires sn attribute",
                        },
                    )

        return errors

    def parse_dn(self) -> dict[str, Any]:
        """Parse DN into components."""
        components: dict[str, Any] = {}

        # Split DN by commas, but be careful about escaped commas
        parts = []
        current_part = ""
        i = 0
        while i < len(self.dn):
            if self.dn[i] == "," and (i == 0 or self.dn[i - 1] != "\\"):
                parts.append(current_part.strip())
                current_part = ""
            else:
                current_part += self.dn[i]
            i += 1
        if current_part:
            parts.append(current_part.strip())

        for part in parts:
            if "=" in part:
                key, value = part.split("=", 1)
                key = key.strip()
                value = value.strip()

                if key in components:
                    if not isinstance(components[key], list):
                        components[key] = [components[key]]
                    components[key].append(value)
                else:
                    components[key] = value

        # Convert single-item values to lists for multi-valued attributes like 'dc'
        for key in ["dc"]:
            if key in components and not isinstance(components[key], list):
                components[key] = [components[key]]

        return components

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
    """LDIF file processor with comprehensive parsing capabilities."""

    # Common LDIF line patterns
    DN_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"^dn:\s*(.+)$", re.IGNORECASE)
    ATTR_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"^([^:]+):\s*(.*)$")
    BASE64_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"^([^:]+):\s*(.*)$")
    CONTROL_PATTERN: ClassVar[re.Pattern[str]] = re.compile(
        r"^control:\s*(.+)$",
        re.IGNORECASE,
    )
    CHANGETYPE_PATTERN: ClassVar[re.Pattern[str]] = re.compile(
        r"^changetype:\s*(.+)$",
        re.IGNORECASE,
    )

    def __init__(self, *, ignore_errors: bool = True, max_errors: int = 100) -> None:
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

    def parse_file(self, file_path: Path) -> Iterator[LDIFEntry]:
        if not file_path.exists():
            msg = f"LDIF file not found: {file_path}"
            raise ValueError(msg)

        logger.info(f"Starting LDIF parsing: {file_path}")
        try:
            with Path(file_path).open(encoding="utf-8") as f:
                yield from self._parse_lines(f.readlines(), str(file_path))
        except UnicodeDecodeError:
            # Try with latin-1 encoding if UTF-8 fails
            logger.warning(f"UTF-8 decoding failed, trying latin-1 for: {file_path}")
            with Path(file_path).open(encoding="latin-1") as f:
                yield from self._parse_lines(f.readlines(), str(file_path))
        except Exception as e:
            error_msg = f"Failed to parse LDIF file {file_path}: {e}"
            if self.ignore_errors:
                logger.exception(error_msg)
                self.errors.append(error_msg)
            else:
                raise ValueError(error_msg) from None

    def parse_content(
        self,
        content: str,
        source_name: str = "content",
    ) -> Iterator[LDIFEntry]:
        lines = content.splitlines()
        yield from self._parse_lines(lines, source_name)

    def _parse_lines(self, lines: list[str], source_name: str) -> Iterator[LDIFEntry]:
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

            stripped_line = line.rstrip("\r\n")

            # Skip empty lines and comments
            if not stripped_line or stripped_line.startswith("#"):
                # Empty line might indicate end of entry
                if not stripped_line and current_entry and current_entry.dn:
                    yield current_entry
                    current_entry = None
                    self.processed_entries += 1
                continue

            # Check if this might be a continuation line for next iteration
            if any(
                lines[i : i + 1] and lines[i].startswith(" ")
                for i in range(line_number, min(line_number + 1, len(lines)))
            ):
                continuation_line = stripped_line
                continue

            # Process the line immediately if no continuation
            current_entry = self._process_line(
                stripped_line,
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
            f"LDIF parsing completed: {self.processed_entries} entries processed, "
            f"{self.skipped_entries} skipped, {len(self.errors)} errors"
        )

    def _process_line(
        self,
        line: str,
        current_entry: LDIFEntry | None,
        line_number: int,
        source_name: str,
    ) -> LDIFEntry | None:
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

            # Check for base64 encoded attribute (indicated by ::)
            if "::" in line:
                parts = line.split("::", 1)
                if len(parts) == 2:
                    attr_name = parts[0].strip()
                    attr_value_b64 = parts[1].strip()
                    try:
                        import base64

                        attr_value = base64.b64decode(attr_value_b64).decode("utf-8")
                        current_entry.attributes[attr_name] = [attr_value]
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
        if name not in entry.attributes:
            entry.attributes[name] = []
        entry.attributes[name].append(value)

    def _handle_error(self, error_msg: str) -> None:
        self.errors.append(error_msg)

        if len(self.errors) > self.max_errors:
            msg = f"Too many errors (>{self.max_errors}), stopping"
            raise ValueError(msg)

        if self.ignore_errors:
            logger.warning(error_msg)
        else:
            raise ValueError(msg)

    def get_statistics(self) -> dict[str, Any]:
        return {
            "processed_entries": self.processed_entries,
            "skipped_entries": self.skipped_entries,
            "errors": len(self.errors),
            "error_messages": self.errors.copy(),
        }

    def load_from_file(self, file_path: Path) -> FlextResult[Any]:
        """Load LDIF entries from file and return as FlextResult."""
        try:
            self.entries = list(self.parse_file(file_path))
            self._update_stats()
            return FlextResult.ok("LDIF file loaded successfully")
        except Exception as e:
            return FlextResult.fail(f"Failed to load LDIF file: {e}")

    def load_from_string(
        self,
        content: str,
        source_name: str = "string",
    ) -> FlextResult[Any]:
        """Load LDIF entries from string and return as FlextResult."""
        try:
            self.entries = list(self.parse_content(content, source_name))
            self._update_stats()
            return FlextResult.ok("LDIF content loaded successfully")
        except Exception as e:
            return FlextResult.fail(f"Failed to load LDIF content: {e}")

    def _update_stats(self) -> None:
        """Update statistics based on loaded entries."""
        self.stats["total_entries"] = len(self.entries)

        valid_count = 0
        invalid_count = 0

        # Use comprehensive validation that includes objectClass requirements
        validator = LDIFValidator()

        for entry in self.entries:
            if entry.is_valid() and validator.validate_entry(entry):
                valid_count += 1
            else:
                invalid_count += 1

        # If we had parsing errors but no entries, count errors as invalid entries
        if len(self.entries) == 0 and len(self.errors) > 0:
            invalid_count = len(self.errors)

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

    def to_singer_format(self, stream_name: str) -> list[dict[str, Any]]:
        """Convert LDIF entries to Singer record format."""
        records = []

        for entry in self.entries:
            record = {
                "type": "RECORD",
                "stream": stream_name,
                "record": {
                    "dn": entry.dn,
                    **dict(entry.attributes.items()),
                },
            }
            records.append(record)

        return records


class LDIFValidator:
    """LDIF content validator for migration scenarios."""

    def __init__(self) -> None:
        self.validation_errors: list[str] = []
        self.warnings: list[str] = []

    def validate_entry(self, entry: LDIFEntry) -> bool:
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

        # Validate objectClass-specific requirements
        if object_classes:
            for oc in object_classes:
                oc_lower = oc.lower()
                if oc_lower == "inetorgperson":
                    # inetOrgPerson requires cn and sn
                    if not entry.get_attribute("cn"):
                        self.validation_errors.append(
                            f"Entry {entry.dn}: inetOrgPerson requires cn attribute",
                        )
                        is_valid = False
                    if not entry.get_attribute("sn"):
                        self.validation_errors.append(
                            f"Entry {entry.dn}: inetOrgPerson requires sn attribute",
                        )
                        is_valid = False
                elif oc_lower == "organizationalunit":
                    # organizationalUnit requires ou
                    if not entry.get_attribute("ou"):
                        self.validation_errors.append(
                            f"Entry {entry.dn}: organizationalUnit requires ou attribute",
                        )
                        is_valid = False

        return is_valid

    def _is_valid_dn(self, dn: str) -> bool:
        # Basic DN validation - should contain at least one valid component
        if not dn or not dn.strip():
            return False

        # Split DN by commas to get components
        components = []
        current_part = ""
        i = 0
        while i < len(dn):
            if dn[i] == "," and (i == 0 or dn[i - 1] != "\\"):
                components.append(current_part.strip())
                current_part = ""
            else:
                current_part += dn[i]
            i += 1
        if current_part:
            components.append(current_part.strip())

        # Each component must have format attribute=value with non-empty parts
        for component in components:
            if not component or "=" not in component:
                return False

            parts = component.split("=", 1)
            if len(parts) != 2:
                return False

            attr_name = parts[0].strip()
            attr_value = parts[1].strip()

            if not attr_name or not attr_value:
                return False

        return True

    def get_validation_results(self) -> dict[str, Any]:
        return {
            "errors": self.validation_errors.copy(),
            "warnings": self.warnings.copy(),
            "is_valid": len(self.validation_errors) == 0,
        }

    def validate_dn_format(self, dn: str) -> bool:
        """Validate DN format."""
        return self._is_valid_dn(dn)

    def validate_objectclass_requirements(self, entry: LDIFEntry) -> bool:
        """Validate that entry meets objectClass requirements."""
        object_classes = entry.get_attribute("objectClass") or []

        for oc in object_classes:
            oc_lower = oc.lower()
            if oc_lower == "inetorgperson":
                # inetOrgPerson requires cn and sn
                if not entry.get_attribute("cn") or not entry.get_attribute("sn"):
                    return False
            elif oc_lower == "organizationalunit" and not entry.get_attribute("ou"):
                # organizationalUnit requires ou
                return False

        return True

    def validate_attribute_syntax(self, attr_name: str, attr_value: str) -> bool:
        """Validate attribute syntax."""
        attr_lower = attr_name.lower()

        if attr_lower == "mail":
            # Simple email validation
            return "@" in attr_value and "." in attr_value.split("@")[-1]
        if attr_lower == "telephonenumber":
            # Simple phone validation - allow digits, spaces, dashes, plus
            import re

            phone_pattern = r"^[\d\s\-\+\(\)\.]+$"
            return bool(re.match(phone_pattern, attr_value))

        # Default: accept all other attributes
        return True

    def validate_entries(self, entries: list[LDIFEntry]) -> dict[str, Any]:
        """Validate a list of LDIF entries."""
        valid_count = 0
        invalid_count = 0
        errors = []

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
    """Transform LDIF entries for target directory compatibility."""

    def __init__(self, transformation_rules: dict[str, Any] | None = None) -> None:
        self.transformation_rules = transformation_rules or {}

    def transform_entry(self, entry: LDIFEntry) -> LDIFEntry:
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
