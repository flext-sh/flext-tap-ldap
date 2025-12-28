"""Test models for flext-tap-ldap - uses m.TapLdap.Tests.* namespace pattern.

This module provides test-specific models that extend the main flext-tap-ldap models.
Uses the unified namespace pattern m.TapLdap.Tests.* for test-only objects.
Combines FlextTestsModels functionality with project-specific test models.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_tests import FlextTestsModels

from flext_tap_ldap import m as FlextMeltanoTapLdapModels


class TestsFlextMeltanoTapLdapModels(FlextTestsModels, FlextMeltanoTapLdapModels):
    """Test models combining FlextTestsModels with flext-tap-ldap models."""

    class TapLdap(FlextMeltanoTapLdapModels.TapLdap):
        """TapLdap test models namespace."""

        class Tests:
            """Internal tests declarations."""


m = TestsFlextMeltanoTapLdapModels

__all__ = ["TestsFlextMeltanoTapLdapModels", "m"]
