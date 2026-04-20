"""Test utilities for flext-tap-ldap - uses u.TapLdap.* namespace pattern.

Provides test-specific utilities that extend the main flext-tap-ldap utilities.
Includes u.Ldap.Tests.FileLock and u.Ldap.Tests.admin_credentials() for
shared LDAP Docker test infrastructure.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import fcntl
import os
import types
from pathlib import Path
from typing import ClassVar, TextIO

from flext_core import FlextUtilities
from flext_ldap import FlextLdapLdap3Wrappers
from flext_tests import FlextTestsUtilities

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

        _logger: ClassVar[p.Logger] = FlextUtilities.fetch_logger(__name__)
        _resolved_admin_credentials: ClassVar[list[tuple[str, str] | None]] = [None]

        class Tests:
            """LDAP test infra utilities: FileLock, admin_credentials.

            Mirrors flext-ldap/tests/_utilities/docker_infra.py pattern.
            """

            class FileLock:
                """File-based locking for pytest-xdist parallel test isolation."""

                def __init__(self, lock_file: Path) -> None:
                    self.lock_file = lock_file
                    self._fd: int | None = None
                    self._file_obj: TextIO | None = None

                def __enter__(self) -> None:
                    """Acquire exclusive file lock."""
                    self.lock_file.parent.mkdir(parents=True, exist_ok=True)
                    self._file_obj = self.lock_file.open("w")
                    self._fd = self._file_obj.fileno()
                    fcntl.flock(self._fd, fcntl.LOCK_EX)

                def __exit__(
                    self,
                    exc_type: type[BaseException] | None,
                    exc_val: BaseException | None,
                    exc_tb: types.TracebackType | None,
                ) -> None:
                    """Release file lock and clean up."""
                    if self._fd is not None:
                        fcntl.flock(self._fd, fcntl.LOCK_UN)
                    if self._file_obj is not None:
                        self._file_obj.close()
                    self.lock_file.unlink(missing_ok=True)

            @staticmethod
            def admin_credentials() -> tuple[str, str]:
                """Resolve LDAP admin credentials, trying env vars then known defaults."""
                parent = TestsFlextTapLdapUtilities.Ldap
                if parent._resolved_admin_credentials[0] is not None:
                    return parent._resolved_admin_credentials[0]
                d = c.Ldap.Tests.Docker
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
                        server = u_ldap.create_bare_server("localhost", port=d.PORT)
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
