"""Test models for flext-tap-ldap tests.

Provides TestsFlextTapLdapModels, extending FlextTestsModels with
flext-tap-ldap-specific models using COMPOSITION INHERITANCE.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests.models import FlextTestsModels

from flext_tap_ldap.models import FlextTapLdapModels


class TestsFlextTapLdapModels(FlextTestsModels, FlextTapLdapModels):
    """Models for flext-tap-ldap tests using COMPOSITION INHERITANCE.

    MANDATORY: Inherits from BOTH:
    1. FlextTestsModels - for test infrastructure (.Tests.*)
    2. FlextTapLdapModels - for domain models

    Access patterns:
    - tm.Tests.* (generic test models from FlextTestsModels)
    - tm.* (Tap LDAP domain models)
    - m.* (production models via alternative alias)
    """

    class Tests:
        """Project-specific test fixtures namespace."""

        class TapLdap:
            """Tap LDAP-specific test fixtures."""


# Short aliases per FLEXT convention
tm = TestsFlextTapLdapModels
m = TestsFlextTapLdapModels

__all__ = [
    "TestsFlextTapLdapModels",
    "m",
    "tm",
]
