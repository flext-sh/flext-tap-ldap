"""Test types for flext-tap-ldap - uses t.TapLdap.* namespace pattern.

This module provides test-specific types that extend the main flext-tap-ldap types.
Uses the unified namespace pattern t.TapLdap.* for test-only types.
Combines t functionality with project-specific test types.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_tests import t

from flext_tap_ldap import FlextTapLdapTypes


class TestsFlextTapLdapTypes(t, FlextTapLdapTypes):
    """Test types combining t with flext-tap-ldap types."""

    class TapLdap(FlextTapLdapTypes.TapLdap):
        """TapLdap test types namespace."""

        class Tests:
            """Internal tests declarations."""


t = TestsFlextTapLdapTypes
__all__ = ["TestsFlextTapLdapTypes", "t"]
