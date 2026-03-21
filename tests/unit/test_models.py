"""Tests for FLEXT Tap LDAP models.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from datetime import datetime

import pytest
from flext_tests import u

from flext_tap_ldap import m


class TestTapExecutionStartedEvent:
    """Test tap execution started event."""

    def test_event_creation(self) -> None:
        """Test creating tap execution started event."""
        event = m.TapLdap.TapExecutionStartedEvent(
            event_type="tap_started",
            aggregate_id="tap-ldap-001",
            execution_id="exec-123",
            config_hash="hash-abc",
        )
        u.Tests.Matchers.that(event.execution_id == "exec-123", eq=True)
        u.Tests.Matchers.that(event.config_hash == "hash-abc", eq=True)
        u.Tests.Matchers.that(event.tap_name == "tap-ldap", eq=True)
        u.Tests.Matchers.that(isinstance(event.timestamp, datetime), eq=True)

    def test_event_defaults(self) -> None:
        """Test event default values."""
        event = m.TapLdap.TapExecutionStartedEvent(
            event_type="tap_started",
            aggregate_id="tap-ldap-002",
            execution_id="exec-456",
        )
        u.Tests.Matchers.that(event.execution_id == "exec-456", eq=True)
        u.Tests.Matchers.that(event.config_hash is None, eq=True)
        u.Tests.Matchers.that(event.tap_name == "tap-ldap", eq=True)


class TestTapExecutionCompletedEvent:
    """Test tap execution completed event."""

    def test_event_creation(self) -> None:
        """Test creating tap execution completed event."""
        event = m.TapLdap.TapExecutionCompletedEvent(
            event_type="tap_completed",
            aggregate_id="tap-ldap-003",
            execution_id="exec-789",
            records_processed=100,
            streams_discovered=4,
            duration_seconds=15.5,
        )
        u.Tests.Matchers.that(event.execution_id == "exec-789", eq=True)
        u.Tests.Matchers.that(event.records_processed == 100, eq=True)
        u.Tests.Matchers.that(event.streams_discovered == 4, eq=True)
        u.Tests.Matchers.that(event.duration_seconds == pytest.approx(15.5), eq=True)

    def test_event_defaults(self) -> None:
        """Test event default values."""
        event = m.TapLdap.TapExecutionCompletedEvent(
            event_type="tap_completed",
            aggregate_id="tap-ldap-004",
            execution_id="exec-000",
        )
        u.Tests.Matchers.that(event.records_processed == 0, eq=True)
        u.Tests.Matchers.that(event.streams_discovered == 0, eq=True)
        u.Tests.Matchers.that(event.duration_seconds == pytest.approx(0.0), eq=True)


class TestStreamDiscoveredEvent:
    """Test stream discovered event."""

    def test_event_creation(self) -> None:
        """Test creating stream discovered event."""
        event = m.TapLdap.StreamDiscoveredEvent(
            event_type="stream_discovered",
            aggregate_id="tap-ldap-005",
            stream_name="users",
            stream_key_properties=["dn"],
            bookmark_key="modifyTimestamp",
        )
        u.Tests.Matchers.that(event.stream_name == "users", eq=True)
        u.Tests.Matchers.that(event.stream_key_properties == ["dn"], eq=True)
        u.Tests.Matchers.that(event.bookmark_key == "modifyTimestamp", eq=True)

    def test_event_defaults(self) -> None:
        """Test event default values."""
        event = m.TapLdap.StreamDiscoveredEvent(
            event_type="stream_discovered",
            aggregate_id="tap-ldap-006",
            stream_name="groups",
        )
        u.Tests.Matchers.that(event.stream_key_properties == [], eq=True)
        u.Tests.Matchers.that(event.bookmark_key is None, eq=True)


class TestRecordExtractedEvent:
    """Test record extracted event."""

    def test_event_creation(self) -> None:
        """Test creating record extracted event."""
        event = m.TapLdap.RecordExtractedEvent(
            event_type="record_extracted",
            aggregate_id="tap-ldap-007",
            stream_name="users",
            record_id="uid=jdoe,ou=users,dc=example,dc=com",
            record_size_bytes=256,
        )
        u.Tests.Matchers.that(event.stream_name == "users", eq=True)
        u.Tests.Matchers.that(
            event.record_id == "uid=jdoe,ou=users,dc=example,dc=com", eq=True
        )
        u.Tests.Matchers.that(event.record_size_bytes == 256, eq=True)

    def test_event_defaults(self) -> None:
        """Test event default values."""
        event = m.TapLdap.RecordExtractedEvent(
            event_type="record_extracted",
            aggregate_id="tap-ldap-008",
            stream_name="groups",
        )
        u.Tests.Matchers.that(event.record_id is None, eq=True)
        u.Tests.Matchers.that(event.record_size_bytes == 0, eq=True)


class TestConnectionTestedEvent:
    """Test connection tested event."""

    def test_event_creation_success(self) -> None:
        """Test creating successful connection tested event."""
        event = m.TapLdap.ConnectionTestedEvent(
            success=True, server_uri="ldap://localhost:389"
        )
        u.Tests.Matchers.that(event.success is True, eq=True)
        u.Tests.Matchers.that(event.server_uri == "ldap://localhost:389", eq=True)
        u.Tests.Matchers.that(event.error_message is None, eq=True)

    def test_event_creation_failure(self) -> None:
        """Test creating failed connection tested event."""
        event = m.TapLdap.ConnectionTestedEvent(
            success=False,
            server_uri="ldap://invalid:389",
            error_message="Connection refused",
        )
        u.Tests.Matchers.that(event.success is False, eq=True)
        u.Tests.Matchers.that(event.error_message == "Connection refused", eq=True)
