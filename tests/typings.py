"""Test types for flext-tap-ldap — MRO composition with test infrastructure.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import FlextTestsTypes

from flext_tap_ldap import FlextTapLdapTypes


class FlextTapLdapTestTypes(FlextTestsTypes, FlextTapLdapTypes):
    """Test types combining FlextTestsTypes with flext-tap-ldap types."""


t = FlextTapLdapTestTypes
__all__ = ["FlextTapLdapTestTypes", "t"]
