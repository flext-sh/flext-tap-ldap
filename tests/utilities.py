"""Test utilities for flext-tap-ldap - uses u.TapLdap.* namespace pattern.

This module provides test-specific utilities that extend the main flext-tap-ldap utilities.
Uses the unified namespace pattern u.TapLdap.* for test-only utilities.
Combines FlextTestsUtilities functionality with project-specific test utilities.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_tests import FlextTestsUtilities

from flext_tap_ldap import u


class TestsFlextTapLdapUtilities(FlextTestsUtilities, u):
    """Test utilities combining FlextTestsUtilities with flext-tap-ldap utilities."""

    class TapLdap(u.TapLdap):
        """TapLdap test utilities namespace."""

        class Tests:
            """Internal tests declarations."""


u = TestsFlextTapLdapUtilities

__all__ = ["TestsFlextTapLdapUtilities", "u"]
