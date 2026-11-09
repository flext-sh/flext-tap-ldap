# AUTO-GENERATED FILE — Regenerate with: make gen
"""FLEXT Tap LDAP Protocols — domain-specific LDAP tap protocol facade.

The 5 inner ``TapLdap.*`` Protocol classes that previously lived here had
**zero workspace consumers**. Per AGENTS.md §3.5 + STRICT YAGNI they were
deleted; the canonical ``FlextTapLdapProtocols`` facade remains intact
(re-exported via ``p``) and inherits behaviour from the parent
``FlextMeltanoProtocols`` (``p``) + ``FlextLdapProtocols`` MRO chain.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_ldap import FlextLdapProtocols
from flext_meltano import FlextMeltanoProtocols

from flext_tap_ldap._protocols import (
    FlextTapLdapProtocolsBase,
    FlextTapLdapProtocolsConfig,
    FlextTapLdapProtocolsGeneratedModelsDomainEvent,
    FlextTapLdapProtocolsGeneratedModelsEntity,
)


class FlextTapLdapProtocols(
    FlextMeltanoProtocols,
    FlextLdapProtocols,
    FlextTapLdapProtocolsBase,
    FlextTapLdapProtocolsGeneratedModelsDomainEvent,
    FlextTapLdapProtocolsGeneratedModelsEntity,
):
    """Singer Tap LDAP protocols facade — composes Meltano + LDAP."""

    class TapLdap(
        FlextTapLdapProtocolsBase,
        FlextTapLdapProtocolsConfig,
        FlextTapLdapProtocolsGeneratedModelsDomainEvent,
        FlextTapLdapProtocolsGeneratedModelsEntity,
    ):
        """Tap LDAP protocol namespace."""


p = FlextTapLdapProtocols
__all__: list[str] = ["FlextTapLdapProtocols", "p"]
