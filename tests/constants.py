"""Module skeleton for FlextTapLdapTestConstants.

Test constants for flext-tap-ldap.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import FlextTestsConstants

from flext_tap_ldap import FlextTapLdapConstants


class FlextTapLdapTestConstants(FlextTestsConstants, FlextTapLdapConstants):
    """Test constants for flext-tap-ldap."""


c = FlextTapLdapTestConstants
__all__ = ["FlextTapLdapTestConstants", "c"]
