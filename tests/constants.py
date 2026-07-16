"""Test constants for flext-tap-ldap.

Extends FlextTapLdapConstants with Docker infrastructure constants
for integration/e2e tests, accessible as c.Ldap.Tests.*.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Final

from flext_tests import FlextTestsConstants

from flext_tap_ldap import FlextTapLdapConstants


class TestsFlextTapLdapConstants(FlextTestsConstants, FlextTapLdapConstants):
    """Test constants for flext-tap-ldap.

    Mirrors flext-ldap's c.Ldap.Tests for shared LDAP test infrastructure.
    """

    class Ldap(FlextTapLdapConstants.Ldap):
        """LDAP test constants extending production Ldap namespace."""

        class Tests(FlextTestsConstants.Tests):
            """LDAP test-specific constants."""

            HOST: Final[str] = "test.ldap.com"
            PORT: Final[int] = 389
            BASE_DN: Final[str] = "dc=test,dc=com"
            BIND_DN: Final[str] = "cn=REDACTED_LDAP_BIND_PASSWORD,dc=test,dc=com"
            BIND_PASSWORD: Final[str] = "test_password"
            USE_TLS: Final[bool] = False
            PAGE_SIZE: Final[int] = 1000
            CONTAINER_PORT: Final[int] = 3390
            ADMIN_DN: Final[str] = "cn=admin,dc=flext,dc=local"
            ADMIN_PASSWORD: Final[str] = "admin123"
            LEGACY_ADMIN_DN: Final[str] = (
                "cn=REDACTED_LDAP_BIND_PASSWORD,dc=flext,dc=local"
            )
            LEGACY_ADMIN_PASSWORD: Final[str] = "REDACTED_LDAP_BIND_PASSWORD123"
            STANDARD_STREAMS: Final[tuple[str, ...]] = (
                "users",
                "groups",
                "organizational_units",
                "schema",
            )
            PRIMARY_KEY: Final[tuple[str, ...]] = ("dn",)
            CONSOLE_SCRIPT: Final[str] = "tap-ldap"
            FLAG_CONFIG: Final[str] = "--config"
            FLAG_DISCOVER: Final[str] = "--discover"


c = TestsFlextTapLdapConstants

__all__: list[str] = ["TestsFlextTapLdapConstants", "c"]
