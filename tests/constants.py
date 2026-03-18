"""Module skeleton for TestsFlextTapLdapConstants.

Test constants for flexttapldap.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests import c

from flext_tap_ldap import FlextTapLdapConstants


class TestsFlextTapLdapConstants(FlextTestsConstants):
    """Test constants for flexttapldap."""

    class TapLdap(FlextTapLdapConstants.TapLdap):
        """TapLdap contants namespace."""

        class Tests:
            """Internal tests declarations."""


c = TestsFlextTapLdapConstants
__all__ = ["TestsFlextTapLdapConstants", "c"]
