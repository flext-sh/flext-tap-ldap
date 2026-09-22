"""Test constants for flext-tap-ldap.

Extends FlextTapLdapConstants with Docker infrastructure constants
for integration/e2e tests, accessible as c.Ldap.Tests.*.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, ClassVar

from flext_tests import FlextTestsConstants

from flext_tap_ldap import FlextTapLdapConstants

if TYPE_CHECKING:
    from . import t


class TestsFlextTapLdapConstants(FlextTestsConstants, FlextTapLdapConstants):
    """Test constants for flext-tap-ldap.

    Mirrors flext-ldap's c.Ldap.Tests for shared LDAP test infrastructure.
    """

    class Ldap(FlextTapLdapConstants.Ldap):
        """LDAP test constants extending production Ldap namespace."""

        class Tests(FlextTestsConstants.Tests):
            """LDAP test-specific constants."""

            HOST: ClassVar[str] = "test.ldap.com"
            PORT: ClassVar[int] = 389
            BASE_DN: ClassVar[str] = "dc=test,dc=com"
            BIND_DN: ClassVar[str] = "cn=REDACTED_LDAP_BIND_PASSWORD,dc=test,dc=com"
            BIND_PASSWORD: ClassVar[str] = os.getenv(
                "FLEXT_TAP_LDAP_BIND_PASSWORD", "test_password"
            )
            USE_TLS: ClassVar[bool] = False
            PAGE_SIZE: ClassVar[int] = 1000
            CONTAINER_PORT: ClassVar[int] = 3390
            ADMIN_DN: ClassVar[str] = "cn=admin,dc=flext,dc=local"
            ADMIN_PASSWORD: ClassVar[str] = os.getenv(
                "FLEXT_TAP_LDAP_ADMIN_PASSWORD", "admin123"
            )
            LEGACY_ADMIN_DN: ClassVar[str] = (
                "cn=REDACTED_LDAP_BIND_PASSWORD,dc=flext,dc=local"
            )
            LEGACY_ADMIN_PASSWORD: ClassVar[str] = os.getenv(
                "FLEXT_TAP_LDAP_LEGACY_ADMIN_PASSWORD", "REDACTED_LDAP_BIND_PASSWORD123"
            )
            STANDARD_STREAMS: ClassVar[t.VariadicTuple[str]] = (
                "users",
                "groups",
                "organizational_units",
                "schema",
            )
            PRIMARY_KEY: ClassVar[t.VariadicTuple[str]] = ("dn",)
            CONSOLE_SCRIPT: ClassVar[str] = "tap-ldap"
            FLAG_CONFIG: ClassVar[str] = "--config"
            FLAG_DISCOVER: ClassVar[str] = "--discover"


c = TestsFlextTapLdapConstants

__all__: list[str] = ["TestsFlextTapLdapConstants", "c"]
