"""Test models for flext-tap-ldap - uses m.TapLdap.Tests.* namespace pattern.

This module provides test-specific models that extend the main flext-tap-ldap models.
Uses the unified namespace pattern m.TapLdap.Tests.* for test-only objects.
Combines FlextTestsModels functionality with project-specific test models.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_tap_ldap import m
from flext_tests import FlextTestsModels


class TestsFlextMeltanoTapLdapModels(FlextTestsModels, m):
    """Test models combining FlextTestsModels with flext-tap-ldap models."""


m = TestsFlextMeltanoTapLdapModels

__all__ = ["TestsFlextMeltanoTapLdapModels", "m"]
