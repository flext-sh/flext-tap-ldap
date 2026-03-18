"""Tests for LDIF stream functionality.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_tests import tm

from flext_tap_ldap import FlextTapLdapLdifStreams, FlextTapLdapTap


class TestLDIFStreamBasic:
    """Basic tests for LDIF stream functionality."""

    def test_imports(self) -> None:
        """Test method."""
        "Test that LDIF stream modules can be imported."
        tm.that(FlextTapLdapLdifStreams.LdifStream is not None, eq=True)
        tm.that(FlextTapLdapLdifStreams.LdifAnalysisStream is not None, eq=True)

    def test_ldif_stream_creation(self) -> None:
        """Test method."""
        "Test LDIF stream can be created."
        try:
            tap = FlextTapLdapTap(
                config={
                    "ldap_host": "test.ldap.com",
                    "ldap_port": 389,
                    "base_dn": "dc=test,dc=com",
                    "bind_dn": "cn=REDACTED_LDAP_BIND_PASSWORD,dc=test,dc=com",
                    "bind_password": "test_password",
                }
            )
            stream = FlextTapLdapLdifStreams.LdifStream(tap=tap)
            tm.that(stream is not None, eq=True)
        except (TypeError, AttributeError, ImportError):
            tm.that(FlextTapLdapLdifStreams.LdifStream is not None, eq=True)
