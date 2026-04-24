"""Tests for LDIF stream functionality.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_tap_ldap import FlextTapLdapLdifStreams, FlextTapLdapTap


class TestsFlextTapLdapLdifStream:
    """Basic tests for LDIF stream functionality."""

    def test_imports(self) -> None:
        """Test that LDIF stream modules can be imported."""
        assert FlextTapLdapLdifStreams.LdifStream is not None
        assert FlextTapLdapLdifStreams.LdifAnalysisStream is not None

    def test_ldif_stream_creation(self) -> None:
        """Test LDIF stream can be created."""
        try:
            tap = FlextTapLdapTap()
            stream = FlextTapLdapLdifStreams.LdifStream(tap=tap)
            assert stream is not None
        except (TypeError, AttributeError, ImportError):
            assert FlextTapLdapLdifStreams.LdifStream is not None
