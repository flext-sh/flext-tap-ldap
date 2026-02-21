"""Tests for FLEXT Tap LDAP models.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from datetime import datetime

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

        assert event.execution_id == "exec-123"
        assert event.config_hash == "hash-abc"
        assert event.tap_name == "tap-ldap"
        assert isinstance(event.timestamp, datetime)

    def test_event_defaults(self) -> None:
        """Test event default values."""
        event = m.TapLdap.TapExecutionStartedEvent(
            event_type="tap_started",
            aggregate_id="tap-ldap-002",
            execution_id="exec-456",
        )

        assert event.execution_id == "exec-456"
        assert event.config_hash is None
        assert event.tap_name == "tap-ldap"


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

        assert event.execution_id == "exec-789"
        assert event.records_processed == 100
        assert event.streams_discovered == 4
        assert event.duration_seconds == 15.5

    def test_event_defaults(self) -> None:
        """Test event default values."""
        event = m.TapLdap.TapExecutionCompletedEvent(
            event_type="tap_completed",
            aggregate_id="tap-ldap-004",
            execution_id="exec-000",
        )

        assert event.records_processed == 0
        assert event.streams_discovered == 0
        assert event.duration_seconds == 0.0


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

        assert event.stream_name == "users"
        assert event.stream_key_properties == ["dn"]
        assert event.bookmark_key == "modifyTimestamp"

    def test_event_defaults(self) -> None:
        """Test event default values."""
        event = m.TapLdap.StreamDiscoveredEvent(
            event_type="stream_discovered",
            aggregate_id="tap-ldap-006",
            stream_name="groups",
        )

        assert event.stream_key_properties == []
        assert event.bookmark_key is None


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

        assert event.stream_name == "users"
        assert event.record_id == "uid=jdoe,ou=users,dc=example,dc=com"
        assert event.record_size_bytes == 256

    def test_event_defaults(self) -> None:
        """Test event default values."""
        event = m.TapLdap.RecordExtractedEvent(
            event_type="record_extracted",
            aggregate_id="tap-ldap-008",
            stream_name="groups",
        )

        assert event.record_id is None
        assert event.record_size_bytes == 0


class TestConnectionTestedEvent:
    """Test connection tested event."""

    def test_event_creation_success(self) -> None:
        """Test creating successful connection tested event."""
        event = m.TapLdap.ConnectionTestedEvent(
            success=True,
            server_uri="ldap://localhost:389",
        )

        assert event.success is True
        assert event.server_uri == "ldap://localhost:389"
        assert event.error_message is None

    def test_event_creation_failure(self) -> None:
        """Test creating failed connection tested event."""
        event = m.TapLdap.ConnectionTestedEvent(
            success=False,
            server_uri="ldap://invalid:389",
            error_message="Connection refused",
        )

        assert event.success is False
        assert event.error_message == "Connection refused"
