"""LDAP Tap protocol definitions extending FlextCore.Protocols.

This module defines domain-specific protocols for LDAP tap operations,
following the "one class per module" pattern with FlextMeltanoTapLdapProtocols
extending FlextCore.Protocols from flext-core.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from flext_core import FlextCore

from flext_tap_ldap.typings import FlextMeltanoTapLdapTypes


class FlextMeltanoTapLdapProtocols:
    """Singer Tap LDAP protocols with explicit re-exports from FlextCore.Protocols foundation.

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

    Foundation = FlextCore.Protocols.Foundation
    Domain = FlextCore.Protocols.Domain
    Application = FlextCore.Protocols.Application
    Infrastructure = FlextCore.Protocols.Infrastructure
    Extensions = FlextCore.Protocols.Extensions
    Commands = FlextCore.Protocols.Commands

    # ============================================================================
    # SINGER TAP LDAP-SPECIFIC PROTOCOLS (DOMAIN NAMESPACE)
    # ============================================================================

    class TapLdap:
        """Singer Tap LDAP domain protocols for LDAP data extraction and integration."""

        @runtime_checkable
        class LdapConnectionProtocol(FlextCore.Protocols.Domain.Service, Protocol):
            """Protocol for LDAP connection management in Singer tap operations."""

            def connect(
                self, config: FlextCore.Types.Dict
            ) -> FlextCore.Result[FlextCore.Types.object]:
                """Establish connection to LDAP server for data extraction.

                Args:
                    config: LDAP connection configuration

                Returns:
                    FlextCore.Result[FlextCore.Types.object]: LDAP connection object or error

                """

            def disconnect(self) -> FlextCore.Result[None]:
                """Disconnect from LDAP server.

                Returns:
                    FlextCore.Result[None]: Success status or error

                """

            def test_connection(
                self, config: FlextCore.Types.Dict
            ) -> FlextCore.Result[bool]:
                """Test LDAP server connectivity.

                Args:
                    config: LDAP connection configuration

                Returns:
                    FlextCore.Result[bool]: Connection test result or error

                """

            def get_server_info(self) -> FlextCore.Result[FlextCore.Types.Dict]:
                """Get LDAP server information and capabilities.

                Returns:
                    FlextCore.Result[FlextCore.Types.Dict]: Server information or error

                """

            def bind_with_credentials(
                self, username: str, password: str
            ) -> FlextCore.Result[bool]:
                """Bind to LDAP server with credentials.

                Args:
                    username: LDAP bind username
                    password: LDAP bind password

                Returns:
                    FlextCore.Result[bool]: Bind success status or error

                """

        @runtime_checkable
        class SingerStreamProtocol(FlextCore.Protocols.Domain.Service, Protocol):
            """Protocol for Singer stream generation from LDAP data."""

            def discover_streams(
                self, config: FlextCore.Types.Dict
            ) -> FlextCore.Result[list[FlextCore.Types.Dict]]:
                """Discover available LDAP streams for extraction.

                Args:
                    config: Discovery configuration

                Returns:
                    FlextCore.Result[list[FlextCore.Types.Dict]]: Discovered streams or error

                """

            def get_stream_schema(
                self, stream_name: str
            ) -> FlextCore.Result[FlextCore.Types.Dict]:
                """Get schema definition for LDAP stream.

                Args:
                    stream_name: Name of the stream

                Returns:
                    FlextCore.Result[FlextCore.Types.Dict]: Stream schema or error

                """

            def sync_stream(
                self, stream_name: str, state: FlextCore.Types.Dict
            ) -> FlextCore.Result[FlextCore.Types.Dict]:
                """Synchronize LDAP stream data.

                Args:
                    stream_name: Name of the stream to sync
                    state: Current sync state

                Returns:
                    FlextCore.Result[FlextCore.Types.Dict]: Sync results or error

                """

            def write_schema_message(
                self, stream_name: str, schema: FlextCore.Types.Dict
            ) -> FlextCore.Result[None]:
                """Write Singer schema message for LDAP stream.

                Args:
                    stream_name: Name of the stream
                    schema: Stream schema

                Returns:
                    FlextCore.Result[None]: Success status or error

                """

        @runtime_checkable
        class LdifProcessingProtocol(FlextCore.Protocols.Domain.Service, Protocol):
            """Protocol for LDIF processing in Singer tap operations."""

            def parse_ldif_entry(
                self, ldif_entry: str
            ) -> FlextCore.Result[FlextCore.Types.Dict]:
                """Parse LDIF entry to dictionary.

                Args:
                    ldif_entry: LDIF entry string

                Returns:
                    FlextCore.Result[FlextCore.Types.Dict]: Parsed entry or error

                """

            def convert_to_singer_record(
                self, ldap_entry: FlextCore.Types.Dict
            ) -> FlextCore.Result[FlextCore.Types.Dict]:
                """Convert LDAP entry to Singer record format.

                Args:
                    ldap_entry: LDAP entry dictionary

                Returns:
                    FlextCore.Result[FlextCore.Types.Dict]: Singer record or error

                """

            def handle_binary_attributes(
                self, attributes: FlextCore.Types.Dict
            ) -> FlextCore.Result[FlextCore.Types.Dict]:
                """Handle binary LDAP attributes for Singer format.

                Args:
                    attributes: LDAP attributes

                Returns:
                    FlextCore.Result[FlextCore.Types.Dict]: Processed attributes or error

                """

            def normalize_attribute_names(
                self, attributes: FlextCore.Types.Dict
            ) -> FlextCore.Result[FlextCore.Types.Dict]:
                """Normalize LDAP attribute names for Singer compatibility.

                Args:
                    attributes: LDAP attributes

                Returns:
                    FlextCore.Result[FlextCore.Types.Dict]: Normalized attributes or error

                """

        @runtime_checkable
        class TapExecutionProtocol(FlextCore.Protocols.Domain.Service, Protocol):
            """Protocol for Singer tap execution operations."""

            def run_discovery_mode(
                self, config: FlextCore.Types.Dict
            ) -> FlextCore.Result[FlextCore.Types.Dict]:
                """Run tap in discovery mode.

                Args:
                    config: Tap configuration

                Returns:
                    FlextCore.Result[FlextCore.Types.Dict]: Discovery results or error

                """

            def run_sync_mode(
                self,
                config: FlextCore.Types.Dict,
                catalog: FlextCore.Types.Dict,
                state: FlextCore.Types.Dict,
            ) -> FlextCore.Result[FlextCore.Types.Dict]:
                """Run tap in sync mode.

                Args:
                    config: Tap configuration
                    catalog: Stream catalog
                    state: Current state

                Returns:
                    FlextCore.Result[FlextCore.Types.Dict]: Sync results or error

                """

            def handle_interrupt(
                self, state: FlextCore.Types.Dict
            ) -> FlextCore.Result[None]:
                """Handle tap interruption and save state.

                Args:
                    state: Current state to save

                Returns:
                    FlextCore.Result[None]: Success status or error

                """

            def emit_state_message(
                self, state: FlextCore.Types.Dict
            ) -> FlextCore.Result[None]:
                """Emit Singer state message.

                Args:
                    state: State to emit

                Returns:
                    FlextCore.Result[None]: Success status or error

                """

        @runtime_checkable
        class RecordProcessingProtocol(FlextCore.Protocols.Domain.Service, Protocol):
            """Protocol for LDAP record processing in Singer tap."""

            def transform_ldap_record(
                self,
                ldap_record: FlextCore.Types.Dict,
                stream_schema: FlextCore.Types.Dict,
            ) -> FlextCore.Result[FlextCore.Types.Dict]:
                """Transform LDAP record to match stream schema.

                Args:
                    ldap_record: LDAP record
                    stream_schema: Target schema

                Returns:
                    FlextCore.Result[FlextCore.Types.Dict]: Transformed record or error

                """

            def validate_record_schema(
                self, record: FlextCore.Types.Dict, schema: FlextCore.Types.Dict
            ) -> FlextCore.Result[bool]:
                """Validate record against schema.

                Args:
                    record: Record to validate
                    schema: Schema to validate against

                Returns:
                    FlextCore.Result[bool]: Validation result or error

                """

            def emit_record_message(
                self, stream_name: str, record: FlextCore.Types.Dict
            ) -> FlextCore.Result[None]:
                """Emit Singer record message.

                Args:
                    stream_name: Name of the stream
                    record: Record to emit

                Returns:
                    FlextCore.Result[None]: Success status or error

                """

            def handle_record_errors(
                self, record: FlextCore.Types.Dict, error: str
            ) -> FlextCore.Result[None]:
                """Handle record processing errors.

                Args:
                    record: Record that caused error
                    error: Error description

                Returns:
                    FlextCore.Result[None]: Success status or error

                """

        @runtime_checkable
        class ConfigurationProtocol(FlextCore.Protocols.Domain.Service, Protocol):
            """Protocol for Singer tap configuration management."""

            def validate_config(
                self, config: FlextCore.Types.Dict
            ) -> FlextCore.Result[bool]:
                """Validate tap configuration.

                Args:
                    config: Configuration to validate

                Returns:
                    FlextCore.Result[bool]: Validation result or error

                """

            def get_ldap_base_dn(
                self, config: FlextCore.Types.Dict
            ) -> FlextCore.Result[str]:
                """Get LDAP base DN from configuration.

                Args:
                    config: Tap configuration

                Returns:
                    FlextCore.Result[str]: Base DN or error

                """

            def get_ldap_filter(
                self, config: FlextCore.Types.Dict
            ) -> FlextCore.Result[str]:
                """Get LDAP search filter from configuration.

                Args:
                    config: Tap configuration

                Returns:
                    FlextCore.Result[str]: Search filter or error

                """

            def get_selected_attributes(
                self, config: FlextCore.Types.Dict
            ) -> FlextCore.Result[FlextCore.Types.StringList]:
                """Get list of selected LDAP attributes.

                Args:
                    config: Tap configuration

                Returns:
                    FlextCore.Result[FlextCore.Types.StringList]: Selected attributes or error

                """

            def get_replication_method(
                self, stream_name: str, config: FlextCore.Types.Dict
            ) -> FlextCore.Result[str]:
                """Get replication method for stream.

                Args:
                    stream_name: Name of the stream
                    config: Tap configuration

                Returns:
                    FlextCore.Result[str]: Replication method or error

                """

        @runtime_checkable
        class CompleteTapProtocol(
            FlextCore.Protocols.Domain.Service,
            Protocol,
        ):
            """Complete Singer tap protocol combining all LDAP tap operations."""

            def run_tap(
                self,
                config: FlextCore.Types.Dict,
                catalog: FlextCore.Types.Dict | None = None,
                state: FlextCore.Types.Dict | None = None,
            ) -> FlextCore.Result[FlextCore.Types.Dict]:
                """Run complete Singer tap operation.

                Args:
                    config: Tap configuration
                    catalog: Stream catalog (optional, discovery mode if None)
                    state: Current state (optional)

                Returns:
                    FlextCore.Result[FlextCore.Types.Dict]: Tap execution results or error

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


__all__: FlextMeltanoTapLdapTypes.Core.StringList = [
    "FlextMeltanoTapLdapProtocols",
]
