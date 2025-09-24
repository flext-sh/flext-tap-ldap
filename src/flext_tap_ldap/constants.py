"""FLEXT Tap LDAP Constants - LDAP tap extraction constants.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import ClassVar

from flext_core import FlextConstants


class FlextTapLdapConstants(FlextConstants):
    """LDAP tap extraction-specific constants following flext-core patterns."""

    # LDAP Connection Configuration
    DEFAULT_LDAP_HOST = "localhost"
    DEFAULT_LDAP_PORT = 389
    DEFAULT_LDAPS_PORT = 636
    DEFAULT_LDAP_TIMEOUT = 30
    DEFAULT_PAGE_SIZE = 1000

    # Singer Tap Configuration
    DEFAULT_BATCH_SIZE = 1000
    MAX_BATCH_SIZE = 10000

    # LDAP Search Configuration
    DEFAULT_SEARCH_SCOPE = "SUBTREE"
    SEARCH_SCOPES: ClassVar[list[str]] = ["BASE", "ONELEVEL", "SUBTREE"]


__all__ = ["FlextTapLdapConstants"]
