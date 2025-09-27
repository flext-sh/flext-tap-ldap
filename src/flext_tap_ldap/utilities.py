"""Singer tap utilities for LDAP domain operations.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Any, ClassVar, override

from flext_core import FlextResult, FlextUtilities


class FlextTapLdapUtilities(FlextUtilities):
    """Single unified utilities class for Singer tap LDAP operations.

    Follows FLEXT unified class pattern with nested helper classes for
    domain-specific Singer tap functionality with LDAP data sources.
    Extends FlextUtilities with LDAP tap-specific operations.
    """

    # Configuration constants
    DEFAULT_BATCH_SIZE: ClassVar[int] = 1000
    DEFAULT_TIMEOUT: ClassVar[int] = 30
    MAX_RETRIES: ClassVar[int] = 3

    @override
    def __init__(self) -> None:
        """Initialize LDAP tap utilities."""
        super().__init__()

    class SingerUtilities:
        """Singer protocol utilities for tap operations."""

        @staticmethod
        def create_schema_message(
            stream_name: str,
            schema: dict[str, Any],
            key_properties: list[str] | None = None,
        ) -> dict[str, Any]:
            """Create Singer schema message.

            Args:
                stream_name: Name of the stream
                schema: JSON schema for the stream
                key_properties: List of key property names

            Returns:
                dict[str, Any]: Singer schema message

            """
            return {
                "type": "SCHEMA",
                "stream": stream_name,
                "schema": schema,
                "key_properties": key_properties or [],
            }

        @staticmethod
        def create_record_message(
            stream_name: str,
            record: dict[str, Any],
            time_extracted: datetime | None = None,
        ) -> dict[str, Any]:
            """Create Singer record message.

            Args:
                stream_name: Name of the stream
                record: Record data
                time_extracted: Timestamp when record was extracted

            Returns:
                dict[str, Any]: Singer record message

            """
            extracted_time = time_extracted or datetime.now(UTC)
            return {
                "type": "RECORD",
                "stream": stream_name,
                "record": record,
                "time_extracted": extracted_time.isoformat(),
            }

        @staticmethod
        def create_state_message(state: dict[str, Any]) -> dict[str, Any]:
            """Create Singer state message.

            Args:
                state: State data

            Returns:
                dict[str, Any]: Singer state message

            """
            return {
                "type": "STATE",
                "value": state,
            }

        @staticmethod
        def write_message(message: dict[str, Any]) -> None:
            """Write Singer message to stdout.

            Args:
                message: Singer message to write

            """

    class LdapDataProcessing:
        """LDAP-specific data processing utilities."""

        @staticmethod
        def normalize_dn(dn: str) -> str:
            """Normalize LDAP Distinguished Name.

            Args:
                dn: Distinguished Name to normalize

            Returns:
                str: Normalized DN

            """
            if not dn:
                return ""

            # Remove extra whitespace and normalize case
            return re.sub(r"\s+", " ", dn.strip())

        @staticmethod
        def extract_cn_from_dn(dn: str) -> str:
            """Extract Common Name from Distinguished Name.

            Args:
                dn: Distinguished Name

            Returns:
                str: Common Name or empty string if not found

            """
            if not dn:
                return ""

            match = re.search(r"cn=([^,]+)", dn.lower())
            return match.group(1).strip() if match else ""

        @staticmethod
        def extract_ou_from_dn(dn: str) -> list[str]:
            """Extract Organizational Units from Distinguished Name.

            Args:
                dn: Distinguished Name

            Returns:
                list[str]: List of organizational units

            """
            if not dn:
                return []

            return re.findall(r"ou=([^,]+)", dn.lower())

        @staticmethod
        def convert_ldap_timestamp(timestamp: str) -> FlextResult[str]:
            """Convert LDAP timestamp to ISO format.

            Args:
                timestamp: LDAP timestamp string

            Returns:
                FlextResult[str]: ISO formatted timestamp or error

            """
            try:
                # Handle LDAP generalized time format (YYYYMMDDHHMMSSZ)
                if len(timestamp) == 15 and timestamp.endswith("Z"):
                    dt = datetime.strptime(timestamp, "%Y%m%d%H%M%SZ")
                    dt = dt.replace(tzinfo=UTC)
                    return FlextResult[str].ok(dt.isoformat())

                # Handle other common formats
                for fmt in ["%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S"]:
                    try:
                        dt = datetime.strptime(timestamp, fmt)
                        dt = dt.replace(tzinfo=UTC)
                        return FlextResult[str].ok(dt.isoformat())
                    except ValueError:
                        continue

                return FlextResult[str].fail(
                    f"Unsupported timestamp format: {timestamp}"
                )

            except Exception as e:
                return FlextResult[str].fail(f"Error converting timestamp: {e}")

        @staticmethod
        def sanitize_attribute_name(attr_name: str) -> str:
            """Sanitize LDAP attribute name for JSON schema.

            Args:
                attr_name: LDAP attribute name

            Returns:
                str: Sanitized attribute name

            """
            if not attr_name:
                return ""

            # Convert to lowercase and replace non-alphanumeric with underscores
            sanitized = re.sub(r"[^a-zA-Z0-9]", "_", attr_name.lower())

            # Ensure it doesn't start with a number
            if sanitized and sanitized[0].isdigit():
                sanitized = f"attr_{sanitized}"

            return sanitized

    class StreamUtilities:
        """Stream processing utilities for Singer taps."""

        @staticmethod
        def generate_stream_schema(
            sample_records: list[dict[str, Any]],
            stream_name: str,
        ) -> dict[str, Any]:
            """Generate JSON schema from sample records.

            Args:
                sample_records: List of sample records
                stream_name: Name of the stream

            Returns:
                dict[str, Any]: JSON schema

            """
            if not sample_records:
                return {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": True,
                }

            properties: dict[str, Any] = {}

            for record in sample_records:
                for key, value in record.items():
                    if key not in properties:
                        properties[key] = (
                            FlextTapLdapUtilities.StreamUtilities._infer_type(value)
                        )

            return {
                "type": "object",
                "properties": properties,
                "additionalProperties": True,
            }

        @staticmethod
        def _infer_type(value: Any) -> dict[str, Any]:
            """Infer JSON schema type from value.

            Args:
                value: Value to analyze

            Returns:
                dict[str, Any]: JSON schema type definition

            """
            if value is None:
                return {"type": ["null", "string"]}
            if isinstance(value, bool):
                return {"type": "boolean"}
            if isinstance(value, int):
                return {"type": "integer"}
            if isinstance(value, float):
                return {"type": "number"}
            if isinstance(value, list):
                if value:
                    # Infer type from first element
                    item_type = FlextTapLdapUtilities.StreamUtilities._infer_type(
                        value[0]
                    )
                    return {"type": "array", "items": item_type}
                return {"type": "array", "items": {"type": "string"}}
            if isinstance(value, dict):
                return {"type": "object", "additionalProperties": True}
            return {"type": "string"}

        @staticmethod
        def calculate_batch_size(record_count: int, target_batches: int = 10) -> int:
            """Calculate optimal batch size for processing.

            Args:
                record_count: Total number of records
                target_batches: Target number of batches

            Returns:
                int: Optimal batch size

            """
            if record_count <= 0:
                return FlextTapLdapUtilities.DEFAULT_BATCH_SIZE

            calculated_size = max(1, record_count // target_batches)
            return min(calculated_size, FlextTapLdapUtilities.DEFAULT_BATCH_SIZE)

    class ConfigValidation:
        """Configuration validation utilities."""

        @staticmethod
        def validate_ldap_connection_config(
            config: dict[str, Any],
        ) -> FlextResult[dict[str, Any]]:
            """Validate LDAP connection configuration.

            Args:
                config: Configuration dictionary

            Returns:
                FlextResult[dict[str, Any]]: Validated config or error

            """
            required_fields = ["host", "base_dn"]
            missing_fields = [field for field in required_fields if field not in config]

            if missing_fields:
                return FlextResult[dict[str, Any]].fail(
                    f"Missing required fields: {', '.join(missing_fields)}"
                )

            # Validate host format
            host = config["host"]
            if not isinstance(host, str) or not host.strip():
                return FlextResult[dict[str, Any]].fail(
                    "Host must be a non-empty string"
                )

            # Validate base DN format
            base_dn = config["base_dn"]
            if not isinstance(base_dn, str) or not base_dn.strip():
                return FlextResult[dict[str, Any]].fail(
                    "Base DN must be a non-empty string"
                )

            # Validate port if provided
            if "port" in config:
                port = config["port"]
                if not isinstance(port, int) or port <= 0 or port > 65535:
                    return FlextResult[dict[str, Any]].fail(
                        "Port must be a valid integer between 1 and 65535"
                    )

            return FlextResult[dict[str, Any]].ok(config)

        @staticmethod
        def validate_stream_config(
            config: dict[str, Any],
        ) -> FlextResult[dict[str, Any]]:
            """Validate stream configuration.

            Args:
                config: Stream configuration

            Returns:
                FlextResult[dict[str, Any]]: Validated config or error

            """
            if "streams" not in config:
                return FlextResult[dict[str, Any]].fail(
                    "Configuration must include 'streams' section"
                )

            streams = config["streams"]
            if not isinstance(streams, dict):
                return FlextResult[dict[str, Any]].fail(
                    "Streams configuration must be a dictionary"
                )

            # Validate each stream
            for stream_name, stream_config in streams.items():
                if not isinstance(stream_config, dict):
                    return FlextResult[dict[str, Any]].fail(
                        f"Stream '{stream_name}' configuration must be a dictionary"
                    )

                # Check for required stream fields
                if "selected" not in stream_config:
                    return FlextResult[dict[str, Any]].fail(
                        f"Stream '{stream_name}' must have 'selected' field"
                    )

            return FlextResult[dict[str, Any]].ok(config)

    class StateManagement:
        """State management utilities for incremental syncs."""

        @staticmethod
        def get_stream_state(state: dict[str, Any], stream_name: str) -> dict[str, Any]:
            """Get state for a specific stream.

            Args:
                state: Complete state dictionary
                stream_name: Name of the stream

            Returns:
                dict[str, Any]: Stream state

            """
            return state.get("bookmarks", {}).get(stream_name, {})

        @staticmethod
        def set_stream_state(
            state: dict[str, Any],
            stream_name: str,
            stream_state: dict[str, Any],
        ) -> dict[str, Any]:
            """Set state for a specific stream.

            Args:
                state: Complete state dictionary
                stream_name: Name of the stream
                stream_state: State data for the stream

            Returns:
                dict[str, Any]: Updated state

            """
            if "bookmarks" not in state:
                state["bookmarks"] = {}

            state["bookmarks"][stream_name] = stream_state
            return state

        @staticmethod
        def get_bookmark(
            state: dict[str, Any],
            stream_name: str,
            bookmark_key: str,
        ) -> Any:
            """Get bookmark value for a stream.

            Args:
                state: Complete state dictionary
                stream_name: Name of the stream
                bookmark_key: Bookmark key

            Returns:
                Any: Bookmark value or None

            """
            stream_state = FlextTapLdapUtilities.StateManagement.get_stream_state(
                state, stream_name
            )
            return stream_state.get(bookmark_key)

        @staticmethod
        def set_bookmark(
            state: dict[str, Any],
            stream_name: str,
            bookmark_key: str,
            bookmark_value: Any,
        ) -> dict[str, Any]:
            """Set bookmark value for a stream.

            Args:
                state: Complete state dictionary
                stream_name: Name of the stream
                bookmark_key: Bookmark key
                bookmark_value: Bookmark value

            Returns:
                dict[str, Any]: Updated state

            """
            if "bookmarks" not in state:
                state["bookmarks"] = {}
            if stream_name not in state["bookmarks"]:
                state["bookmarks"][stream_name] = {}

            state["bookmarks"][stream_name][bookmark_key] = bookmark_value
            return state

    # Proxy methods for backward compatibility
    @classmethod
    def create_schema_message(
        cls,
        stream_name: str,
        schema: dict[str, Any],
        key_properties: list[str] | None = None,
    ) -> dict[str, Any]:
        """Proxy method for SingerUtilities.create_schema_message()."""
        return cls.SingerUtilities.create_schema_message(
            stream_name, schema, key_properties
        )

    @classmethod
    def create_record_message(
        cls,
        stream_name: str,
        record: dict[str, Any],
        time_extracted: datetime | None = None,
    ) -> dict[str, Any]:
        """Proxy method for SingerUtilities.create_record_message()."""
        return cls.SingerUtilities.create_record_message(
            stream_name, record, time_extracted
        )

    @classmethod
    def normalize_dn(cls, dn: str) -> str:
        """Proxy method for LdapDataProcessing.normalize_dn()."""
        return cls.LdapDataProcessing.normalize_dn(dn)

    @classmethod
    def extract_cn_from_dn(cls, dn: str) -> str:
        """Proxy method for LdapDataProcessing.extract_cn_from_dn()."""
        return cls.LdapDataProcessing.extract_cn_from_dn(dn)

    @classmethod
    def convert_ldap_timestamp(cls, timestamp: str) -> FlextResult[str]:
        """Proxy method for LdapDataProcessing.convert_ldap_timestamp()."""
        return cls.LdapDataProcessing.convert_ldap_timestamp(timestamp)

    @classmethod
    def validate_ldap_connection_config(
        cls, config: dict[str, Any]
    ) -> FlextResult[dict[str, Any]]:
        """Proxy method for ConfigValidation.validate_ldap_connection_config()."""
        return cls.ConfigValidation.validate_ldap_connection_config(config)

    @classmethod
    def get_stream_state(
        cls, state: dict[str, Any], stream_name: str
    ) -> dict[str, Any]:
        """Proxy method for StateManagement.get_stream_state()."""
        return cls.StateManagement.get_stream_state(state, stream_name)

    @classmethod
    def set_bookmark(
        cls,
        state: dict[str, Any],
        stream_name: str,
        bookmark_key: str,
        bookmark_value: Any,
    ) -> dict[str, Any]:
        """Proxy method for StateManagement.set_bookmark()."""
        return cls.StateManagement.set_bookmark(
            state, stream_name, bookmark_key, bookmark_value
        )


__all__ = [
    "FlextTapLdapUtilities",
]
