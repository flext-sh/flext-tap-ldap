"""Test protocols for flext-tap-ldap - uses p.TapLdap.* namespace pattern.

This module provides test-specific protocols that extend the main flext-tap-ldap protocols.
Uses the unified namespace pattern p.TapLdap.* for test-only protocols.
Combines p functionality with project-specific test protocols.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_tests import p

from flext_tap_ldap.protocols import FlextTapLdapProtocols


class TestsFlextTapLdapProtocols(p, FlextTapLdapProtocols):
    """Test protocols combining p with flext-tap-ldap protocols."""

    class TapLdap(FlextTapLdapProtocols.TapLdap):
        """TapLdap test protocols namespace."""

        class Tests:
            """Internal tests declarations."""


p = TestsFlextTapLdapProtocols
__all__ = ["TestsFlextTapLdapProtocols", "p"]
