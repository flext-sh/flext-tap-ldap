"""Test utilities for flext-tap-ldap - uses u.TapLdap.* namespace pattern.

Provides test-specific utilities that extend the main flext-tap-ldap utilities.
Includes u.Ldap.Tests.FileLock and u.Ldap.Tests.admin_credentials() for
shared LDAP Docker test infrastructure.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import os
from typing import ClassVar

from flext_tests import FlextTestsUtilities

from flext_core import FlextUtilities
from flext_ldap.adapters._ldap3.wrappers import FlextLdapLdap3Wrappers
from flext_tap_ldap import FlextTapLdapUtilities
from tests import c, p


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

        class Tests:
            """LDAP test infra utilities: FileLock, admin_credentials.

            Mirrors flext-ldap/tests/_utilities/docker_infra.py pattern.
            """

            FileLock = FlextTestsUtilities.Tests.FileLock

            @staticmethod
            def admin_credentials() -> tuple[str, str]:
                """Resolve LDAP admin credentials, trying env vars then known defaults."""
                parent = TestsFlextTapLdapUtilities.Ldap
                if parent._resolved_admin_credentials[0] is not None:
                    return parent._resolved_admin_credentials[0]
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
                u_ldap = TestsFlextTapLdapUtilities.Ldap
                for candidate_dn, candidate_password in candidates:
                    try:
                        server = u_ldap.create_bare_server(
                            "localhost",
                            port=d.CONTAINER_PORT,
                        )
                        test_conn = u_ldap.create_connection(
                            server,
                            user=candidate_dn,
                            password=candidate_password,
                            auto_bind=True,
                            receive_timeout=1,
                        )
                        if test_conn.bound:
                            FlextLdapLdap3Wrappers.unbind(test_conn)
                            parent._resolved_admin_credentials[0] = (
                                candidate_dn,
                                candidate_password,
                            )
                            return (candidate_dn, candidate_password)
                    except (ConnectionError, OSError, ValueError):
                        continue
                parent._resolved_admin_credentials[0] = (
                    d.ADMIN_DN,
                    d.ADMIN_PASSWORD,
                )
                return (d.ADMIN_DN, d.ADMIN_PASSWORD)


u = TestsFlextTapLdapUtilities
__all__: list[str] = ["TestsFlextTapLdapUtilities", "u"]
