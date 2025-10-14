"""Domain entities for tap-ldap using flext-core patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_core import FlextCore
from pydantic import Field

from flext_tap_ldap.typings import FlextMeltanoTapLdapTypes

# Constants
MAX_PORT = 65535


class LDAPConnection(FlextCore.Models.Entity):
    """LDAP connection entity using FlextCore.Models pattern."""

    host: str = Field(..., description="LDAP server hostname")
    port: int = Field(
        default=FlextCore.Constants.Platform.LDAP_DEFAULT_PORT,
        description="LDAP server port",
        le=MAX_PORT,
    )
    use_ssl: bool = Field(default=False, description="Use SSL connection")
    bind_dn: str = Field(default="", description="Bind DN for authentication")


class LDAPEntry(FlextCore.Models.Entity):
    """LDAP entry entity."""

    dn: str = Field(..., description="Distinguished Name")
    attributes: FlextMeltanoTapLdapTypes.Core.Dict = Field(
        default_factory=dict,
        description="Entry attributes",
    )
    object_class: FlextCore.Types.StringList = Field(
        default_factory=list, description="Object classes"
    )


__all__: FlextMeltanoTapLdapTypes.Core.StringList = [
    "MAX_PORT",
    "LDAPConnection",
    "LDAPEntry",
]
