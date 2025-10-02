"""LDAP Tap protocol definitions extending FlextProtocols.

This module defines domain-specific protocols for LDAP tap operations,
following the "one class per module" pattern with FlextTapLdapProtocols
extending FlextProtocols from flext-core.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol

from flext_core import FlextProtocols, FlextResult
from flext_tap_ldap.typings import FlextTapLdapTypes


class FlextTapLdapProtocols(FlextProtocols):
    """LDAP Tap protocol hierarchy extending FlextProtocols.

    Provides domain-specific protocols for LDAP tap operations including:
    - LDAP connection and client protocols
    - Singer stream extraction protocols
    - LDIF processing protocols
    - Tap execution and orchestration protocols
    - Record processing and transformation protocols

    All nested protocols extend appropriate FlextProtocols base protocols
    to maintain consistency with the FLEXT architecture.
    """

    class LdapConnectionProtocol(FlextProtocols.Domain.Service, Protocol):
        """Protocol for LDAP connection management in tap operations.

        Defines the interface for establishing, managing, and validating
        LDAP connections specifically for data extraction scenarios.
        """

        def connect(
            self,
            host: str,
            port: int = 389,
            *,
            bind_dn: str | None = None,
            password: str | None = None,
            use_ssl: bool = False,
            timeout: int = 30,
        ) -> FlextResult[bool]:
            """Establish connection to LDAP server.

            Args:
                host: LDAP server hostname
                port: LDAP server port (default 389)
                bind_dn: Distinguished name for binding
                password: Password for authentication
                use_ssl: Whether to use SSL/TLS
                timeout: Connection timeout in seconds

            Returns:
                FlextResult containing connection success status

            """

        def disconnect(self) -> FlextResult[None]:
            """Disconnect from LDAP server.

            Returns:
                FlextResult indicating disconnection status

            """

        def is_connected(self) -> bool:
            """Check if currently connected to LDAP server.

            Returns:
                True if connected, False otherwise

            """

        def test_connection(self) -> FlextResult[FlextTapLdapTypes.Core.Dict]:
            """Test LDAP connection and return diagnostics.

            Returns:
                FlextResult containing connection test results and metrics

            """

        def get_connection_info(self) -> FlextTapLdapTypes.Core.Dict:
            """Get current connection information.

            Returns:
                Dictionary with connection details and status

            """

    class SingerStreamProtocol(FlextProtocols.Domain.Service, Protocol):
        """Protocol for Singer stream operations in LDAP taps.

        Defines the interface for discovering, configuring, and executing
        Singer streams for LDAP data extraction.
        """

        def discover_streams(self) -> FlextResult[list[FlextTapLdapTypes.Core.Dict]]:
            """Discover available LDAP streams for extraction.

            Returns:
                FlextResult containing list of discoverable stream definitions

            """

        def get_stream_schema(
            self,
            stream_name: str,
        ) -> FlextResult[FlextTapLdapTypes.Core.Dict]:
            """Get JSON schema for specified stream.

            Args:
                stream_name: Name of the stream

            Returns:
                FlextResult containing the stream's JSON schema

            """

        def extract_records(
            self,
            stream_name: str,
            *,
            ldap_filter: str | None = None,
            base_dn: str | None = None,
            attributes: list[str] | None = None,
        ) -> FlextResult[Iterable[FlextTapLdapTypes.Core.Dict]]:
            """Extract records from LDAP stream.

            Args:
                stream_name: Name of the stream to extract
                ldap_filter: LDAP search filter
                base_dn: Base distinguished name for search
                attributes: List of attributes to retrieve

            Returns:
                FlextResult containing iterable of extracted records

            """

        def get_stream_metadata(
            self,
            stream_name: str,
        ) -> FlextResult[FlextTapLdapTypes.Core.Dict]:
            """Get metadata for specified stream.

            Args:
                stream_name: Name of the stream

            Returns:
                FlextResult containing stream metadata

            """

    class LdifProcessingProtocol(FlextProtocols.Domain.Service, Protocol):
        """Protocol for LDIF file processing in taps.

        Defines the interface for parsing, analyzing, and extracting
        data from LDIF files as part of tap operations.
        """

        def parse_ldif_file(
            self,
            file_path: str,
        ) -> FlextResult[Iterable[FlextTapLdapTypes.Core.Dict]]:
            """Parse LDIF file and extract entries.

            Args:
                file_path: Path to LDIF file

            Returns:
                FlextResult containing iterable of parsed LDIF entries

            """

        def analyze_ldif_file(
            self,
            file_path: str,
        ) -> FlextResult[FlextTapLdapTypes.Core.Dict]:
            """Analyze LDIF file structure and statistics.

            Args:
                file_path: Path to LDIF file

            Returns:
                FlextResult containing analysis results and statistics

            """

        def validate_ldif_file(
            self,
            file_path: str,
        ) -> FlextResult[FlextTapLdapTypes.Core.Dict]:
            """Validate LDIF file format and content.

            Args:
                file_path: Path to LDIF file

            Returns:
                FlextResult containing validation results

            """

        def process_ldif_directory(
            self,
            directory_path: str,
        ) -> FlextResult[Iterable[FlextTapLdapTypes.Core.Dict]]:
            """Process all LDIF files in a directory.

            Args:
                directory_path: Path to directory containing LDIF files

            Returns:
                FlextResult containing iterable of all processed entries

            """

    class TapExecutionProtocol(FlextProtocols.Application.Handler, Protocol):
        """Protocol for tap execution orchestration.

        Defines the interface for managing complete tap execution
        workflows including discovery, extraction, and state management.
        """

        def execute_discovery(self) -> FlextResult[FlextTapLdapTypes.Core.Dict]:
            """Execute tap discovery phase.

            Returns:
                FlextResult containing discovery catalog

            """

        def execute_extraction(
            self,
            catalog: FlextTapLdapTypes.Core.Dict,
            *,
            state: FlextTapLdapTypes.Core.Dict | None = None,
        ) -> FlextResult[Iterable[FlextTapLdapTypes.Core.Dict]]:
            """Execute tap extraction phase.

            Args:
                catalog: Singer catalog configuration
                state: Optional state for incremental extraction

            Returns:
                FlextResult containing extracted records

            """

        def get_execution_metrics(self) -> FlextTapLdapTypes.Core.Dict:
            """Get execution performance metrics.

            Returns:
                Dictionary containing execution metrics and statistics

            """

        def handle_execution_errors(
            self,
            error: Exception,
        ) -> FlextResult[None]:
            """Handle and process execution errors.

            Args:
                error: Exception that occurred during execution

            Returns:
                FlextResult indicating error handling status

            """

    class RecordProcessingProtocol(FlextProtocols.Domain.Service, Protocol):
        """Protocol for LDAP record processing and transformation.

        Defines the interface for transforming LDAP entries into
        Singer-compatible records with proper type handling.
        """

        def transform_ldap_entry(
            self,
            entry: FlextTapLdapTypes.Core.Dict,
        ) -> FlextResult[FlextTapLdapTypes.Core.Dict]:
            """Transform LDAP entry to Singer record format.

            Args:
                entry: Raw LDAP entry data

            Returns:
                FlextResult containing transformed Singer record

            """

        def validate_record_schema(
            self,
            record: FlextTapLdapTypes.Core.Dict,
            schema: FlextTapLdapTypes.Core.Dict,
        ) -> FlextResult[bool]:
            """Validate record against JSON schema.

            Args:
                record: Record to validate
                schema: JSON schema for validation

            Returns:
                FlextResult containing validation status

            """

        def apply_record_filters(
            self,
            record: FlextTapLdapTypes.Core.Dict,
            filters: FlextTapLdapTypes.Core.Dict,
        ) -> FlextResult[bool]:
            """Apply filtering rules to record.

            Args:
                record: Record to filter
                filters: Filter configuration

            Returns:
                FlextResult indicating if record passes filters

            """

        def enrich_record_metadata(
            self,
            record: FlextTapLdapTypes.Core.Dict,
        ) -> FlextResult[FlextTapLdapTypes.Core.Dict]:
            """Enrich record with extraction metadata.

            Args:
                record: Record to enrich

            Returns:
                FlextResult containing enriched record

            """

    class ConfigurationProtocol(FlextProtocols.Infrastructure.Configurable, Protocol):
        """Protocol for tap configuration management.

        Defines the interface for managing tap configuration,
        validation, and runtime settings.
        """

        def load_tap_config(
            self,
            config_path: str | None = None,
        ) -> FlextResult[FlextTapLdapTypes.Core.Dict]:
            """Load tap configuration from file or environment.

            Args:
                config_path: Optional path to configuration file

            Returns:
                FlextResult containing loaded configuration

            """

        def validate_tap_config(
            self,
            config: FlextTapLdapTypes.Core.Dict,
        ) -> FlextResult[None]:
            """Validate tap configuration completeness and correctness.

            Args:
                config: Configuration to validate

            Returns:
                FlextResult indicating validation status

            """

        def get_default_config(self) -> FlextTapLdapTypes.Core.Dict:
            """Get default tap configuration.

            Returns:
                Dictionary containing default configuration values

            """

        def merge_config_sources(
            self,
            *configs: FlextTapLdapTypes.Core.Dict,
        ) -> FlextResult[FlextTapLdapTypes.Core.Dict]:
            """Merge multiple configuration sources with precedence.

            Args:
                configs: Configuration dictionaries to merge

            Returns:
                FlextResult containing merged configuration

            """

    # Protocol composition for complete tap implementations
    class CompleteTapProtocol(
        LdapConnectionProtocol,
        SingerStreamProtocol,
        TapExecutionProtocol,
        ConfigurationProtocol,
        Protocol,
    ):
        """Composite protocol for complete LDAP tap implementations.

        Combines all essential protocols for a fully functional
        LDAP tap that can handle connection, stream discovery,
        extraction, and configuration management.
        """

        def get_tap_info(self) -> FlextTapLdapTypes.Core.Dict:
            """Get comprehensive tap information and capabilities.

            Returns:
                Dictionary containing tap metadata and capabilities

            """

        def execute_extraction(
            self,
            catalog: FlextTapLdapTypes.Core.Dict,
        ) -> Iterable[FlextTapLdapTypes.Core.Dict]:
            """Execute hronous extraction for high-volume scenarios.

            Args:
                catalog: Singer catalog configuration

            Returns:
                iterable of extracted records

            """


__all__: FlextTapLdapTypes.Core.StringList = [
    "FlextTapLdapProtocols",
]
