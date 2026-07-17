"""Test types for flext-tap-ldap — MRO composition with test infrastructure.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import FlextTestsTypes

from flext_tap_ldap import FlextTapLdapTypes


class TestsFlextTapLdapTypes(FlextTestsTypes, FlextTapLdapTypes):
    """Test types combining TestsFlextTypes with flext-tap-ldap types."""

    type Entry = dict[str, str | dict[str, list[str]]]


t = TestsFlextTapLdapTypes
__all__: list[str] = ["TestsFlextTapLdapTypes", "t"]
