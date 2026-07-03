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
from flext_meltano import p as meltano_p


class FlextTapLdapProtocols(meltano_p, FlextLdapProtocols):
    """Singer Tap LDAP protocols facade — composes Meltano + LDAP."""


p = FlextTapLdapProtocols

__all__: list[str] = ["FlextTapLdapProtocols", "p"]
