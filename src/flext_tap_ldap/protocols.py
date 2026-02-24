"""FLEXT Tap LDAP Protocols - Domain-specific LDAP tap protocol definitions.

This module provides LDAP tap-specific protocol definitions extending p.
Follows FLEXT standards:
- Domain-specific protocols extending parent protocols
- Protocol composition with multiple inheritance
- Runtime-checkable protocols where applicable

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from flext_ldap import FlextLdapProtocols
from flext_meltano import FlextMeltanoModels as m, FlextMeltanoProtocols

from flext_tap_ldap.typings import t


class FlextMeltanoTapLdapProtocols(FlextMeltanoProtocols, FlextLdapProtocols):
    """LDAP tap-specific protocol definitions extending p.

    Domain-specific protocol system for LDAP data extraction operations.
    Contains ONLY complex LDAP tap-specific protocols extending parent protocols.
    """

    class TapLdap:
        """Tap LDAP namespace for protocol definitions.

        Contains all LDAP tap-specific protocol definitions
        organized by functional domains.
        """

        @runtime_checkable
        class LdapConnectionProtocol(
            FlextLdapProtocols.Service[dict[str, t.JsonValue]],
            Protocol,
        ):
            """Protocol for LDAP database connection management."""

            def connect(
                self,
                config: dict[str, t.JsonValue],
            ) -> FlextMeltanoProtocols.Result[dict[str, t.JsonValue]]:
                """Connect to LDAP database with provided configuration."""
                ...

            def disconnect(self) -> FlextMeltanoProtocols.Result[bool]:
                """Disconnect from LDAP database."""
                ...

            def test_connection(
                self,
                config: dict[str, t.JsonValue],
            ) -> FlextMeltanoProtocols.Result[bool]:
                """Test LDAP database connection with validation."""
                ...

        @runtime_checkable
        class DirectoryDiscoveryProtocol(
            FlextLdapProtocols.Service[dict[str, t.JsonValue]],
            Protocol,
        ):
            """Protocol for LDAP directory discovery."""

            def discover_base_dns(
                self,
                config: dict[str, t.JsonValue],
            ) -> FlextMeltanoProtocols.Result[list[str]]:
                """Discover available base DNs in LDAP directory."""
                ...

            def discover_object_classes(
                self,
                base_dn: str,
            ) -> FlextMeltanoProtocols.Result[list[str]]:
                """Discover object classes in LDAP directory."""
                ...

            def get_directory_metadata(
                self,
                base_dn: str,
            ) -> FlextMeltanoProtocols.Result[dict[str, t.JsonValue]]:
                """Get LDAP directory metadata and schema information."""
                ...

        @runtime_checkable
        class LdapExtractionProtocol(
            FlextLdapProtocols.Service[dict[str, t.JsonValue]],
            Protocol,
        ):
            """Protocol for LDAP data extraction."""

            def extract_entries(
                self,
                base_dn: str,
                filter_str: str,
                attributes: list[str] | None = None,
            ) -> FlextMeltanoProtocols.Result[list[dict[str, t.JsonValue]]]:
                """Extract LDAP entries matching filter."""
                ...

            def extract_single_entry(
                self,
                dn: str,
                attributes: list[str] | None = None,
            ) -> FlextMeltanoProtocols.Result[dict[str, t.JsonValue]]:
                """Extract single LDAP entry by DN."""
                ...

        @runtime_checkable
        class AttributeMappingProtocol(
            FlextLdapProtocols.Service[t.JsonValue],
            Protocol,
        ):
            """Protocol for LDAP to Singer attribute mapping."""

            def map_ldap_attribute(
                self,
                ldap_attr: str,
            ) -> FlextMeltanoProtocols.Result[str]:
                """Map LDAP attribute to Singer field name."""
                ...

            def convert_attribute_value(
                self,
                value: t.JsonValue,
                ldap_attr: str,
            ) -> FlextMeltanoProtocols.Result[t.JsonValue]:
                """Convert LDAP attribute value to Singer-compatible format."""
                ...

        @runtime_checkable
        class StreamGenerationProtocol(
            FlextLdapProtocols.Service[dict[str, t.JsonValue]],
            Protocol,
        ):
            """Protocol for Singer stream generation from LDAP."""

            def generate_streams_from_ldap(
                self,
                base_dn: str,
                config: dict[str, t.JsonValue],
            ) -> FlextMeltanoProtocols.Result[m.Meltano.SingerCatalog]:
                """Generate Singer streams from LDAP directory structure."""
                ...

            def sync_ldap_stream(
                self,
                stream_name: str,
                base_dn: str,
                state: dict[str, t.JsonValue],
            ) -> FlextMeltanoProtocols.Result[m.Meltano.SingerStateMessage]:
                """Sync Singer stream from LDAP entries."""
                ...


# Runtime alias for simplified usage
p = FlextMeltanoTapLdapProtocols


__all__ = [
    "FlextMeltanoTapLdapProtocols",
    "TapConfigProtocol",
    "TapProtocol",
    "p",
]


class TapConfigProtocol(Protocol):
    """Protocol for tap configuration interface."""

    def get_config(
        self,
        key: str,
        default: t.JsonValue | None = None,
    ) -> t.JsonValue:
        """Get configuration value by key.

        Args:
            key: Configuration key.
            default: Default value if key not found.

        Returns:
            Configuration value or default.

        """
        ...


class TapProtocol(Protocol):
    """Protocol for tap interface used by streams.

    Defines the minimal interface that streams need from tap instances,
    avoiding circular dependencies through protocol-based typing.
    """

    @property
    def config(self) -> TapConfigProtocol:
        """Get tap configuration.

        Returns:
            Tap configuration object.

        """
        ...


__all__ = [
    "FlextMeltanoTapLdapProtocols",
    "TapConfigProtocol",
    "TapProtocol",
    "p",
]
