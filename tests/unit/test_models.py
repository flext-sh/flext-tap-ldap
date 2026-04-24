"""Tests for FLEXT Tap LDAP models.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from datetime import UTC, datetime

from tests import m


class TestsFlextTapLdapModelsUnit:
    """Test tap execution started event."""

    def test_event_creation(self) -> None:
        """Test creating tap execution started event."""
        event = m.TapLdap.TapExecutionStartedEvent(
            event_type="tap_started",
            aggregate_id="tap-ldap-001",
            timestamp=datetime.now(UTC),
            execution_id="exec-123",
            config_hash="hash-abc",
        )
        assert event.execution_id == "exec-123"
        assert event.config_hash == "hash-abc"
        assert event.tap_name == "tap-ldap"
        assert isinstance(event.timestamp, datetime)

    def test_event_defaults(self) -> None:
        """Test event default values."""
        event = m.TapLdap.TapExecutionStartedEvent(
            event_type="tap_started",
            aggregate_id="tap-ldap-002",
            timestamp=datetime.now(UTC),
            execution_id="exec-456",
        )
        assert event.execution_id == "exec-456"
        assert event.config_hash is None
        assert event.tap_name == "tap-ldap"

    def test_event_creation_success(self) -> None:
        """Test creating successful connection tested event."""
        event = m.TapLdap.ConnectionTestedEvent(
            event_type="connection_tested",
            aggregate_id="ldap://localhost:389",
            success=True,
            server_uri="ldap://localhost:389",
        )
        assert event.success is True
        assert event.server_uri == "ldap://localhost:389"
        assert event.error_message is None

    def test_event_creation_failure(self) -> None:
        """Test creating failed connection tested event."""
        event = m.TapLdap.ConnectionTestedEvent(
            event_type="connection_tested",
            aggregate_id="ldap://invalid:389",
            success=False,
            server_uri="ldap://invalid:389",
            error_message="Connection refused",
        )
        assert event.success is False
        assert event.error_message == "Connection refused"
