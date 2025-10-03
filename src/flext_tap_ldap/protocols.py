"""LDAP Tap protocol definitions extending FlextProtocols.

This module defines domain-specific protocols for LDAP tap operations,
following the "one class per module" pattern with FlextTapLdapProtocols
extending FlextProtocols from flext-core.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from flext_core import FlextProtocols, FlextResult, FlextTypes
from flext_tap_ldap.typings import FlextTapLdapTypes


class FlextTapLdapProtocols:
    """Singer Tap LDAP protocols with explicit re-exports from FlextProtocols foundation.

    This class provides protocol definitions for Singer tap operations with LDAP data extraction,
    directory service integration, schema discovery, and enterprise LDAP data pipelines.

    Domain Extension Pattern (Phase 3):
    - Explicit re-export of foundation protocols (not inheritance)
    - Domain-specific protocols organized in TapLdap namespace
    - 100% backward compatibility through aliases
    """

    # ============================================================================
    # RE-EXPORT FOUNDATION PROTOCOLS (EXPLICIT PATTERN)
    # ============================================================================

    Foundation = FlextProtocols.Foundation
    Domain = FlextProtocols.Domain
    Application = FlextProtocols.Application
    Infrastructure = FlextProtocols.Infrastructure
    Extensions = FlextProtocols.Extensions
    Commands = FlextProtocols.Commands

    # ============================================================================
    # SINGER TAP LDAP-SPECIFIC PROTOCOLS (DOMAIN NAMESPACE)
    # ============================================================================

    class TapLdap:
        """Singer Tap LDAP domain protocols for LDAP data extraction and integration."""

        @runtime_checkable
        class LdapConnectionProtocol(FlextProtocols.Domain.Service, Protocol):
            """Protocol for LDAP connection management in Singer tap operations."""

            def connect(self, config: FlextTypes.Dict) -> FlextResult[FlextTypes.Any]:
                """Establish connection to LDAP server for data extraction.

                Args:
                    config: LDAP connection configuration

                Returns:
                    FlextResult[FlextTypes.Any]: LDAP connection object or error

                """

            def disconnect(self) -> FlextResult[None]:
                """Disconnect from LDAP server.

                Returns:
                    FlextResult[None]: Success status or error

                """

            def test_connection(self, config: FlextTypes.Dict) -> FlextResult[bool]:
                """Test LDAP server connectivity.

                Args:
                    config: LDAP connection configuration

                Returns:
                    FlextResult[bool]: Connection test result or error

                """

            def get_server_info(self) -> FlextResult[FlextTypes.Dict]:
                """Get LDAP server information and capabilities.

                Returns:
                    FlextResult[FlextTypes.Dict]: Server information or error

                """

            def bind_with_credentials(
                self, username: str, password: str
            ) -> FlextResult[bool]:
                """Bind to LDAP server with credentials.

                Args:
                    username: LDAP bind username
                    password: LDAP bind password

                Returns:
                    FlextResult[bool]: Bind success status or error

                """

        @runtime_checkable
        class SingerStreamProtocol(FlextProtocols.Domain.Service, Protocol):
            """Protocol for Singer stream generation from LDAP data."""

            def discover_streams(
                self, config: FlextTypes.Dict
            ) -> FlextResult[list[FlextTypes.Dict]]:
                """Discover available LDAP streams for extraction.

                Args:
                    config: Discovery configuration

                Returns:
                    FlextResult[list[FlextTypes.Dict]]: Discovered streams or error

                """

            def get_stream_schema(
                self, stream_name: str
            ) -> FlextResult[FlextTypes.Dict]:
                """Get schema definition for LDAP stream.

                Args:
                    stream_name: Name of the stream

                Returns:
                    FlextResult[FlextTypes.Dict]: Stream schema or error

                """

            def sync_stream(
                self, stream_name: str, state: FlextTypes.Dict
            ) -> FlextResult[FlextTypes.Dict]:
                """Synchronize LDAP stream data.

                Args:
                    stream_name: Name of the stream to sync
                    state: Current sync state

                Returns:
                    FlextResult[FlextTypes.Dict]: Sync results or error

                """

            def write_schema_message(
                self, stream_name: str, schema: FlextTypes.Dict
            ) -> FlextResult[None]:
                """Write Singer schema message for LDAP stream.

                Args:
                    stream_name: Name of the stream
                    schema: Stream schema

                Returns:
                    FlextResult[None]: Success status or error

                """

        @runtime_checkable
        class LdifProcessingProtocol(FlextProtocols.Domain.Service, Protocol):
            """Protocol for LDIF processing in Singer tap operations."""

            def parse_ldif_entry(self, ldif_entry: str) -> FlextResult[FlextTypes.Dict]:
                """Parse LDIF entry to dictionary.

                Args:
                    ldif_entry: LDIF entry string

                Returns:
                    FlextResult[FlextTypes.Dict]: Parsed entry or error

                """

            def convert_to_singer_record(
                self, ldap_entry: FlextTypes.Dict
            ) -> FlextResult[FlextTypes.Dict]:
                """Convert LDAP entry to Singer record format.

                Args:
                    ldap_entry: LDAP entry dictionary

                Returns:
                    FlextResult[FlextTypes.Dict]: Singer record or error

                """

            def handle_binary_attributes(
                self, attributes: FlextTypes.Dict
            ) -> FlextResult[FlextTypes.Dict]:
                """Handle binary LDAP attributes for Singer format.

                Args:
                    attributes: LDAP attributes

                Returns:
                    FlextResult[FlextTypes.Dict]: Processed attributes or error

                """

            def normalize_attribute_names(
                self, attributes: FlextTypes.Dict
            ) -> FlextResult[FlextTypes.Dict]:
                """Normalize LDAP attribute names for Singer compatibility.

                Args:
                    attributes: LDAP attributes

                Returns:
                    FlextResult[FlextTypes.Dict]: Normalized attributes or error

                """

        @runtime_checkable
        class TapExecutionProtocol(FlextProtocols.Domain.Service, Protocol):
            """Protocol for Singer tap execution operations."""

            def run_discovery_mode(
                self, config: FlextTypes.Dict
            ) -> FlextResult[FlextTypes.Dict]:
                """Run tap in discovery mode.

                Args:
                    config: Tap configuration

                Returns:
                    FlextResult[FlextTypes.Dict]: Discovery results or error

                """

            def run_sync_mode(
                self,
                config: FlextTypes.Dict,
                catalog: FlextTypes.Dict,
                state: FlextTypes.Dict,
            ) -> FlextResult[FlextTypes.Dict]:
                """Run tap in sync mode.

                Args:
                    config: Tap configuration
                    catalog: Stream catalog
                    state: Current state

                Returns:
                    FlextResult[FlextTypes.Dict]: Sync results or error

                """

            def handle_interrupt(self, state: FlextTypes.Dict) -> FlextResult[None]:
                """Handle tap interruption and save state.

                Args:
                    state: Current state to save

                Returns:
                    FlextResult[None]: Success status or error

                """

            def emit_state_message(self, state: FlextTypes.Dict) -> FlextResult[None]:
                """Emit Singer state message.

                Args:
                    state: State to emit

                Returns:
                    FlextResult[None]: Success status or error

                """

        @runtime_checkable
        class RecordProcessingProtocol(FlextProtocols.Domain.Service, Protocol):
            """Protocol for LDAP record processing in Singer tap."""

            def transform_ldap_record(
                self, ldap_record: FlextTypes.Dict, stream_schema: FlextTypes.Dict
            ) -> FlextResult[FlextTypes.Dict]:
                """Transform LDAP record to match stream schema.

                Args:
                    ldap_record: LDAP record
                    stream_schema: Target schema

                Returns:
                    FlextResult[FlextTypes.Dict]: Transformed record or error

                """

            def validate_record_schema(
                self, record: FlextTypes.Dict, schema: FlextTypes.Dict
            ) -> FlextResult[bool]:
                """Validate record against schema.

                Args:
                    record: Record to validate
                    schema: Schema to validate against

                Returns:
                    FlextResult[bool]: Validation result or error

                """

            def emit_record_message(
                self, stream_name: str, record: FlextTypes.Dict
            ) -> FlextResult[None]:
                """Emit Singer record message.

                Args:
                    stream_name: Name of the stream
                    record: Record to emit

                Returns:
                    FlextResult[None]: Success status or error

                """

            def handle_record_errors(
                self, record: FlextTypes.Dict, error: str
            ) -> FlextResult[None]:
                """Handle record processing errors.

                Args:
                    record: Record that caused error
                    error: Error description

                Returns:
                    FlextResult[None]: Success status or error

                """

        @runtime_checkable
        class ConfigurationProtocol(FlextProtocols.Domain.Service, Protocol):
            """Protocol for Singer tap configuration management."""

            def validate_config(self, config: FlextTypes.Dict) -> FlextResult[bool]:
                """Validate tap configuration.

                Args:
                    config: Configuration to validate

                Returns:
                    FlextResult[bool]: Validation result or error

                """

            def get_ldap_base_dn(self, config: FlextTypes.Dict) -> FlextResult[str]:
                """Get LDAP base DN from configuration.

                Args:
                    config: Tap configuration

                Returns:
                    FlextResult[str]: Base DN or error

                """

            def get_ldap_filter(self, config: FlextTypes.Dict) -> FlextResult[str]:
                """Get LDAP search filter from configuration.

                Args:
                    config: Tap configuration

                Returns:
                    FlextResult[str]: Search filter or error

                """

            def get_selected_attributes(
                self, config: FlextTypes.Dict
            ) -> FlextResult[list[str]]:
                """Get list of selected LDAP attributes.

                Args:
                    config: Tap configuration

                Returns:
                    FlextResult[list[str]]: Selected attributes or error

                """

            def get_replication_method(
                self, stream_name: str, config: FlextTypes.Dict
            ) -> FlextResult[str]:
                """Get replication method for stream.

                Args:
                    stream_name: Name of the stream
                    config: Tap configuration

                Returns:
                    FlextResult[str]: Replication method or error

                """

        @runtime_checkable
        class CompleteTapProtocol(
            FlextProtocols.Domain.Service,
            Protocol,
        ):
            """Complete Singer tap protocol combining all LDAP tap operations."""

            def run_tap(
                self,
                config: FlextTypes.Dict,
                catalog: FlextTypes.Dict | None = None,
                state: FlextTypes.Dict | None = None,
            ) -> FlextResult[FlextTypes.Dict]:
                """Run complete Singer tap operation.

                Args:
                    config: Tap configuration
                    catalog: Stream catalog (optional, discovery mode if None)
                    state: Current state (optional)

                Returns:
                    FlextResult[FlextTypes.Dict]: Tap execution results or error

                """

    # ============================================================================
    # BACKWARD COMPATIBILITY ALIASES (100% COMPATIBILITY)
    # ============================================================================

    # LDAP connection
    LdapConnectionProtocol = TapLdap.LdapConnectionProtocol

    # Singer streams
    SingerStreamProtocol = TapLdap.SingerStreamProtocol

    # LDIF processing
    LdifProcessingProtocol = TapLdap.LdifProcessingProtocol

    # Tap execution
    TapExecutionProtocol = TapLdap.TapExecutionProtocol

    # Record processing
    RecordProcessingProtocol = TapLdap.RecordProcessingProtocol

    # Configuration
    ConfigurationProtocol = TapLdap.ConfigurationProtocol

    # Complete tap
    CompleteTapProtocol = TapLdap.CompleteTapProtocol


__all__: FlextTapLdapTypes.Core.StringList = [
    "FlextTapLdapProtocols",
]
