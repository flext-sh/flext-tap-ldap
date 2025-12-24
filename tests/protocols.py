"""Test protocol definitions for flext-tap-ldap.

Provides TestsFlextTapLdapProtocols, combining FlextTestsProtocols with
the tap's protocol definitions for test-specific protocol definitions.

Note: flext-tap-ldap defines individual protocols (TapProtocol, TapConfigProtocol)
without a wrapper class. Tests can access FlextTestsProtocols functionality.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tests.protocols import FlextTestsProtocols


class TestsFlextTapLdapProtocols(FlextTestsProtocols):
    """Test protocols for flext-tap-ldap.

    Extends FlextTestsProtocols with tap-specific test protocols.

    Provides access to:
    - tp.Tests.Docker.* (from FlextTestsProtocols)
    - tp.Tests.Factory.* (from FlextTestsProtocols)
    - tp.Tests.TapLdap.* (tap-specific test protocols)
    """

    class Tests:
        """Project-specific test protocols.

        Extends FlextTestsProtocols.Tests with TapLdap-specific protocols.
        """

        class TapLdap:
            """TapLdap-specific test protocols."""


# Runtime aliases
p = TestsFlextTapLdapProtocols
tp = TestsFlextTapLdapProtocols

__all__ = ["TestsFlextTapLdapProtocols", "p", "tp"]
