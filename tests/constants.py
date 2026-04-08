"""Test constants for flext-tap-ldap.

Extends FlextTapLdapConstants with Docker infrastructure constants
for integration/e2e tests, accessible as c.Ldap.Tests.Docker.*.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Final

from flext_tests import FlextTestsConstants

from flext_tap_ldap import FlextTapLdapConstants


class TestsFlextTapLdapConstants(FlextTestsConstants, FlextTapLdapConstants):
    """Test constants for flext-tap-ldap.

    Mirrors flext-ldap's c.Ldap.Tests.Docker for shared LDAP test infrastructure.
    """

    class Ldap(FlextTapLdapConstants.Ldap):
        """LDAP test constants extending production Ldap namespace."""

        class Tests:
            """LDAP test-specific constants."""

            class Docker:
                """Docker container infrastructure constants for integration tests.

                Mirrors flext-ldap/tests/constants.py TestsFlextLdapConstants.Ldap.Tests.Docker.
                """

                CONTAINER_NAME: Final[str] = "flext-openldap-test"
                COMPOSE_FILE_REL: Final[str] = "docker/docker-compose.openldap.yml"
                SERVICE_NAME: Final[str] = "openldap"
                PORT: Final[int] = 3390
                BASE_DN: Final[str] = "dc=flext,dc=local"
                ADMIN_DN: Final[str] = "cn=admin,dc=flext,dc=local"
                ADMIN_PASSWORD: Final[str] = "admin123"
                LEGACY_ADMIN_DN: Final[str] = (
                    "cn=REDACTED_LDAP_BIND_PASSWORD,dc=flext,dc=local"
                )
                LEGACY_ADMIN_PASSWORD: Final[str] = "REDACTED_LDAP_BIND_PASSWORD123"


c = TestsFlextTapLdapConstants
__all__ = ["TestsFlextTapLdapConstants", "c"]
