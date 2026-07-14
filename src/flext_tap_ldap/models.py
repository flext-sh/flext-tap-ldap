"""FLEXT Tap LDAP models - tap-specific events only.

Uses models from parent libraries (flext-ldap, flext-ldif).
Defines only tap-execution and event models specific to LDAP data extraction.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import uuid4

from flext_ldap import m
from flext_meltano import FlextMeltanoModels, u
from flext_tap_ldap import c, t


class FlextTapLdapModels(FlextMeltanoModels, m):
    """Complete models for LDAP tap operations extending m.

    Provides standardized models for all LDAP tap domain entities including:
    - Singer stream metadata and configuration
    - LDAP table extraction configuration
    - Replication and discovery operations
    - Performance monitoring and metrics
    - Singer protocol compliance models

    All nested classes inherit m validation and patterns.
    """

    class TapLdap:
        """Tap LDAP namespace for cross-project access."""

        class CliRequest(m.Value):
            """Validated Singer-compatible root command parameters."""

            config_path: Annotated[
                t.FilePath,
                u.Field(alias="config", description="Existing tap config file"),
            ]
            discover: Annotated[
                bool, u.Field(description="Emit the discovered Singer catalog")
            ] = False
            catalog_path: Annotated[
                t.FilePath | None,
                u.Field(None, alias="catalog", description="Existing catalog file"),
            ] = None
            state_path: Annotated[
                t.FilePath | None,
                u.Field(None, alias="state", description="Existing state file"),
            ] = None

        # ── Domain Events ────────────────────────────────────────────────────

        # ── Config Parameter Objects ─────────────────────────────────────────

        class CustomPropertyDefinition(m.BaseModel):
            """Definition of a custom stream property."""

            type: Annotated[
                str,
                u.Field(
                    description="Data type for the custom stream property",
                ),
            ] = "string"
            description: Annotated[
                str | None,
                u.Field(
                    description="Optional description of the custom property",
                ),
            ] = None

        # ── Entities ─────────────────────────────────────────────────────────

        class LdapConnectionParams(m.Value):
            """LDAP connection parameters for tap configuration."""

            host: t.NonEmptyStr = u.Field(description="LDAP server hostname")
            port: t.PortNumber = u.Field(description="LDAP server port")
            bind_dn: Annotated[
                str | None,
                u.Field(description="Bind DN for authentication"),
            ] = None
            bind_password: Annotated[
                str | None,
                u.Field(description="Bind password for authentication"),
            ] = None
            base_dn: Annotated[
                str | None,
                u.Field(description="Base DN for search operations"),
            ] = None
            use_ssl: bool = u.Field(description="Enable SSL")
            timeout_seconds: t.PositiveInt = u.Field(
                description="Search timeout in seconds",
            )
            page_size: t.PositiveInt = u.Field(
                default=c.TapLdap.DEFAULT_PAGE_SIZE,
                description="Page size for paged results",
            )
            max_retries: t.PositiveInt = u.Field(
                default=3,
                description="Maximum connection retries",
            )

        class LdapConnection(m.Entity):
            """LDAP connection entity with test status and error tracking."""

            host: t.NonEmptyStr = u.Field(
                description="LDAP host address for this connection",
            )
            port: t.PortNumber = u.Field(
                description="LDAP port for this connection",
            )
            bind_dn: Annotated[
                str | None,
                u.Field(
                    description="Bind DN used by the connection",
                ),
            ] = None
            password: Annotated[
                str | None,
                u.Field(
                    description="Bind password used by the connection",
                ),
            ] = None
            use_ssl: Annotated[
                bool,
                u.Field(
                    description="Whether the connection uses SSL/TLS",
                ),
            ] = False
            timeout: t.PositiveInt = u.Field(
                description="Timeout in seconds for this LDAP connection",
            )
            id: str = u.Field(
                default_factory=lambda: uuid4().hex,
                description="Unique identifier for this LDAP connection",
            )
            last_tested: Annotated[
                datetime | None,
                u.Field(
                    description="Timestamp when the connection was last tested",
                ),
            ] = None
            last_error: Annotated[
                str | None,
                u.Field(
                    description="Latest error message from connection testing",
                ),
            ] = None


# Runtime alias for simplified usage
m = FlextTapLdapModels

__all__: list[str] = [
    "FlextTapLdapModels",
    "m",
]
