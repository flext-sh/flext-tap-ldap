"""Domain entities for tap-ldap using flext-core patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pydantic import Field

from flext_core import (
    FlextModels,
    FlextTypes,
)

# Constants
MAX_PORT = 65535


class LDAPConnection(FlextModels.Entity):
    """LDAP connection entity using FlextModels pattern."""

    host: str = Field(..., description="LDAP server hostname")
    port: int = Field(default=389, description="LDAP server port", le=MAX_PORT)
    use_ssl: bool = Field(default=False, description="Use SSL connection")
    bind_dn: str = Field(default="", description="Bind DN for authentication")


class LDAPEntry(FlextModels.Entity):
    """LDAP entry entity."""

    dn: str = Field(..., description="Distinguished Name")
    attributes: FlextTypes.Core.Dict = Field(
        default_factory=dict,
        description="Entry attributes",
    )
    object_class: list[str] = Field(default_factory=list, description="Object classes")


__all__: FlextTypes.Core.StringList = [
    "MAX_PORT",
    "LDAPConnection",
    "LDAPEntry",
]
