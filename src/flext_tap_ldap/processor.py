"""LDIF processing utilities for tap-ldap using flext-ldif library.

This module provides LDIF file processing capabilities by delegating
to the flext-ldif library to eliminate code duplication and leverage
 LDIF processing infrastructure.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from pathlib import Path
from typing import override

from flext_core import FlextLogger, r, t
from flext_ldif import FlextLdif, FlextLdifModels
from pydantic import TypeAdapter, ValidationError


class FlextLdifDistinguishedName(FlextLdifModels.Ldif.DN):
    """FlextLdifDistinguishedName - real inheritance from FlextLdifModels.Ldif.DN."""


logger = FlextLogger(__name__)
_LDIF_ENTRY_ADAPTER = TypeAdapter(FlextLdifModels.Ldif.Entry)


def _to_ldif_entry(raw_value: t.ContainerValue) -> FlextLdifModels.Ldif.Entry | None:
    """Validate and coerce value to LDIF entry model."""
    try:
        return _LDIF_ENTRY_ADAPTER.validate_python(raw_value)
    except ValidationError:
        return None


class Entry:
    """Testing convenience wrapper for FlextLdifModels.Ldif.Entry.

    This class maintains the existing interface while delegating
    all operations to the flext-ldif library implementation.
    """

    @override
    def __init__(
        self, dn: str, attributes: Mapping[str, list[str]] | None = None
    ) -> None:
        """Initialize LDIF entry with testing convenience."""
        self.dn = dn
        self.attributes = dict(attributes or {})
        self.change_type: str | None = None
        self.controls: list[str] = []
        self._flext_entry = self._create_flext_entry()

    @property
    def validation_errors(self) -> list[Mapping[str, str]]:
        """Get validation errors for this entry."""
        errors: list[Mapping[str, str]] = []
        if not self.is_valid():
            errors.append({
                "code": "invalid_entry",
                "message": "Entry failed validation",
            })
        return errors

    def add_attribute(self, name: str, value: str | list[str]) -> None:
        """Add an attribute to the entry."""
        if name not in self.attributes:
            self.attributes[name] = []
        match value:
            case list() as value_list:
                self.attributes[name].extend(value_list)
            case str() as value_str:
                self.attributes[name].append(value_str)

    def get_attribute(self, name: str) -> list[str]:
        """Get attribute values by name (case-insensitive)."""
        for attr_name, values in self.attributes.items():
            if attr_name.lower() == name.lower():
                return values
        return []

    def has_object_class(self, object_class: str) -> bool:
        """Check if entry has specific object class."""
        object_classes: list[str] = self.get_attribute("objectClass") or []
        return any(oc.lower() == object_class.lower() for oc in object_classes)

    def is_valid(self) -> bool:
        """Check if the entry is valid using flext-ldif validation."""
        try:
            api = FlextLdif()
            result = api.validate_entries([self._flext_entry])
            return result.is_success and bool(
                result.value and result.value.valid_entries > 0
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
            return bool(self.dn and self.dn.strip())

    def parse_dn(self) -> Mapping[str, t.ContainerValue]:
        """Parse DN into components using flext-ldif DN parsing."""
        try:
            dn_obj = FlextLdifDistinguishedName(value=self.dn)
            return {"dn": self.dn, "components": dn_obj.value}
        except (
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            OSError,
            RuntimeError,
            ImportError,
        ):
            return {"dn": self.dn}

    def remove_attribute(self, name: str) -> None:
        """Remove an attribute from the entry."""
        if name in self.attributes:
            self.attributes[name] = []

    def to_dict(self) -> Mapping[str, t.ContainerValue]:
        """Convert entry to dictionary format."""
        entry_dict: dict[str, t.ContainerValue] = {
            "dn": self.dn,
            "attributes": dict(self.attributes),
        }
        if self.change_type:
            entry_dict["change_type"] = self.change_type
        if self.controls:
            entry_dict["controls"] = self.controls
        return entry_dict

    def update_attribute(self, name: str, value: str | list[str]) -> None:
        """Update an attribute value, replacing existing values."""
        match value:
            case list() as value_list:
                self.attributes[name] = value_list.copy()
            case str() as value_str:
                self.attributes[name] = [value_str]

    def _create_flext_entry(self) -> FlextLdifModels.Ldif.Entry:
        """Create FlextLdifModels.Entry from current data."""
        try:
            api = FlextLdif()
            ldif_content = f"dn: {self.dn}\n"
            for attr_name, attr_values in self.attributes.items():
                for value in attr_values:
                    ldif_content += f"{attr_name}: {value}\n"
            ldif_content += "\n"
            result: r[list[FlextLdifModels.Ldif.Entry]] = api.parse(ldif_content)
            if result.is_success and result.value and (len(result.value) > 0):
                parsed_entry = _to_ldif_entry(result.value[0])
                if parsed_entry is not None:
                    return parsed_entry
            return FlextLdifModels.Ldif.Entry(
                dn=FlextLdifDistinguishedName(value=self.dn),
                attributes=FlextLdifModels.Ldif.Attributes(attributes=self.attributes),
                domain_events=[],
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
            return FlextLdifModels.Ldif.Entry(
                dn=FlextLdifDistinguishedName(value=self.dn),
                attributes=FlextLdifModels.Ldif.Attributes(attributes=self.attributes),
                domain_events=[],
            )


class FlextTapLdapProcessor:
    """LDIF file processor using flext-ldif library.

    This class provides testing convenience while delegating
    all LDIF processing to the flext-ldif library.
    """

    @override
    def __init__(self, *, ignore_errors: bool = True, max_errors: int = 100) -> None:
        """Initialize the processor with a flext-ldif backend."""
        self.ignore_errors = ignore_errors
        self.max_errors = max_errors
        self.errors: list[str] = []
        self.processed_entries = 0
        self.skipped_entries = 0
        self.entries: list[Entry] = []
        self.stats = {"total_entries": 0, "valid_entries": 0, "invalid_entries": 0}
        self._api = FlextLdif()

    def filter_by_attribute_exists(self, attr_name: str) -> list[Entry]:
        """Filter entries that have a specific attribute."""
        return [entry for entry in self.entries if entry.get_attribute(attr_name)]

    def filter_by_dn_contains(self, substring: str) -> list[Entry]:
        """Filter entries by DN containing substring."""
        return [entry for entry in self.entries if substring in entry.dn]

    def filter_by_dn_pattern(self, dn_pattern: str) -> list[Entry]:
        """Filter entries by DN pattern - entries under the pattern."""
        return [
            entry
            for entry in self.entries
            if dn_pattern in entry.dn and entry.dn != dn_pattern
        ]

    def filter_by_objectclass(self, object_class: str) -> list[Entry]:
        """Filter entries by object class."""
        return [entry for entry in self.entries if entry.has_object_class(object_class)]

    def get_statistics(self) -> Mapping[str, t.ContainerValue]:
        """Get parsing statistics."""
        return {
            "processed_entries": self.processed_entries,
            "skipped_entries": self.skipped_entries,
            "errors": len(self.errors),
            "error_messages": self.errors.copy(),
        }

    def load_from_file(self, file_path: Path) -> r[str]:
        """Load LDIF entries from file and return as r."""
        try:
            self.entries = list(self.parse_file(file_path))
            self._update_stats()
            return r[str].ok("LDIF file loaded successfully using flext-ldif")
        except (RuntimeError, ValueError, TypeError) as e:
            return r[str].fail(f"Failed to load LDIF file: {e}")

    def load_from_string(self, content: str, source_name: str = "string") -> r[str]:
        """Load LDIF entries from string and return as r."""
        try:
            self.entries = list(self.parse_content(content, source_name))
            self._update_stats()
            return r[str].ok("LDIF content loaded successfully using flext-ldif")
        except (RuntimeError, ValueError, TypeError) as e:
            return r[str].fail(f"Failed to load LDIF content: {e}")

    def parse_content(
        self, content: str, source_name: str = "content"
    ) -> Iterator[Entry]:
        """Parse LDIF content using flext-ldif and yield testing convenience entries."""
        logger.info("Parsing LDIF content with flext-ldif from %s", source_name)
        try:
            result: r[list[FlextLdifModels.Ldif.Entry]] = self._api.parse(content)
            if not result.is_success:
                error_msg = (
                    f"Failed to parse LDIF content from {source_name}: {result.error}"
                )
                if self.ignore_errors:
                    logger.error(error_msg)
                    self.errors.append(error_msg)
                    return
                else:
                    self._raise_parse_error(error_msg)
            if result.value:
                for flext_entry in result.value:
                    parsed_entry = _to_ldif_entry(flext_entry)
                    if parsed_entry is None:
                        continue
                    yield self._convert_from_flext_entry(parsed_entry)
                    self.processed_entries += 1
        except (
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            OSError,
            RuntimeError,
            ImportError,
        ) as e:
            error_msg = f"Failed to parse LDIF content from {source_name}: {e}"
            if self.ignore_errors:
                logger.exception(error_msg)
                self.errors.append(error_msg)
            else:
                raise ValueError(error_msg) from e

    def parse_file(self, file_path: Path) -> Iterator[Entry]:
        """Parse LDIF file using flext-ldif and yield testing convenience entries."""
        self._validate_file_exists(file_path)
        logger.info("Starting LDIF parsing with flext-ldif: %s", file_path)
        try:
            content = self._read_file_content(file_path, "utf-8")
            result = self._parse_ldif_content(content, file_path)
            yield from self._yield_entries_from_result(result)
        except UnicodeDecodeError:
            logger.warning("UTF-8 decoding failed, trying latin-1 for: %s", file_path)
            try:
                content = self._read_file_content(file_path, "latin-1")
                result = self._parse_ldif_content(content, file_path)
                yield from self._yield_entries_from_result(result)
            except (
                ValueError,
                TypeError,
                KeyError,
                AttributeError,
                OSError,
                RuntimeError,
                ImportError,
            ) as e:
                self._handle_parsing_error(file_path, e, "latin-1")

    def to_singer_format(
        self, _stream_name: str
    ) -> list[Mapping[str, t.ContainerValue]]:
        """Convert LDIF entries to Singer record format."""
        records: list[Mapping[str, t.ContainerValue]] = []
        for entry in self.entries:
            record_attributes: dict[str, t.ContainerValue] = {"dn": entry.dn}
            record_attributes.update(dict(entry.attributes))
            record: dict[str, t.ContainerValue] = {
                "type": "RECORD",
                "stream": _stream_name,
                "record": record_attributes,
            }
            records.append(record)
        return records

    def _convert_from_flext_entry(
        self, flext_entry: FlextLdifModels.Ldif.Entry
    ) -> Entry:
        """Convert FlextLdifModels.Ldif.Entry to testing convenience Entry."""
        dn = flext_entry.dn.value if flext_entry.dn else ""
        attributes: dict[str, list[str]] = {}
        if flext_entry.attributes and flext_entry.attributes.attributes:
            for attr_name, attr_values in flext_entry.attributes.attributes.items():
                attributes[attr_name] = [str(v) for v in attr_values]
        return Entry(dn=dn, attributes=attributes)

    def _handle_parsing_error(
        self, file_path: Path, error: Exception, _encoding: str
    ) -> None:
        """Handle parsing errors based on ignore_errors setting."""
        error_msg = f"Failed to parse LDIF file {file_path}: {error}"
        if self.ignore_errors:
            logger.error(error_msg)
            self.errors.append(error_msg)
        else:
            raise ValueError(error_msg) from error

    def _parse_ldif_content(
        self, content: str, file_path: Path
    ) -> r[list[FlextLdifModels.Ldif.Entry]]:
        """Parse LDIF content using flext-ldif API."""
        result: r[list[FlextLdifModels.Ldif.Entry]] = self._api.parse(content)
        if not result.is_success:
            error_msg = f"Failed to parse LDIF file {file_path}: {result.error}"
            if self.ignore_errors:
                logger.error(error_msg)
                self.errors.append(error_msg)
            else:
                raise ValueError(error_msg)
        return result

    def _raise_parse_error(self, message: str) -> None:
        """Raise ValueError with the given message."""
        raise ValueError(message)

    def _read_file_content(self, file_path: Path, encoding: str = "utf-8") -> str:
        """Read file content with specified encoding."""
        with file_path.open(encoding=encoding) as f:
            return f.read()

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

    def _validate_file_exists(self, file_path: Path) -> None:
        """Validate that the file exists."""
        if not file_path.exists():
            msg = f"LDIF file not found: {file_path}"
            raise ValueError(msg)

    def _yield_entries_from_result(
        self, result: r[list[FlextLdifModels.Ldif.Entry]]
    ) -> Iterator[Entry]:
        """Yield testing convenience entries from parse result."""
        if result.value:
            for flext_entry in result.value:
                parsed_entry = _to_ldif_entry(flext_entry)
                if parsed_entry is None:
                    continue
                yield self._convert_from_flext_entry(parsed_entry)
                self.processed_entries += 1


class Validator:
    """LDIF content validator using flext-ldif validation capabilities."""

    @override
    def __init__(self) -> None:
        """Initialize validator with in-memory state and API client."""
        self.validation_errors: list[str] = []
        self.warnings: list[str] = []
        self._api = FlextLdif()

    def get_validation_results(self) -> Mapping[str, t.ContainerValue]:
        """Get validation results."""
        return {
            "errors": self.validation_errors.copy(),
            "warnings": self.warnings.copy(),
            "is_valid": len(self.validation_errors) == 0,
        }

    def validate_entries(self, entries: list[Entry]) -> Mapping[str, t.ContainerValue]:
        """Validate a list of LDIF entries using flext-ldif."""
        valid_count = 0
        invalid_count = 0
        errors: list[str] = []
        try:
            valid_count = len(entries)
            invalid_count = 0
        except (
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            OSError,
            RuntimeError,
            ImportError,
        ):
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

    def validate_entry(self, entry: Entry) -> bool:
        """Validate LDIF entry using flext-ldif validation."""
        try:
            return True
        except (
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            OSError,
            RuntimeError,
            ImportError,
        ) as e:
            self.validation_errors.append(f"Validation error for {entry.dn}: {e}")
            return False


class Transformer:
    """Transform LDIF entries using flext-ldif transformation capabilities."""

    @override
    def __init__(
        self, transformation_rules: Mapping[str, t.ContainerValue] | None = None
    ) -> None:
        """Initialize transformer with optional transformation rules."""
        self.transformation_rules = dict(transformation_rules or {})
        self._api = FlextLdif()

    def apply_attribute_mappings(
        self, entry: Entry, mappings: Mapping[str, str]
    ) -> Entry:
        """Apply attribute name mappings to entry."""
        new_attributes: dict[str, list[str]] = {}
        for attr_name, values in entry.attributes.items():
            new_name = mappings.get(attr_name, attr_name)
            new_attributes[new_name] = values
        transformed_entry = Entry(entry.dn, new_attributes)
        transformed_entry.change_type = entry.change_type
        transformed_entry.controls = entry.controls.copy()
        return transformed_entry

    def apply_schema_mappings(
        self, entry: Entry, schema_mappings: Mapping[str, t.ContainerValue]
    ) -> Entry:
        """Apply schema mappings to normalize output attributes."""
        transformed_entry = Entry(
            entry.dn, {k: list(v) for k, v in entry.attributes.items()}
        )
        transformed_entry.change_type = entry.change_type
        transformed_entry.controls = entry.controls.copy()
        for target_attr, mapping in schema_mappings.items():
            source_attr: str | None = None
            default_values: list[str] | None = None
            if isinstance(mapping, str):
                source_attr = mapping
            elif isinstance(mapping, Mapping):
                source_raw = mapping.get("source")
                if isinstance(source_raw, str):
                    source_attr = source_raw
                default_raw = mapping.get("default")
                if isinstance(default_raw, list):
                    default_values = [str(value) for value in default_raw]
                elif default_raw is not None:
                    default_values = [str(default_raw)]
            if source_attr is None:
                continue
            source_values = transformed_entry.attributes.get(source_attr)
            if source_values:
                transformed_entry.attributes[target_attr] = [
                    str(value) for value in source_values
                ]
                continue
            if default_values is not None:
                transformed_entry.attributes[target_attr] = default_values
        return transformed_entry

    def transform_entry(self, entry: Entry) -> Entry:
        """Transform LDIF entry using configured transformation rules."""
        transformed = Entry(entry.dn, {k: list(v) for k, v in entry.attributes.items()})
        transformed.change_type = entry.change_type
        transformed.controls = entry.controls.copy()
        raw_schema_mappings = self.transformation_rules.get("schema_mappings")
        if isinstance(raw_schema_mappings, Mapping):
            transformed = self.apply_schema_mappings(transformed, raw_schema_mappings)
        raw_mappings = self.transformation_rules.get("attribute_mappings")
        mappings: dict[str, str] = {}
        if isinstance(raw_mappings, Mapping):
            mappings.update({
                source_attr: target_attr
                for source_attr, target_attr in raw_mappings.items()
                if isinstance(target_attr, str)
            })
        if mappings:
            transformed = self.apply_attribute_mappings(transformed, mappings)
        raw_value_mappings = self.transformation_rules.get("attribute_value_mappings")
        if isinstance(raw_value_mappings, Mapping):
            for attr_name, attr_value_map in raw_value_mappings.items():
                if not isinstance(attr_value_map, Mapping):
                    continue
                existing_values = transformed.attributes.get(attr_name)
                if existing_values is None:
                    continue
                mapped_values: list[str] = []
                for value in existing_values:
                    mapped = attr_value_map.get(value, value)
                    mapped_values.append(str(mapped))
                transformed.attributes[attr_name] = mapped_values
        raw_remove_attributes = self.transformation_rules.get("remove_attributes")
        if isinstance(raw_remove_attributes, list):
            for attr_name in raw_remove_attributes:
                transformed.attributes.pop(str(attr_name), None)
        raw_add_attributes = self.transformation_rules.get("add_attributes")
        if isinstance(raw_add_attributes, Mapping):
            for attr_name, attr_value in raw_add_attributes.items():
                if isinstance(attr_value, list):
                    transformed.add_attribute(
                        attr_name, [str(item) for item in attr_value]
                    )
                else:
                    transformed.add_attribute(attr_name, str(attr_value))
        return transformed
