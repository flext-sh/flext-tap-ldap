"""Test utilities for flext-tap-ldap - uses u.TapLdap.* namespace pattern.

Provides test-specific utilities that extend the main flext-tap-ldap utilities.
Includes u.Ldap.Tests.FileLock and u.Ldap.Tests.admin_credentials() for
shared LDAP Docker test infrastructure.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, ClassVar

from flext_core import FlextUtilities
from flext_ldap.adapters.ldap3 import FlextLdapLdap3Wrappers
from flext_tap_ldap import FlextTapLdapUtilities
from flext_tests import FlextTestsUtilities
from tests import c

if TYPE_CHECKING:
    from tests import p


class TestsFlextTapLdapUtilities(FlextTestsUtilities, FlextTapLdapUtilities):
    """Test utilities combining TestsFlextUtilities with flext-tap-ldap utilities."""

    class TapLdap(FlextTapLdapUtilities.TapLdap):
        """TapLdap test utilities namespace."""

        class Tests:
            """Internal tests declarations."""

    class Ldap(FlextTapLdapUtilities.Ldap):
        """LDAP test utilities with Docker infra helpers."""

        logger: ClassVar[p.Logger] = FlextUtilities.fetch_logger(__name__)
        _resolved_admin_credentials: ClassVar[list[tuple[str, str] | None]] = [None]

        @classmethod
        def admin_credentials(cls) -> tuple[str, str]:
            """Resolve LDAP admin credentials, trying env vars then known defaults."""
            cached = cls._resolved_admin_credentials[0]
            if cached is not None:
                return cached
            d = c.Ldap.Tests
            env_dn = os.getenv("FLEXT_LDAP_BIND_DN")
            env_password = os.getenv("FLEXT_LDAP_BIND_PASSWORD")
            candidates: list[tuple[str, str]] = []
            if env_dn and env_password:
                candidates.append((env_dn, env_password))
            candidates.extend([
                (d.ADMIN_DN, d.ADMIN_PASSWORD),
                (d.LEGACY_ADMIN_DN, d.LEGACY_ADMIN_PASSWORD),
            ])
            for candidate_dn, candidate_password in candidates:
                try:
                    server = cls.create_bare_server("localhost", port=d.CONTAINER_PORT)
                    test_conn = cls.create_connection(
                        server,
                        user=candidate_dn,
                        password=candidate_password,
                        auto_bind=True,
                        receive_timeout=1,
                    )
                    if test_conn.bound:
                        FlextLdapLdap3Wrappers.unbind(test_conn)
                        cls._resolved_admin_credentials[0] = (
                            candidate_dn,
                            candidate_password,
                        )
                        return (candidate_dn, candidate_password)
                except (ConnectionError, OSError, ValueError):
                    continue
            cls._resolved_admin_credentials[0] = (d.ADMIN_DN, d.ADMIN_PASSWORD)
            return (d.ADMIN_DN, d.ADMIN_PASSWORD)

        class Tests:
            """LDAP test infra utilities: FileLock, admin_credentials.

            Mirrors flext-ldap/tests/_utilities/docker_infra.py pattern.
            """

            FileLock = FlextTestsUtilities.Tests.FileLock

            @staticmethod
            def admin_credentials() -> tuple[str, str]:
                """Resolve LDAP admin credentials, trying env vars then known defaults."""
                return TestsFlextTapLdapUtilities.Ldap.admin_credentials()


u = TestsFlextTapLdapUtilities
__all__: list[str] = ["TestsFlextTapLdapUtilities", "u"]
