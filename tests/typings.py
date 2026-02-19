"""Test types for flext-tap-ldap - uses t.TapLdap.* namespace pattern.

This module provides test-specific types that extend the main flext-tap-ldap types.
Uses the unified namespace pattern t.TapLdap.* for test-only types.
Combines FlextTestsTypes functionality with project-specific test types.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_tap_ldap import t
from flext_tests import FlextTestsTypes


class TestsFlextMeltanoTapLdapTypes(FlextTestsTypes, t):
    """Test types combining FlextTestsTypes with flext-tap-ldap types."""

    class TapLdap(t.TapLdap):
        """TapLdap test types namespace."""

        class Tests:
            """Internal tests declarations."""


t = TestsFlextMeltanoTapLdapTypes

__all__ = ["TestsFlextMeltanoTapLdapTypes", "t"]
