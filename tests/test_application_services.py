"""Tests for application services layer.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from uuid import uuid4

import pytest

from flext_tap_ldap.tap_services import FlextMeltanoTapLdapServices


class TestLDAPConnectionParams:
    """Test FlextMeltanoTapLdapServices.LDAPConnectionParams parameter object."""

    def test_valid_params_creation(self) -> None:
        """Test method."""
        """Test creating valid connection parameters."""
        params = FlextMeltanoTapLdapServices.LDAPConnectionParams(
            host="localhost",
            base_dn="dc=test,dc=com",
            port=389,
            bind_dn="cn=REDACTED_LDAP_BIND_PASSWORD,dc=test,dc=com",
            bind_password="password",
        )

        assert params.host == "localhost"
        assert params.port == 389
        assert params.bind_dn == "cn=REDACTED_LDAP_BIND_PASSWORD,dc=test,dc=com"
        assert params.bind_password == "password"
        assert params.use_ssl is False

    def test_invalid_host_validation(self) -> None:
        """Test method."""
        """Test host validation."""
        with pytest.raises(ValueError, match="Host is required"):
            FlextMeltanoTapLdapServices.LDAPConnectionParams(
                host="", base_dn="dc=test,dc=com", port=389
            )

    def test_invalid_port_validation(self) -> None:
        """Test method."""
        """Test port validation."""
        with pytest.raises(ValueError, match="Port must be between 1 and 65535"):
            FlextMeltanoTapLdapServices.LDAPConnectionParams(
                host="localhost", base_dn="dc=test,dc=com", port=0
            )

        with pytest.raises(ValueError, match="Port must be between 1 and 65535"):
            FlextMeltanoTapLdapServices.LDAPConnectionParams(
                host="localhost", base_dn="dc=test,dc=com", port=70000
            )

    def test_invalid_timeout_validation(self) -> None:
        """Test method."""
        """Test timeout validation."""
        with pytest.raises(ValueError, match="Timeout must be positive"):
            FlextMeltanoTapLdapServices.LDAPConnectionParams(
                host="localhost", base_dn="dc=test,dc=com", timeout_seconds=0
            )

    def test_invalid_page_size_validation(self) -> None:
        """Test method."""
        """Test page size validation."""
        with pytest.raises(ValueError, match="Page size must be positive"):
            FlextMeltanoTapLdapServices.LDAPConnectionParams(
                host="localhost", base_dn="dc=test,dc=com", page_size=0
            )

    def test_invalid_max_retries_validation(self) -> None:
        """Test method."""
        """Test max retries validation."""
        with pytest.raises(ValueError, match="Max retries cannot be negative"):
            FlextMeltanoTapLdapServices.LDAPConnectionParams(
                host="localhost", base_dn="dc=test,dc=com", max_retries=-1
            )


class TestLDAPConnectionService:
    """Test LDAP connection service."""

    @pytest.fixture
    def service(self) -> FlextMeltanoTapLdapServices.LDAPConnectionService:
        """Create connection service instance."""
        return FlextMeltanoTapLdapServices.LDAPConnectionService()

    @pytest.fixture
    def valid_params(self) -> FlextMeltanoTapLdapServices.LDAPConnectionParams:
        """Create valid connection parameters."""
        return FlextMeltanoTapLdapServices.LDAPConnectionParams(
            host="localhost",
            base_dn="dc=test,dc=com",
            port=389,
            bind_dn="cn=REDACTED_LDAP_BIND_PASSWORD,dc=test,dc=com",
            bind_password="password",
        )

    def test_create_connection_success(
        self,
        service: FlextMeltanoTapLdapServices.LDAPConnectionService,
        valid_params: FlextMeltanoTapLdapServices.LDAPConnectionParams,
    ) -> None:
        """Test successful connection creation."""
        result = service.create_connection(
            FlextMeltanoTapLdapServices.LDAPConnectionParams(
                host=valid_params.host,
                base_dn=valid_params.base_dn,
                port=valid_params.port,
                bind_dn=valid_params.bind_dn,
                bind_password=valid_params.bind_password,
            )
        )

        assert result.is_success
        assert result.data is not None
        # Verify connection is stored
        assert len(service._connections) == 1

    def test_create_connection_stores_multiple(
        self,
        service: FlextMeltanoTapLdapServices.LDAPConnectionService,
        valid_params: FlextMeltanoTapLdapServices.LDAPConnectionParams,
    ) -> None:
        """Test creating multiple connections."""
        result1 = service.create_connection(
            FlextMeltanoTapLdapServices.LDAPConnectionParams(
                host=valid_params.host,
                base_dn=valid_params.base_dn,
                port=valid_params.port,
                bind_dn=valid_params.bind_dn,
                bind_password=valid_params.bind_password,
            )
        )
        result2 = service.create_connection(
            FlextMeltanoTapLdapServices.LDAPConnectionParams(
                host=valid_params.host,
                base_dn=valid_params.base_dn,
                port=valid_params.port,
                bind_dn=valid_params.bind_dn,
                bind_password=valid_params.bind_password,
            )
        )

        assert result1.is_success
        assert result2.is_success
        assert len(service._connections) == 2
        assert result1.data.id != result2.data.id

    def test_get_connection_success(
        self,
        service: FlextMeltanoTapLdapServices.LDAPConnectionService,
        valid_params: FlextMeltanoTapLdapServices.LDAPConnectionParams,
    ) -> None:
        """Test getting existing connection."""
        create_result = service.create_connection(valid_params)
        connection_id = create_result.data.id

        get_result = service.get_connection(connection_id)

        assert get_result.is_success
        assert get_result.data is not None
        assert get_result.data.id == connection_id

    def test_get_nonexistent_connection(
        self,
        service: FlextMeltanoTapLdapServices.LDAPConnectionService,
    ) -> None:
        """Test getting non-existent connection."""
        result = service.get_connection("non-existent-id")

        assert result.is_failure
        assert result.error is not None
        assert "Connection not found" in result.error

    def test_list_connections_empty(
        self,
        service: FlextMeltanoTapLdapServices.LDAPConnectionService,
    ) -> None:
        """Test listing connections when empty."""
        result = service.list_connections()

        assert result.is_success
        assert result.data == []

    def test_list_connections_with_data(
        self,
        service: FlextMeltanoTapLdapServices.LDAPConnectionService,
        valid_params: FlextMeltanoTapLdapServices.LDAPConnectionParams,
    ) -> None:
        """Test listing connections with data."""
        service.create_connection(
            FlextMeltanoTapLdapServices.LDAPConnectionParams(
                host=valid_params.host,
                base_dn=valid_params.base_dn,
                port=valid_params.port,
                bind_dn=valid_params.bind_dn,
                bind_password=valid_params.bind_password,
            )
        )
        service.create_connection(
            FlextMeltanoTapLdapServices.LDAPConnectionParams(
                host=valid_params.host,
                base_dn=valid_params.base_dn,
                port=valid_params.port,
                bind_dn=valid_params.bind_dn,
                bind_password=valid_params.bind_password,
            )
        )

        result = service.list_connections()

        assert result.is_success
        assert len(result.data) == 2

    def test_test_connection_success(
        self,
        service: FlextMeltanoTapLdapServices.LDAPConnectionService,
        valid_params: FlextMeltanoTapLdapServices.LDAPConnectionParams,
    ) -> None:
        """Test connection testing."""
        create_result = service.create_connection(
            FlextMeltanoTapLdapServices.LDAPConnectionParams(
                host=valid_params.host,
                base_dn=valid_params.base_dn,
                port=valid_params.port,
                bind_dn=valid_params.bind_dn,
                bind_password=valid_params.bind_password,
            )
        )
        connection_id = str(create_result.data.id)

        test_result = service.test_connection(connection_id)

        assert test_result.is_success
        # Connection should have updated timestamp
        connection = service._connections[connection_id]
        assert connection.last_tested is not None

    def test_test_nonexistent_connection(
        self,
        service: FlextMeltanoTapLdapServices.LDAPConnectionService,
    ) -> None:
        """Test testing non-existent connection."""
        result = service.test_connection("non-existent-id")

        assert result.is_failure
        assert result.error is not None
        assert result.error is not None and "Connection not found" in result.error


class TestLDAPStreamService:
    """Test LDAP stream service."""

    @pytest.fixture
    def service(self) -> FlextMeltanoTapLdapServices.LDAPStreamService:
        """Create stream service instance."""
        return FlextMeltanoTapLdapServices.LDAPStreamService()

    def test_create_stream_with_attributes(
        self, service: FlextMeltanoTapLdapServices.LDAPStreamService
    ) -> None:
        """Test successful stream creation with specific attributes."""
        connection_id = str(uuid4())
        params = FlextMeltanoTapLdapServices.StreamCreationParams(
            connection_id=connection_id,
            stream_type="users",
            search_filter="(objectClass=inetOrgPerson)",
            attributes=["uid", "cn", "mail"],
            key_properties=["dn"],
        )
        result = service.create_stream(params)

        assert result.is_success
        assert result.data.connection_id == connection_id
        assert result.data.name == "users"
        assert result.data.search_filter == "(objectClass=inetOrgPerson)"

    def test_create_stream_with_defaults(
        self,
        service: FlextMeltanoTapLdapServices.LDAPStreamService,
    ) -> None:
        """Test stream creation with default values."""
        connection_id = str(uuid4())
        params = FlextMeltanoTapLdapServices.StreamCreationParams(
            connection_id=connection_id,
            stream_type="users",
            search_filter="(objectClass=inetOrgPerson)",
            key_properties=["dn"],
        )
        result = service.create_stream(params)

        assert result.is_success
        assert result.data.tap_stream_id == "users_stream"
        assert result.data.key_properties == ["dn"]
        assert result.data.replication_method == "FULL_TABLE"

    def test_schema_discovery(
        self, service: FlextMeltanoTapLdapServices.LDAPStreamService
    ) -> None:
        """Test schema discovery functionality."""
        connection_id = str(uuid4())
        params = FlextMeltanoTapLdapServices.StreamCreationParams(
            connection_id=connection_id,
            stream_type="users",
            search_filter="(objectClass=inetOrgPerson)",
            key_properties=["dn"],
        )
        create_result = service.create_stream(params)
        stream_id = str(create_result.data.id)

        schema_result = service.discover_schema(stream_id)

        assert schema_result.is_success
        assert schema_result.data is not None
        assert "type" in schema_result.data
        assert "properties" in schema_result.data
        properties = schema_result.data["properties"]
        assert isinstance(properties, dict)
        assert "dn" in properties

    def test_self(self, service: FlextMeltanoTapLdapServices.LDAPStreamService) -> None:
        """Test method."""
        """Test listing streams filtered by connection."""
        connection_id1 = str(uuid4())
        connection_id2 = str(uuid4())

        service.create_stream(
            FlextMeltanoTapLdapServices.StreamCreationParams(
                connection_id=connection_id1,
                stream_type="users",
                search_filter="(objectClass=person)",
                key_properties=["dn"],
            ),
        )
        service.create_stream(
            FlextMeltanoTapLdapServices.StreamCreationParams(
                connection_id=connection_id1,
                stream_type="groups",
                search_filter="(objectClass=group)",
                key_properties=["dn"],
            ),
        )
        service.create_stream(
            FlextMeltanoTapLdapServices.StreamCreationParams(
                connection_id=connection_id2,
                stream_type="users",
                search_filter="(objectClass=person)",
                key_properties=["dn"],
            ),
        )

        # List all streams
        all_result = service.list_streams()
        assert len(all_result.data) == 3

        # List streams for connection 1
        filtered_result = service.list_streams(connection_id1)
        assert len(filtered_result.data) == 2


class TestTapExecutionService:
    """Test tap execution service."""

    @pytest.fixture
    def service(self) -> FlextMeltanoTapLdapServices.TapExecutionService:
        """Create execution service instance."""
        return FlextMeltanoTapLdapServices.TapExecutionService()

    def test_create_execution(
        self, service: FlextMeltanoTapLdapServices.TapExecutionService
    ) -> None:
        """Test execution creation."""
        connection_id = str(uuid4())
        result = service.create_execution(
            connection_id=connection_id,
            command="discover",
            config={"ldap_host": "localhost"},
        )

        assert result.is_success
        assert result.data.connection_id == connection_id
        assert result.data.command == "discover"
        assert result.data.tap_status == "created"

    def test_start_execution(
        self, service: FlextMeltanoTapLdapServices.TapExecutionService
    ) -> None:
        """Test starting execution."""
        connection_id = str(uuid4())
        create_result = service.create_execution(connection_id, "sync")
        execution_id = create_result.data.id

        start_result = service.start_execution(execution_id)

        assert start_result.is_success
        assert start_result.data.tap_status == "discovering"
        assert start_result.data.started_at is not None

    def test_complete_execution(
        self, service: FlextMeltanoTapLdapServices.TapExecutionService
    ) -> None:
        """Test completing execution."""
        connection_id = str(uuid4())
        create_result = service.create_execution(connection_id, "sync")
        execution_id = create_result.data.id

        service.start_execution(execution_id)
        complete_result = service.complete_execution(
            execution_id,
            exit_code=0,
            stdout="Success",
        )

        assert complete_result.is_success
        assert complete_result.data.tap_status == "completed"
        assert complete_result.data.exit_code == 0

    def test_update_execution_metrics(
        self, service: FlextMeltanoTapLdapServices.TapExecutionService
    ) -> None:
        """Test updating execution metrics."""
        connection_id = str(uuid4())
        create_result = service.create_execution(connection_id, "sync")
        execution_id = create_result.data.id

        metrics_result = service.update_metrics(
            execution_id,
            records_extracted=100,
            streams_processed=3,
        )

        assert metrics_result.is_success
        assert metrics_result.data.records_extracted == 100
        assert metrics_result.data.streams_processed == 3


class TestLDAPRecordService:
    """Test LDAP record service."""

    @pytest.fixture
    def service(self) -> FlextMeltanoTapLdapServices.LDAPRecordService:
        """Create record service instance."""
        return FlextMeltanoTapLdapServices.LDAPRecordService()

    def test_create_record(
        self, service: FlextMeltanoTapLdapServices.LDAPRecordService
    ) -> None:
        """Test record creation."""
        stream_id = str(uuid4())
        execution_id = str(uuid4())

        result = service.create_record(
            stream_id=stream_id,
            execution_id=execution_id,
            dn="uid=jdoe,ou=users,dc=test,dc=com",
            attributes={"uid": "jdoe", "cn": "John Doe"},
            object_class=["inetOrgPerson"],
        )

        assert result.is_success
        assert result.data.record["dn"] == "uid=jdoe,ou=users,dc=test,dc=com"
        assert result.data.record["attributes"]["uid"] == "jdoe"
        assert "id" in result.data.record

    def test_list_records_with_filters(
        self, service: FlextMeltanoTapLdapServices.LDAPRecordService
    ) -> None:
        """Test listing records with filters."""
        stream_id1 = str(uuid4())
        stream_id2 = str(uuid4())
        execution_id = str(uuid4())

        # Create records for different streams
        service.create_record(stream_id1, execution_id, "uid=user1,dc=test", {})
        service.create_record(stream_id1, execution_id, "uid=user2,dc=test", {})
        service.create_record(stream_id2, execution_id, "uid=user3,dc=test", {})

        # List all records
        all_result = service.list_records()
        assert len(all_result.data) == 3

        # List records for stream 1
        filtered_result = service.list_records(stream_id=stream_id1)
        assert len(filtered_result.data) == 2

    def test_count_records(
        self, service: FlextMeltanoTapLdapServices.LDAPRecordService
    ) -> None:
        """Test counting records."""
        stream_id = str(uuid4())
        execution_id = str(uuid4())

        # Create some records
        service.create_record(stream_id, execution_id, "uid=user1,dc=test", {})
        service.create_record(stream_id, execution_id, "uid=user2,dc=test", {})

        count_result = service.count_records(stream_id=stream_id)

        assert count_result.is_success
        assert count_result.value == 2
