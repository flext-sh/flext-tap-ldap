"""Tests for application services layer.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from uuid import uuid4

import pytest

from flext_tap_ldap import (
    LDAPConnectionParams,
    LDAPConnectionService,
    LDAPRecordService,
    LDAPStreamService,
    StreamCreationParams,
    TapExecutionService,
)


class TestLDAPConnectionParams:
    """Test LDAPConnectionParams parameter object."""

    def test_valid_params_creation(self) -> None:
        """Test creating valid connection parameters."""
        params = LDAPConnectionParams(
            host="localhost",
            port=389,
            bind_dn="cn=REDACTED_LDAP_BIND_PASSWORD,dc=test,dc=com",
            bind_password="password",
            use_ssl=False,
        )

        assert params.host == "localhost"
        assert params.port == 389
        assert params.bind_dn == "cn=REDACTED_LDAP_BIND_PASSWORD,dc=test,dc=com"
        assert params.bind_password == "password"
        assert params.use_ssl is False

    def test_invalid_host_validation(self) -> None:
        """Test host validation."""
        with pytest.raises(ValueError, match="Host is required"):
            LDAPConnectionParams(host="")

    def test_invalid_port_validation(self) -> None:
        """Test port validation."""
        with pytest.raises(ValueError, match="Port must be between 1 and 65535"):
            LDAPConnectionParams(host="localhost", port=0)

        with pytest.raises(ValueError, match="Port must be between 1 and 65535"):
            LDAPConnectionParams(host="localhost", port=70000)

    def test_invalid_timeout_validation(self) -> None:
        """Test timeout validation."""
        with pytest.raises(ValueError, match="Timeout must be positive"):
            LDAPConnectionParams(host="localhost", timeout_seconds=0)

    def test_invalid_page_size_validation(self) -> None:
        """Test page size validation."""
        with pytest.raises(ValueError, match="Page size must be positive"):
            LDAPConnectionParams(host="localhost", page_size=0)

    def test_invalid_max_retries_validation(self) -> None:
        """Test max retries validation."""
        with pytest.raises(ValueError, match="Max retries cannot be negative"):
            LDAPConnectionParams(host="localhost", max_retries=-1)


class TestLDAPConnectionService:
    """Test LDAP connection service."""

    @pytest.fixture
    def service(self) -> LDAPConnectionService:
        """Create connection service instance."""
        return LDAPConnectionService()

    @pytest.fixture
    def valid_params(self) -> LDAPConnectionParams:
        """Create valid connection parameters."""
        return LDAPConnectionParams(
            host="localhost",
            port=389,
            bind_dn="cn=REDACTED_LDAP_BIND_PASSWORD,dc=test,dc=com",
            bind_password="password",
        )

    async def test_create_connection_success(
        self,
        service: LDAPConnectionService,
        valid_params: LDAPConnectionParams,
    ) -> None:
        """Test successful connection creation."""
        result = await service.create_connection(valid_params)

        assert result.success
        assert result.data is not None
        # Verify connection is stored
        assert len(service._connections) == 1

    async def test_create_connection_stores_multiple(
        self,
        service: LDAPConnectionService,
        valid_params: LDAPConnectionParams,
    ) -> None:
        """Test creating multiple connections."""
        result1 = await service.create_connection(valid_params)
        result2 = await service.create_connection(valid_params)

        assert result1.success
        assert result2.success
        assert len(service._connections) == 2
        assert result1.data.id != result2.data.id

    async def test_get_connection_success(
        self,
        service: LDAPConnectionService,
        valid_params: LDAPConnectionParams,
    ) -> None:
        """Test getting existing connection."""
        create_result = await service.create_connection(valid_params)
        connection_id = create_result.data.id

        get_result = await service.get_connection(connection_id)

        assert get_result.success
        assert get_result.data.id == connection_id

    async def test_get_nonexistent_connection(
        self,
        service: LDAPConnectionService,
    ) -> None:
        """Test getting non-existent connection."""
        result = await service.get_connection(uuid4())

        assert result.success
        assert result.data is None

    async def test_list_connections_empty(
        self,
        service: LDAPConnectionService,
    ) -> None:
        """Test listing connections when empty."""
        result = await service.list_connections()

        assert result.success
        assert result.data == []

    async def test_list_connections_with_data(
        self,
        service: LDAPConnectionService,
        valid_params: LDAPConnectionParams,
    ) -> None:
        """Test listing connections with data."""
        await service.create_connection(valid_params)
        await service.create_connection(valid_params)

        result = await service.list_connections()

        assert result.success
        assert len(result.data) == 2

    async def test_test_connection_success(
        self,
        service: LDAPConnectionService,
        valid_params: LDAPConnectionParams,
    ) -> None:
        """Test connection testing."""
        create_result = await service.create_connection(valid_params)
        connection_id = create_result.data.id

        test_result = await service.test_connection(connection_id)

        assert test_result.success
        # Connection should have updated timestamp
        connection = service._connections[connection_id]
        assert connection.last_tested is not None

    async def test_test_nonexistent_connection(
        self,
        service: LDAPConnectionService,
    ) -> None:
        """Test testing non-existent connection."""
        result = await service.test_connection(uuid4())

        assert result.is_failure
        assert "Connection not found" in result.error


class TestLDAPStreamService:
    """Test LDAP stream service."""

    @pytest.fixture
    def service(self) -> LDAPStreamService:
        """Create stream service instance."""
        return LDAPStreamService()

    async def test_create_stream_success(self, service: LDAPStreamService) -> None:
        """Test successful stream creation."""
        connection_id = uuid4()
        params = StreamCreationParams(
            connection_id=connection_id,
            stream_type="users",
            search_filter="(objectClass=inetOrgPerson)",
            attributes=["uid", "cn", "mail"],
        )
        result = await service.create_stream(params)

        assert result.success
        assert result.data.connection_id == connection_id
        assert result.data.stream_type == "users"
        assert result.data.search_filter == "(objectClass=inetOrgPerson)"

    async def test_create_stream_with_defaults(
        self,
        service: LDAPStreamService,
    ) -> None:
        """Test stream creation with default values."""
        connection_id = uuid4()
        params = StreamCreationParams(
            connection_id=connection_id,
            stream_type="users",
            search_filter="(objectClass=inetOrgPerson)",
        )
        result = await service.create_stream(params)

        assert result.success
        assert result.data.tap_stream_id == "users_stream"
        assert result.data.key_properties == ["dn"]
        assert result.data.replication_method == "FULL_TABLE"

    async def test_discover_schema(self, service: LDAPStreamService) -> None:
        """Test schema discovery."""
        connection_id = uuid4()
        params = StreamCreationParams(
            connection_id=connection_id,
            stream_type="users",
            search_filter="(objectClass=inetOrgPerson)",
        )
        create_result = await service.create_stream(params)
        stream_id = create_result.data.id

        schema_result = await service.discover_schema(stream_id)

        assert schema_result.success
        assert "type" in schema_result.data
        assert "properties" in schema_result.data
        assert "dn" in schema_result.data["properties"]

    async def test_list_streams_filtered(self, service: LDAPStreamService) -> None:
        """Test listing streams filtered by connection."""
        connection_id1 = uuid4()
        connection_id2 = uuid4()

        await service.create_stream(
            StreamCreationParams(connection_id1, "users", "(objectClass=person)"),
        )
        await service.create_stream(
            StreamCreationParams(connection_id1, "groups", "(objectClass=group)"),
        )
        await service.create_stream(
            StreamCreationParams(connection_id2, "users", "(objectClass=person)"),
        )

        # List all streams
        all_result = await service.list_streams()
        assert len(all_result.data) == 3

        # List streams for connection 1
        filtered_result = await service.list_streams(connection_id1)
        assert len(filtered_result.data) == 2


class TestTapExecutionService:
    """Test tap execution service."""

    @pytest.fixture
    def service(self) -> TapExecutionService:
        """Create execution service instance."""
        return TapExecutionService()

    async def test_create_execution(self, service: TapExecutionService) -> None:
        """Test execution creation."""
        connection_id = uuid4()
        result = await service.create_execution(
            connection_id=connection_id,
            command="discover",
            config={"ldap_host": "localhost"},
        )

        assert result.success
        assert result.data.connection_id == connection_id
        assert result.data.command == "discover"
        assert result.data.tap_status == "created"

    async def test_start_execution(self, service: TapExecutionService) -> None:
        """Test starting execution."""
        connection_id = uuid4()
        create_result = await service.create_execution(connection_id, "sync")
        execution_id = create_result.data.id

        start_result = await service.start_execution(execution_id)

        assert start_result.success
        assert start_result.data.tap_status == "discovering"
        assert start_result.data.started_at is not None

    async def test_complete_execution(self, service: TapExecutionService) -> None:
        """Test completing execution."""
        connection_id = uuid4()
        create_result = await service.create_execution(connection_id, "sync")
        execution_id = create_result.data.id

        await service.start_execution(execution_id)
        complete_result = await service.complete_execution(
            execution_id,
            exit_code=0,
            stdout="Success",
        )

        assert complete_result.success
        assert complete_result.data.tap_status == "completed"
        assert complete_result.data.exit_code == 0

    async def test_update_metrics(self, service: TapExecutionService) -> None:
        """Test updating execution metrics."""
        connection_id = uuid4()
        create_result = await service.create_execution(connection_id, "sync")
        execution_id = create_result.data.id

        metrics_result = await service.update_metrics(
            execution_id,
            records_extracted=100,
            streams_processed=3,
        )

        assert metrics_result.success
        assert metrics_result.data.records_extracted == 100
        assert metrics_result.data.streams_processed == 3


class TestLDAPRecordService:
    """Test LDAP record service."""

    @pytest.fixture
    def service(self) -> LDAPRecordService:
        """Create record service instance."""
        return LDAPRecordService()

    async def test_create_record(self, service: LDAPRecordService) -> None:
        """Test record creation."""
        stream_id = uuid4()
        execution_id = uuid4()

        result = await service.create_record(
            stream_id=stream_id,
            execution_id=execution_id,
            dn="uid=jdoe,ou=users,dc=test,dc=com",
            attributes={"uid": "jdoe", "cn": "John Doe"},
            object_class=["inetOrgPerson"],
        )

        assert result.success
        assert result.data.dn == "uid=jdoe,ou=users,dc=test,dc=com"
        assert result.data.attributes["uid"] == "jdoe"
        assert "singer_record" in result.data.__dict__

    async def test_list_records_filtered(self, service: LDAPRecordService) -> None:
        """Test listing records with filters."""
        stream_id1 = uuid4()
        stream_id2 = uuid4()
        execution_id = uuid4()

        # Create records for different streams
        await service.create_record(stream_id1, execution_id, "uid=user1,dc=test", {})
        await service.create_record(stream_id1, execution_id, "uid=user2,dc=test", {})
        await service.create_record(stream_id2, execution_id, "uid=user3,dc=test", {})

        # List all records
        all_result = await service.list_records()
        assert len(all_result.data) == 3

        # List records for stream 1
        filtered_result = await service.list_records(stream_id=stream_id1)
        assert len(filtered_result.data) == 2

    async def test_count_records(self, service: LDAPRecordService) -> None:
        """Test counting records."""
        stream_id = uuid4()
        execution_id = uuid4()

        # Create some records
        await service.create_record(stream_id, execution_id, "uid=user1,dc=test", {})
        await service.create_record(stream_id, execution_id, "uid=user2,dc=test", {})

        count_result = await service.count_records(stream_id=stream_id)

        assert count_result.success
        assert count_result.value == 2
