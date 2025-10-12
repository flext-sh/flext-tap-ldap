"""Singer tap utilities for LDAP domain operations.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import ClassVar, override

from flext_core import FlextCore


class FlextMeltanoTapLdapUtilities(FlextCore.Utilities):
    """Single unified utilities class for Singer tap LDAP operations.

    Follows FLEXT unified class pattern with nested helper classes for
    domain-specific Singer tap functionality with LDAP data sources.
    Extends FlextCore.Utilities with LDAP tap-specific operations.
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
            schema: FlextCore.Types.Dict,
            key_properties: FlextCore.Types.StringList | None = None,
        ) -> FlextCore.Types.Dict:
            """Create Singer schema message.

            Args:
                stream_name: Name of the stream
                schema: JSON schema for the stream
                key_properties: List of key property names

            Returns:
                FlextCore.Types.Dict: Singer schema message

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
            record: FlextCore.Types.Dict,
            time_extracted: datetime | None = None,
        ) -> FlextCore.Types.Dict:
            """Create Singer record message.

            Args:
                stream_name: Name of the stream
                record: Record data
                time_extracted: Timestamp when record was extracted

            Returns:
                FlextCore.Types.Dict: Singer record message

            """
            extracted_time = time_extracted or datetime.now(UTC)
            return {
                "type": "RECORD",
                "stream": stream_name,
                "record": record,
                "time_extracted": extracted_time.isoformat(),
            }

        @staticmethod
        def create_state_message(state: FlextCore.Types.Dict) -> FlextCore.Types.Dict:
            """Create Singer state message.

            Args:
                state: State data

            Returns:
                FlextCore.Types.Dict: Singer state message

            """
            return {
                "type": "STATE",
                "value": state,
            }

        @staticmethod
        def write_message(message: FlextCore.Types.Dict) -> None:
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
        def extract_ou_from_dn(dn: str) -> FlextCore.Types.StringList:
            """Extract Organizational Units from Distinguished Name.

            Args:
                dn: Distinguished Name

            Returns:
                FlextCore.Types.StringList: List of organizational units

            """
            if not dn:
                return []

            return re.findall(r"ou=([^,]+)", dn.lower())

        @staticmethod
        def convert_ldap_timestamp(timestamp: str) -> FlextCore.Result[str]:
            """Convert LDAP timestamp to ISO format.

            Args:
                timestamp: LDAP timestamp string

            Returns:
                FlextCore.Result[str]: ISO formatted timestamp or error

            """
            try:
                # Handle LDAP generalized time format (YYYYMMDDHHMMSSZ)
                ldap_generalized_time_length = 15
                if len(
                    timestamp
                ) == ldap_generalized_time_length and timestamp.endswith("Z"):
                    dt = datetime.strptime(timestamp[:-1], "%Y%m%d%H%M%S").replace(
                        tzinfo=UTC
                    )
                    return FlextCore.Result[str].ok(dt.isoformat())

                # Handle other common formats
                for fmt in ["%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S"]:
                    try:
                        dt = datetime.strptime(timestamp, fmt).replace(tzinfo=UTC)
                        return FlextCore.Result[str].ok(dt.isoformat())
                    except ValueError:
                        continue

                return FlextCore.Result[str].fail(
                    f"Unsupported timestamp format: {timestamp}"
                )

            except Exception as e:
                return FlextCore.Result[str].fail(f"Error converting timestamp: {e}")

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
            sample_records: list[FlextCore.Types.Dict],
            _stream_name: str,
        ) -> FlextCore.Types.Dict:
            """Generate JSON schema from sample records.

            Args:
                sample_records: List of sample records
                stream_name: Name of the stream

            Returns:
                FlextCore.Types.Dict: JSON schema

            """
            if not sample_records:
                return {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": True,
                }

            properties: FlextCore.Types.Dict = {}

            for record in sample_records:
                for key, value in record.items():
                    if key not in properties:
                        properties[key] = (
                            FlextMeltanoTapLdapUtilities.StreamUtilities.infer_type(
                                value
                            )
                        )

            return {
                "type": "object",
                "properties": properties,
                "additionalProperties": True,
            }

        @staticmethod
        def infer_type(value: object) -> FlextCore.Types.Dict:
            """Infer JSON schema type from value.

            Args:
                value: Value to analyze

            Returns:
                FlextCore.Types.Dict: JSON schema type definition

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
                    item_type = FlextMeltanoTapLdapUtilities.StreamUtilities.infer_type(
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
                return FlextMeltanoTapLdapUtilities.DEFAULT_BATCH_SIZE

            calculated_size = max(1, record_count // target_batches)
            return min(calculated_size, FlextMeltanoTapLdapUtilities.DEFAULT_BATCH_SIZE)

    class ConfigValidation:
        """Configuration validation utilities."""

        @staticmethod
        def validate_ldap_connection_config(
            config: FlextCore.Types.Dict,
        ) -> FlextCore.Result[FlextCore.Types.Dict]:
            """Validate LDAP connection configuration.

            Args:
                config: Configuration dictionary

            Returns:
                FlextCore.Result[FlextCore.Types.Dict]: Validated config or error

            """
            required_fields = ["host", "base_dn"]
            missing_fields = [field for field in required_fields if field not in config]

            if missing_fields:
                return FlextCore.Result[FlextCore.Types.Dict].fail(
                    f"Missing required fields: {', '.join(missing_fields)}"
                )

            # Validate host format
            host = config["host"]
            if not isinstance(host, str) or not host.strip():
                return FlextCore.Result[FlextCore.Types.Dict].fail(
                    "Host must be a non-empty string"
                )

            # Validate base DN format
            base_dn = config["base_dn"]
            if not isinstance(base_dn, str) or not base_dn.strip():
                return FlextCore.Result[FlextCore.Types.Dict].fail(
                    "Base DN must be a non-empty string"
                )

            # Validate port if provided
            if "port" in config:
                port = config["port"]
                if (
                    not isinstance(port, int)
                    or port <= 0
                    or port > FlextCore.Constants.Network.MAX_PORT
                ):
                    return FlextCore.Result[FlextCore.Types.Dict].fail(
                        "Port must be a valid integer between 1 and 65535"
                    )

            return FlextCore.Result[FlextCore.Types.Dict].ok(config)

        @staticmethod
        def validate_stream_config(
            config: FlextCore.Types.Dict,
        ) -> FlextCore.Result[FlextCore.Types.Dict]:
            """Validate stream configuration.

            Args:
                config: Stream configuration

            Returns:
                FlextCore.Result[FlextCore.Types.Dict]: Validated config or error

            """
            if "streams" not in config:
                return FlextCore.Result[FlextCore.Types.Dict].fail(
                    "Configuration must include 'streams' section"
                )

            streams = config["streams"]
            if not isinstance(streams, dict):
                return FlextCore.Result[FlextCore.Types.Dict].fail(
                    "Streams configuration must be a dictionary"
                )

            # Validate each stream
            for stream_name, stream_config in streams.items():
                if not isinstance(stream_config, dict):
                    return FlextCore.Result[FlextCore.Types.Dict].fail(
                        f"Stream '{stream_name}' configuration must be a dictionary"
                    )

                # Check for required stream fields
                if "selected" not in stream_config:
                    return FlextCore.Result[FlextCore.Types.Dict].fail(
                        f"Stream '{stream_name}' must have 'selected' field"
                    )

            return FlextCore.Result[FlextCore.Types.Dict].ok(config)

    class StateManagement:
        """State management utilities for incremental syncs."""

        @staticmethod
        def get_stream_state(
            state: FlextCore.Types.Dict, stream_name: str
        ) -> FlextCore.Types.Dict:
            """Get state for a specific stream.

            Args:
                state: Complete state dictionary
                stream_name: Name of the stream

            Returns:
                FlextCore.Types.Dict: Stream state

            """
            return state.get("bookmarks", {}).get(stream_name, {})

        @staticmethod
        def set_stream_state(
            state: FlextCore.Types.Dict,
            stream_name: str,
            stream_state: FlextCore.Types.Dict,
        ) -> FlextCore.Types.Dict:
            """Set state for a specific stream.

            Args:
                state: Complete state dictionary
                stream_name: Name of the stream
                stream_state: State data for the stream

            Returns:
                FlextCore.Types.Dict: Updated state

            """
            if "bookmarks" not in state:
                state["bookmarks"] = {}

            state["bookmarks"][stream_name] = stream_state
            return state

        @staticmethod
        def get_bookmark(
            state: FlextCore.Types.Dict,
            stream_name: str,
            bookmark_key: str,
        ) -> object:
            """Get bookmark value for a stream.

            Args:
                state: Complete state dictionary
                stream_name: Name of the stream
                bookmark_key: Bookmark key

            Returns:
                object: Bookmark value or None

            """
            stream_state = (
                FlextMeltanoTapLdapUtilities.StateManagement.get_stream_state(
                    state, stream_name
                )
            )
            return stream_state.get(bookmark_key)

        @staticmethod
        def set_bookmark(
            state: FlextCore.Types.Dict,
            stream_name: str,
            bookmark_key: str,
            bookmark_value: object,
        ) -> FlextCore.Types.Dict:
            """Set bookmark value for a stream.

            Args:
                state: Complete state dictionary
                stream_name: Name of the stream
                bookmark_key: Bookmark key
                bookmark_value: Bookmark value

            Returns:
                FlextCore.Types.Dict: Updated state

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
        schema: FlextCore.Types.Dict,
        key_properties: FlextCore.Types.StringList | None = None,
    ) -> FlextCore.Types.Dict:
        """Proxy method for SingerUtilities.create_schema_message()."""
        return cls.SingerUtilities.create_schema_message(
            stream_name, schema, key_properties
        )

    @classmethod
    def create_record_message(
        cls,
        stream_name: str,
        record: FlextCore.Types.Dict,
        time_extracted: datetime | None = None,
    ) -> FlextCore.Types.Dict:
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
    def convert_ldap_timestamp(cls, timestamp: str) -> FlextCore.Result[str]:
        """Proxy method for LdapDataProcessing.convert_ldap_timestamp()."""
        return cls.LdapDataProcessing.convert_ldap_timestamp(timestamp)

    @classmethod
    def validate_ldap_connection_config(
        cls, config: FlextCore.Types.Dict
    ) -> FlextCore.Result[FlextCore.Types.Dict]:
        """Proxy method for ConfigValidation.validate_ldap_connection_config()."""
        return cls.ConfigValidation.validate_ldap_connection_config(config)

    @classmethod
    def get_stream_state(
        cls, state: FlextCore.Types.Dict, stream_name: str
    ) -> FlextCore.Types.Dict:
        """Proxy method for StateManagement.get_stream_state()."""
        return cls.StateManagement.get_stream_state(state, stream_name)

    @classmethod
    def set_bookmark(
        cls,
        state: FlextCore.Types.Dict,
        stream_name: str,
        bookmark_key: str,
        bookmark_value: object,
    ) -> FlextCore.Types.Dict:
        """Proxy method for StateManagement.set_bookmark()."""
        return cls.StateManagement.set_bookmark(
            state, stream_name, bookmark_key, bookmark_value
        )


__all__ = [
    "FlextMeltanoTapLdapUtilities",
]
