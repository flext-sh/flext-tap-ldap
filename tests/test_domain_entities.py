"""Simplified tests for domain entities."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from flext_tap_ldap.domain.entities import (
    LDAPConnection,
    LDAPRecord,
    LDAPStream,
    TapExecution,
    TapExecutionCompletedEvent,
    TapExecutionStartedEvent,
)


class TestLDAPConnection:
    """Test LDAPConnection entity."""

    def test_ldap_connection_creation(self) -> None:
        """Test creating an LDAP connection."""
        connection = LDAPConnection(
            host="ldap.example.com",
            port=389,
            bind_dn="cn=admin,dc=example,dc=com",
            password="secret",
        )

        assert connection.host == "ldap.example.com"
        assert connection.port == 389
        assert connection.bind_dn == "cn=admin,dc=example,dc=com"
        assert connection.password == "secret"
        assert connection.use_ssl is False
        assert connection.timeout == 30
        assert connection.pool_size == 5
        assert connection.is_active is True
        assert isinstance(connection.id, UUID)

    def test_ldap_connection_with_ssl(self) -> None:
        """Test creating an LDAP connection with SSL."""
        connection = LDAPConnection(
            host="ldaps.example.com",
            port=636,
            bind_dn=None,
            password=None,
            use_ssl=True,
        )

        assert connection.use_ssl is True
        assert connection.port == 636
        assert connection.bind_dn is None
        assert connection.password is None


class TestLDAPStream:
    """Test LDAPStream entity."""

    def test_ldap_stream_creation(self) -> None:
        """Test creating an LDAP stream."""
        connection_id = uuid4()
        stream = LDAPStream(
            connection_id=connection_id,
            stream_type="users",
            tap_stream_id="users",
            search_filter="(objectClass=inetOrgPerson)",
            attributes=["cn", "uid", "mail"],
            key_properties=["dn"],
            replication_method="FULL_TABLE",
            stream_schema={"type": "object", "properties": {}},
        )

        assert stream.stream_type == "users"
        assert stream.connection_id == connection_id
        assert stream.search_filter == "(objectClass=inetOrgPerson)"
        assert stream.attributes == ["cn", "uid", "mail"]
        assert isinstance(stream.id, UUID)
        assert stream.key_properties == ["dn"]
        assert stream.replication_method == "FULL_TABLE"
        assert stream.records_extracted == 0

    def test_ldap_stream_update_schema(self) -> None:
        """Test updating stream schema."""
        connection_id = uuid4()
        stream = LDAPStream(
            connection_id=connection_id,
            stream_type="users",
            tap_stream_id="users",
            search_filter="(objectClass=inetOrgPerson)",
            attributes=["cn"],
            key_properties=["dn"],
            replication_method="FULL_TABLE",
            stream_schema={"type": "object"},
        )

        new_schema = {
            "type": "object",
            "properties": {
                "dn": {"type": "string"},
                "cn": {"type": "string"},
            },
        }

        stream.update_schema(new_schema)
        assert stream.stream_schema == new_schema

    def test_ldap_stream_record_extraction(self) -> None:
        """Test recording extraction metrics."""
        connection_id = uuid4()
        stream = LDAPStream(
            connection_id=connection_id,
            stream_type="users",
            tap_stream_id="users",
            search_filter="(objectClass=inetOrgPerson)",
            attributes=["cn"],
            key_properties=["dn"],
            replication_method="FULL_TABLE",
            stream_schema={},
        )

        initial_count = stream.records_extracted
        stream.record_extraction(10)

        assert stream.records_extracted == initial_count + 10
        assert stream.last_extraction is not None
        assert isinstance(stream.last_extraction, datetime)


class TestTapExecution:
    """Test TapExecution entity."""

    def test_tap_execution_creation(self) -> None:
        """Test creating a tap execution."""
        connection_id = uuid4()
        execution = TapExecution(
            connection_id=connection_id,
            command="sync",
            tap_status="created",
            config={"host": "ldap.example.com"},
            catalog={"streams": []},
            state={"bookmarks": {}},
        )

        assert execution.connection_id == connection_id
        assert execution.command == "sync"
        assert execution.tap_status == "created"
        assert execution.config == {"host": "ldap.example.com"}
        assert execution.catalog == {"streams": []}
        assert execution.state == {"bookmarks": {}}
        assert isinstance(execution.id, UUID)
        assert execution.records_extracted == 0
        assert execution.streams_processed == 0

    def test_tap_execution_start_execution(self) -> None:
        """Test starting execution."""
        connection_id = uuid4()
        execution = TapExecution(
            connection_id=connection_id,
            command="sync",
            tap_status="created",
            config={},
            catalog={},
            state={},
        )

        execution.start_execution()

        assert execution.tap_status == "discovering"
        assert execution.started_at is not None
        assert isinstance(execution.started_at, datetime)

    def test_tap_execution_start_extraction(self) -> None:
        """Test starting extraction phase."""
        connection_id = uuid4()
        execution = TapExecution(
            connection_id=connection_id,
            command="sync",
            tap_status="discovering",
            config={},
            catalog={},
            state={},
        )

        execution.start_extraction()
        assert execution.tap_status == "extracting"

    def test_tap_execution_complete_execution_success(self) -> None:
        """Test completing execution successfully."""
        connection_id = uuid4()
        execution = TapExecution(
            connection_id=connection_id,
            command="sync",
            tap_status="extracting",
            config={},
            catalog={},
            state={},
        )

        # Start execution first
        execution.start_execution()

        # Complete execution
        execution.complete_execution(
            exit_code=0,
            stdout="Extraction completed successfully",
            stderr=None,
        )

        assert execution.tap_status == "completed"
        assert execution.exit_code == 0
        assert execution.stdout == "Extraction completed successfully"
        assert execution.stderr is None
        assert execution.completed_at is not None
        assert execution.duration_seconds is not None
        assert execution.is_completed is True
        assert execution.successful is True

    def test_tap_execution_complete_execution_failure(self) -> None:
        """Test completing execution with failure."""
        connection_id = uuid4()
        execution = TapExecution(
            connection_id=connection_id,
            command="sync",
            tap_status="extracting",
            config={},
            catalog={},
            state={},
        )

        execution.start_execution()

        execution.complete_execution(
            exit_code=1,
            stdout="Some output",
            stderr="Connection failed",
        )

        assert execution.tap_status == "failed"
        assert execution.exit_code == 1
        assert execution.stdout == "Some output"
        assert execution.stderr == "Connection failed"
        assert execution.is_completed is True
        assert execution.successful is False

    def test_tap_execution_cancel_execution(self) -> None:
        """Test cancelling execution."""
        connection_id = uuid4()
        execution = TapExecution(
            connection_id=connection_id,
            command="sync",
            tap_status="extracting",
            config={},
            catalog={},
            state={},
        )

        execution.start_execution()
        execution.cancel_execution()

        assert execution.tap_status == "cancelled"
        assert execution.completed_at is not None
        assert execution.duration_seconds is not None
        assert execution.is_completed is True
        assert execution.successful is False

    def test_tap_execution_update_metrics(self) -> None:
        """Test updating execution metrics."""
        connection_id = uuid4()
        execution = TapExecution(
            connection_id=connection_id,
            command="sync",
            tap_status="extracting",
            config={},
            catalog={},
            state={},
        )

        execution.update_metrics(records_extracted=1500, streams_processed=3)

        assert execution.records_extracted == 1500
        assert execution.streams_processed == 3


class TestLDAPRecord:
    """Test LDAPRecord entity."""

    def test_ldap_record_creation(self) -> None:
        """Test creating an LDAP record."""
        stream_id = uuid4()
        execution_id = uuid4()
        record = LDAPRecord(
            stream_id=stream_id,
            execution_id=execution_id,
            dn="uid=jdoe,ou=users,dc=example,dc=com",
            attributes={
                "cn": ["John Doe"],
                "uid": ["jdoe"],
                "mail": ["jdoe@example.com"],
            },
            object_class=["inetOrgPerson", "organizationalPerson", "person"],
            singer_record={"dn": "uid=jdoe,ou=users,dc=example,dc=com"},
        )

        assert record.stream_id == stream_id
        assert record.execution_id == execution_id
        assert record.dn == "uid=jdoe,ou=users,dc=example,dc=com"
        assert record.attributes["cn"] == ["John Doe"]
        assert record.object_class == [
            "inetOrgPerson",
            "organizationalPerson",
            "person",
        ]
        assert isinstance(record.id, UUID)
        assert record.extracted_at is not None

    def test_ldap_record_rdn_property(self) -> None:
        """Test getting relative DN."""
        stream_id = uuid4()
        execution_id = uuid4()
        record = LDAPRecord(
            stream_id=stream_id,
            execution_id=execution_id,
            dn="uid=jdoe,ou=users,dc=example,dc=com",
            attributes={},
            object_class=[],
            singer_record={},
        )

        assert record.rdn == "uid=jdoe"

    def test_ldap_record_to_singer_record(self) -> None:
        """Test converting to Singer record format."""
        stream_id = uuid4()
        execution_id = uuid4()
        record = LDAPRecord(
            stream_id=stream_id,
            execution_id=execution_id,
            dn="uid=jdoe,ou=users,dc=example,dc=com",
            attributes={
                "cn": ["John Doe"],
                "uid": ["jdoe"],
            },
            object_class=["inetOrgPerson"],
            singer_record={},
        )

        singer_record = record.to_singer_record()

        assert isinstance(singer_record, dict)
        assert singer_record["type"] == "RECORD"
        assert singer_record["record"]["dn"] == "uid=jdoe,ou=users,dc=example,dc=com"
        assert singer_record["record"]["cn"] == ["John Doe"]
        assert singer_record["record"]["object_class"] == ["inetOrgPerson"]
        assert "time_extracted" in singer_record


class TestDomainEvents:
    """Test domain events."""

    def test_tap_execution_started_event(self) -> None:
        """Test tap execution started event."""
        execution_id = uuid4()
        connection_id = uuid4()

        event = TapExecutionStartedEvent(
            execution_id=execution_id,
            connection_id=connection_id,
            command="sync",
        )

        assert event.execution_id == execution_id
        assert event.connection_id == connection_id
        assert event.command == "sync"

    def test_tap_execution_completed_event(self) -> None:
        """Test tap execution completed event."""
        execution_id = uuid4()
        connection_id = uuid4()

        event = TapExecutionCompletedEvent(
            execution_id=execution_id,
            connection_id=connection_id,
        )

        assert event.execution_id == execution_id
        assert event.connection_id == connection_id
