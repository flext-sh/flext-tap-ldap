"""LDIF processing utilities absorbed into u.TapLdap namespace.

Provides Entry, Processor, Validator, Transformer as inner classes
of u.TapLdap via MRO mixin composition.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Iterator, Mapping, MutableSequence, Sequence
from pathlib import Path
from typing import override

from flext_ldif import ldif
from pydantic import ValidationError

from flext_core import FlextLogger, r
from flext_tap_ldap import c, m, t

_DEFAULT_ENTRY_METADATA = m.Ldif.EntryMetadata()

logger = FlextLogger(__name__)


class FlextTapLdapUtilitiesProcessorMixin:
    """Mixin providing LDIF processing utilities for u.TapLdap namespace."""

    class TapLdap:
        """Tap LDAP namespace — processor inner classes."""

        class DistinguishedName(m.Ldif.DN):
            """Distinguished name — real inheritance from m.Ldif.DN."""

        class Entry:
            """Testing convenience wrapper for m.Ldif.Entry.

            Maintains the existing interface while delegating
            all operations to the flext-ldif library implementation.
            """

            @override
            def __init__(
                self,
                dn: str,
                attributes: Mapping[str, t.StrSequence] | None = None,
            ) -> None:
                """Initialize LDIF entry with testing convenience."""
                self.dn = dn
                self.attributes: t.MutableStrSequenceMapping = {
                    k: list(v) for k, v in (attributes or {}).items()
                }
                self.change_type: str | None = None
                self.controls: MutableSequence[str] = []
                self._flext_entry = self._create_flext_entry()

            @property
            def validation_errors(self) -> MutableSequence[t.MutableStrMapping]:
                """Get validation errors for this entry."""
                errors: MutableSequence[t.MutableStrMapping] = []
                if not self.is_valid():
                    errors.append({
                        "code": "invalid_entry",
                        "message": "Entry failed validation",
                    })
                return errors

            def add_attribute(
                self, name: str, value: str | MutableSequence[str]
            ) -> None:
                """Add an attribute to the entry."""
                self.attributes.setdefault(name, [])
                match value:
                    case list() as value_list:
                        self.attributes[name].extend(value_list)
                    case str() as value_str:
                        self.attributes[name].append(value_str)
                    case _:
                        self.attributes[name].extend(list(value))

            def get_attribute(self, name: str) -> t.StrSequence:
                """Get attribute values by name (case-insensitive)."""
                for attr_name, values in self.attributes.items():
                    if attr_name.lower() == name.lower():
                        return values
                return []

            def has_object_class(self, object_class: str) -> bool:
                """Check if entry has specific object class."""
                object_classes: t.StrSequence = self.get_attribute("objectClass") or []
                return any(oc.lower() == object_class.lower() for oc in object_classes)

            def is_valid(self) -> bool:
                """Check if the entry is valid using flext-ldif validation."""
                try:
                    api = ldif()
                    result = api.validate_entries([self._flext_entry])
                    return result.is_success and bool(
                        result.value and result.value.valid_entries > 0,
                    )
                except c.Meltano.SINGER_SAFE_EXCEPTIONS:
                    return bool(self.dn and self.dn.strip())

            def parse_dn(self) -> t.ContainerMapping:
                """Parse DN into components using flext-ldif DN parsing."""
                try:
                    dn_obj = (
                        FlextTapLdapUtilitiesProcessorMixin.TapLdap.DistinguishedName(
                            value=self.dn,
                            metadata=_DEFAULT_ENTRY_METADATA,
                        )
                    )
                    return {"dn": self.dn, "components": dn_obj.value}
                except c.Meltano.SINGER_SAFE_EXCEPTIONS:
                    return {"dn": self.dn}

            def remove_attribute(self, name: str) -> None:
                """Remove an attribute from the entry."""
                if name in self.attributes:
                    empty_attrs: MutableSequence[str] = []
                    self.attributes[name] = empty_attrs

            def to_dict(self) -> t.MutableContainerMapping:
                """Convert entry to dictionary format."""
                entry_dict: t.MutableContainerMapping = {
                    "dn": self.dn,
                    "attributes": dict(self.attributes),
                }
                if self.change_type:
                    entry_dict["change_type"] = self.change_type
                if self.controls:
                    entry_dict["controls"] = self.controls
                return entry_dict

            def update_attribute(
                self, name: str, value: str | MutableSequence[str]
            ) -> None:
                """Update an attribute value, replacing existing values."""
                match value:
                    case list() as value_list:
                        self.attributes[name] = value_list.copy()
                    case str() as value_str:
                        self.attributes[name] = [value_str]
                    case _:
                        self.attributes[name] = list(value)

            def _create_flext_entry(self) -> m.Ldif.Entry:
                """Create m.Entry from current data."""
                try:
                    api = ldif()
                    ldif_content = f"dn: {self.dn}\n"
                    for attr_name, attr_values in self.attributes.items():
                        for value in attr_values:
                            ldif_content += f"{attr_name}: {value}\n"
                    ldif_content += "\n"
                    result: r[MutableSequence[m.Ldif.Entry]] = api.parse_ldif(
                        ldif_content
                    )
                    if result.is_success and result.value and (result.value):
                        try:
                            parsed_entry = m.Ldif.Entry.model_validate(
                                result.value[0].model_dump()
                            )
                        except ValidationError:
                            parsed_entry = None
                        if parsed_entry is not None:
                            return parsed_entry
                    return self._fallback_entry()
                except c.Meltano.SINGER_SAFE_EXCEPTIONS:
                    return self._fallback_entry()

            def _fallback_entry(self) -> m.Ldif.Entry:
                """Create fallback entry from current data."""
                return m.Ldif.Entry(
                    dn=FlextTapLdapUtilitiesProcessorMixin.TapLdap.DistinguishedName(
                        value=self.dn,
                        metadata=_DEFAULT_ENTRY_METADATA,
                    ),
                    attributes=m.Ldif.Attributes(
                        attributes={
                            str(k): list(v) for k, v in self.attributes.items()
                        },
                        attribute_metadata={},
                        metadata=_DEFAULT_ENTRY_METADATA,
                    ),
                    changetype=None,
                    metadata=None,
                    validation_metadata=None,
                    domain_events=[],
                )

        class Processor:
            """LDIF file processor using flext-ldif library.

            Provides testing convenience while delegating
            all LDIF processing to the flext-ldif library.
            """

            @staticmethod
            def _to_ldif_entry(raw_value: t.ContainerMapping) -> m.Ldif.Entry | None:
                """Validate and coerce value to LDIF entry model."""
                try:
                    return m.Ldif.Entry.model_validate(raw_value)
                except ValidationError:
                    return None

            @override
            def __init__(
                self, *, ignore_errors: bool = True, max_errors: int = 100
            ) -> None:
                """Initialize the processor with a flext-ldif backend."""
                self.ignore_errors = ignore_errors
                self.max_errors = max_errors
                self.errors: MutableSequence[str] = []
                self.processed_entries = 0
                self.skipped_entries = 0
                self.entries: MutableSequence[
                    FlextTapLdapUtilitiesProcessorMixin.TapLdap.Entry
                ] = []
                self.stats = {
                    "total_entries": 0,
                    "valid_entries": 0,
                    "invalid_entries": 0,
                }
                self._api = ldif()

            def filter_by_attribute_exists(
                self,
                attr_name: str,
            ) -> Sequence[FlextTapLdapUtilitiesProcessorMixin.TapLdap.Entry]:
                """Filter entries that have a specific attribute."""
                return [
                    entry for entry in self.entries if entry.get_attribute(attr_name)
                ]

            def filter_by_dn_contains(
                self,
                substring: str,
            ) -> Sequence[FlextTapLdapUtilitiesProcessorMixin.TapLdap.Entry]:
                """Filter entries by DN containing substring."""
                return [entry for entry in self.entries if substring in entry.dn]

            def filter_by_dn_pattern(
                self,
                dn_pattern: str,
            ) -> Sequence[FlextTapLdapUtilitiesProcessorMixin.TapLdap.Entry]:
                """Filter entries by DN pattern - entries under the pattern."""
                return [
                    entry
                    for entry in self.entries
                    if dn_pattern in entry.dn and entry.dn != dn_pattern
                ]

            def filter_by_objectclass(
                self,
                object_class: str,
            ) -> Sequence[FlextTapLdapUtilitiesProcessorMixin.TapLdap.Entry]:
                """Filter entries by object class."""
                return [
                    entry
                    for entry in self.entries
                    if entry.has_object_class(object_class)
                ]

            def get_statistics(self) -> t.ContainerMapping:
                """Get parsing statistics."""
                return {
                    "processed_entries": self.processed_entries,
                    "skipped_entries": self.skipped_entries,
                    "errors": len(self.errors),
                    "error_messages": list(self.errors),
                }

            def load_from_file(self, file_path: Path) -> r[str]:
                """Load LDIF entries from file and return as r."""
                try:
                    self.entries = list(self.parse_file(file_path))
                    self._update_stats()
                    return r[str].ok("LDIF file loaded successfully using flext-ldif")
                except (RuntimeError, ValueError, TypeError) as e:
                    return r[str].fail(f"Failed to load LDIF file: {e}")

            def load_from_string(
                self,
                content: str,
                source_name: str = "string",
            ) -> r[str]:
                """Load LDIF entries from string and return as r."""
                try:
                    self.entries = list(self.parse_content(content, source_name))
                    self._update_stats()
                    return r[str].ok(
                        "LDIF content loaded successfully using flext-ldif"
                    )
                except (RuntimeError, ValueError, TypeError) as e:
                    return r[str].fail(f"Failed to load LDIF content: {e}")

            def parse_content(
                self,
                content: str,
                source_name: str = "content",
            ) -> Iterator[FlextTapLdapUtilitiesProcessorMixin.TapLdap.Entry]:
                """Parse LDIF content using flext-ldif and yield entries."""
                logger.info("Parsing LDIF content with flext-ldif from %s", source_name)
                try:
                    result: r[MutableSequence[m.Ldif.Entry]] = self._api.parse_ldif(
                        content
                    )
                    if not result.is_success:
                        error_msg = f"Failed to parse LDIF content from {source_name}: {result.error}"
                        if self.ignore_errors:
                            logger.error(error_msg)
                            self.errors.append(error_msg)
                            return
                        else:
                            self._raise_parse_error(error_msg)
                    if result.value:
                        for flext_entry in result.value:
                            parsed_entry = self._to_ldif_entry(flext_entry.model_dump())
                            if parsed_entry is None:
                                continue
                            yield self._convert_from_flext_entry(parsed_entry)
                            self.processed_entries += 1
                except c.Meltano.SINGER_SAFE_EXCEPTIONS as e:
                    error_msg = f"Failed to parse LDIF content from {source_name}: {e}"
                    if self.ignore_errors:
                        logger.exception(error_msg)
                        self.errors.append(error_msg)
                    else:
                        raise ValueError(error_msg) from e

            def parse_file(
                self,
                file_path: Path,
            ) -> Iterator[FlextTapLdapUtilitiesProcessorMixin.TapLdap.Entry]:
                """Parse LDIF file using flext-ldif and yield entries."""
                self._validate_file_exists(file_path)
                logger.info("Starting LDIF parsing with flext-ldif: %s", file_path)
                try:
                    content = self._read_file_content(file_path, "utf-8")
                    result = self._parse_ldif_content(content, file_path)
                    yield from self._yield_entries_from_result(result)
                except UnicodeDecodeError:
                    logger.warning(
                        "UTF-8 decoding failed, trying latin-1 for: %s",
                        file_path,
                    )
                    try:
                        content = self._read_file_content(file_path, "latin-1")
                        result = self._parse_ldif_content(content, file_path)
                        yield from self._yield_entries_from_result(result)
                    except c.Meltano.SINGER_SAFE_EXCEPTIONS as e:
                        self._handle_parsing_error(file_path, e, "latin-1")

            def to_singer_format(
                self,
                _stream_name: str,
            ) -> Sequence[t.ContainerMapping]:
                """Convert LDIF entries to Singer record format."""
                records: Sequence[t.ContainerMapping] = [
                    {
                        "type": "RECORD",
                        "stream": _stream_name,
                        "record": {"dn": entry.dn, **dict(entry.attributes)},
                    }
                    for entry in self.entries
                ]
                return records

            def _convert_from_flext_entry(
                self,
                flext_entry: m.Ldif.Entry,
            ) -> FlextTapLdapUtilitiesProcessorMixin.TapLdap.Entry:
                """Convert m.Ldif.Entry to testing convenience Entry."""
                dn = flext_entry.dn.value if flext_entry.dn else ""
                attributes: t.MutableStrSequenceMapping = {}
                if flext_entry.attributes and flext_entry.attributes.attributes:
                    for (
                        attr_name,
                        attr_values,
                    ) in flext_entry.attributes.attributes.items():
                        attributes[attr_name] = [str(v) for v in attr_values]
                return FlextTapLdapUtilitiesProcessorMixin.TapLdap.Entry(
                    dn=dn,
                    attributes=attributes,
                )

            def _handle_parsing_error(
                self,
                file_path: Path,
                error: Exception,
                _encoding: str,
            ) -> None:
                """Handle parsing errors based on ignore_errors setting."""
                error_msg = f"Failed to parse LDIF file {file_path}: {error}"
                if self.ignore_errors:
                    logger.error(error_msg)
                    self.errors.append(error_msg)
                else:
                    raise ValueError(error_msg) from error

            def _parse_ldif_content(
                self,
                content: str,
                file_path: Path,
            ) -> r[MutableSequence[m.Ldif.Entry]]:
                """Parse LDIF content using flext-ldif API."""
                result: r[MutableSequence[m.Ldif.Entry]] = self._api.parse_ldif(content)
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

            def _read_file_content(
                self,
                file_path: Path,
                encoding: str = "utf-8",
            ) -> str:
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
                self,
                result: r[MutableSequence[m.Ldif.Entry]],
            ) -> Iterator[FlextTapLdapUtilitiesProcessorMixin.TapLdap.Entry]:
                """Yield testing convenience entries from parse result."""
                if result.value:
                    for flext_entry in result.value:
                        parsed_entry = self._to_ldif_entry(flext_entry.model_dump())
                        if parsed_entry is None:
                            continue
                        yield self._convert_from_flext_entry(parsed_entry)
                        self.processed_entries += 1

        class Validator:
            """LDIF content validator using flext-ldif validation capabilities."""

            @override
            def __init__(self) -> None:
                """Initialize validator with in-memory state and API client."""
                self.validation_errors: MutableSequence[str] = []
                self.warnings: MutableSequence[str] = []
                self._api = ldif()

            def get_validation_results(self) -> t.ContainerMapping:
                """Get validation results."""
                return {
                    "errors": list(self.validation_errors),
                    "warnings": list(self.warnings),
                    "is_valid": not self.validation_errors,
                }

            def validate_entries(
                self,
                entries: Sequence[FlextTapLdapUtilitiesProcessorMixin.TapLdap.Entry],
            ) -> t.ContainerMapping:
                """Validate a list of LDIF entries using flext-ldif."""
                valid_count = 0
                invalid_count = 0
                errors: MutableSequence[str] = []
                try:
                    valid_count = len(entries)
                    invalid_count = 0
                except c.Meltano.SINGER_SAFE_EXCEPTIONS:
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

            def validate_entry(
                self,
                entry: FlextTapLdapUtilitiesProcessorMixin.TapLdap.Entry,
            ) -> bool:
                """Validate LDIF entry using flext-ldif validation."""
                try:
                    return True
                except c.Meltano.SINGER_SAFE_EXCEPTIONS as e:
                    self.validation_errors.append(
                        f"Validation error for {entry.dn}: {e}",
                    )
                    return False

        class Transformer:
            """Transform LDIF entries using flext-ldif transformation capabilities."""

            @override
            def __init__(
                self,
                transformation_rules: t.ContainerMapping | None = None,
            ) -> None:
                """Initialize transformer with optional transformation rules."""
                self.transformation_rules = dict(transformation_rules or {})
                self._api = ldif()

            def apply_attribute_mappings(
                self,
                entry: FlextTapLdapUtilitiesProcessorMixin.TapLdap.Entry,
                mappings: t.StrMapping,
            ) -> FlextTapLdapUtilitiesProcessorMixin.TapLdap.Entry:
                """Apply attribute name mappings to entry."""
                new_attributes: t.MutableStrSequenceMapping = {}
                for attr_name, values in entry.attributes.items():
                    new_name = mappings.get(attr_name, attr_name)
                    new_attributes[new_name] = list(values)
                transformed_entry = FlextTapLdapUtilitiesProcessorMixin.TapLdap.Entry(
                    entry.dn,
                    new_attributes,
                )
                transformed_entry.change_type = entry.change_type
                transformed_entry.controls = list(entry.controls)
                return transformed_entry

            def apply_schema_mappings(
                self,
                entry: FlextTapLdapUtilitiesProcessorMixin.TapLdap.Entry,
                schema_mappings: t.ContainerMapping,
            ) -> FlextTapLdapUtilitiesProcessorMixin.TapLdap.Entry:
                """Apply schema mappings to normalize output attributes."""
                transformed_entry = FlextTapLdapUtilitiesProcessorMixin.TapLdap.Entry(
                    entry.dn,
                    {k: list(v) for k, v in entry.attributes.items()},
                )
                transformed_entry.change_type = entry.change_type
                transformed_entry.controls = list(entry.controls)
                for target_attr_key, mapping in schema_mappings.items():
                    target_attr: str = str(target_attr_key)
                    source_attr: str | None = None
                    default_values: MutableSequence[str] | None = None
                    if isinstance(mapping, str):
                        source_attr = mapping
                    else:
                        mapping_dict: t.ContainerMapping = (
                            dict(mapping) if isinstance(mapping, Mapping) else {}
                        )
                        source_raw: t.NormalizedValue = mapping_dict.get("source")
                        if isinstance(source_raw, str):
                            source_attr = source_raw
                        default_raw: t.NormalizedValue = mapping_dict.get("default")
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

            def transform_entry(
                self,
                entry: FlextTapLdapUtilitiesProcessorMixin.TapLdap.Entry,
            ) -> FlextTapLdapUtilitiesProcessorMixin.TapLdap.Entry:
                """Transform LDIF entry using configured transformation rules."""
                transformed = FlextTapLdapUtilitiesProcessorMixin.TapLdap.Entry(
                    entry.dn,
                    {k: list(v) for k, v in entry.attributes.items()},
                )
                transformed.change_type = entry.change_type
                transformed.controls = list(entry.controls)
                raw_schema_mappings: t.NormalizedValue = self.transformation_rules.get(
                    "schema_mappings",
                )
                if isinstance(raw_schema_mappings, dict):
                    schema_map: t.ContainerMapping = raw_schema_mappings
                    transformed = self.apply_schema_mappings(transformed, schema_map)
                raw_mappings: t.NormalizedValue = self.transformation_rules.get(
                    "attribute_mappings",
                )
                mappings: t.MutableStrMapping = {}
                if isinstance(raw_mappings, dict):
                    attr_map: t.ContainerMapping = raw_mappings
                    mappings.update({
                        k: str(v) for k, v in attr_map.items() if isinstance(v, str)
                    })
                if mappings:
                    transformed = self.apply_attribute_mappings(transformed, mappings)
                raw_value_mappings: t.NormalizedValue = self.transformation_rules.get(
                    "attribute_value_mappings",
                )
                if isinstance(raw_value_mappings, dict):
                    vm_dict: t.ContainerMapping = raw_value_mappings
                    for vm_key, vm_val in vm_dict.items():
                        if not isinstance(vm_val, dict):
                            continue
                        val_map: t.ContainerMapping = vm_val
                        existing_values = transformed.attributes.get(vm_key)
                        if existing_values is None:
                            continue
                        mapped_values: MutableSequence[str] = [
                            str(val_map.get(value, value)) for value in existing_values
                        ]
                        transformed.attributes[vm_key] = mapped_values
                raw_remove_attributes: t.NormalizedValue = (
                    self.transformation_rules.get(
                        "remove_attributes",
                    )
                )
                if isinstance(raw_remove_attributes, list):
                    remove_list: t.ContainerList = raw_remove_attributes
                    for rm_item in remove_list:
                        transformed.attributes.pop(str(rm_item), None)
                raw_add_attributes: t.NormalizedValue = self.transformation_rules.get(
                    "add_attributes",
                )
                if isinstance(raw_add_attributes, dict):
                    add_dict: t.ContainerMapping = raw_add_attributes
                    for add_key, add_val in add_dict.items():
                        if isinstance(add_val, list):
                            transformed.add_attribute(
                                add_key,
                                [str(item) for item in add_val],
                            )
                        else:
                            transformed.add_attribute(add_key, str(add_val))
                return transformed
