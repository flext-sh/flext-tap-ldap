"""FLEXT Tap LDAP Services - UNIFIED service implementation for LDAP tap operations.

This module provides a SINGLE UNIFIED service class for LDAP tap operations
following FLEXT 'one class per module' pattern with nested helper classes.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from uuid import uuid4

from flext_core import (
    FlextConstants,
    FlextResult,
    FlextTypes,
)

from flext_tap_ldap.models import (
    LDAPConnection,
    LDAPStream,
    TapExecution,
)
from flext_tap_ldap.typings import FlextTapLdapTypes
from flext_tap_ldap.utilities import FlextTapLdapUtilities


@dataclass
class LDAPConnectionParams:
    """Parameter object for LDAP connection creation."""

    host: str
    port: int = 389
    bind_dn: str | None = None
    bind_password: str | None = None
    base_dn: str = ""
    use_ssl: bool = False
    use_tls: bool = False
    timeout_seconds: int = 30
    page_size: int = 1000
    max_retries: int = 3

    def __post_init__(self: object) -> None:
        """Validate connection parameters after initialization."""
        if self.port <= 0 or self.port > FlextConstants.Network.MAX_PORT:
            msg = f"Port must be between 1 and 65535, got {self.port}"
            raise ValueError(msg)


@dataclass
class StreamCreationParams:
    """Parameter object for stream creation."""

    stream_name: str
    base_dn: str
    search_filter: str = "(objectClass=*)"
    attributes: list[str] | None = None
    scope: str = "subtree"


class FlextTapLdapServices:
    """UNIFIED LDAP tap services following FLEXT 'one class per module' pattern.

    Consolidates all LDAP service functionality into a single class with nested
    helper classes for connection, streaming, execution, and record operations.
    """

    # ========================================================================
    # NESTED HELPER CLASSES - Connection Services
    # ========================================================================

    class _ConnectionService:
        """Nested helper for LDAP connection operations."""

        def __init__(self) -> None:
            """Initialize connection service."""
            self._logger = FlextTapLdapUtilities.get_logger()

        def create_connection(
            self, params: LDAPConnectionParams
        ) -> FlextResult[LDAPConnection]:
            """Create LDAP connection from parameters."""
            try:
                connection = LDAPConnection(
                    host=params.host,
                    port=params.port,
                    bind_dn=params.bind_dn,
                    bind_password=params.bind_password,
                    base_dn=params.base_dn,
                    use_ssl=params.use_ssl,
                    use_tls=params.use_tls,
                    timeout_seconds=params.timeout_seconds,
                    page_size=params.page_size,
                    max_retries=params.max_retries,
                )
                return FlextResult[LDAPConnection].ok(data=connection)
            except Exception as e:
                return FlextResult[LDAPConnection].fail(
                    f"Failed to create connection: {e}"
                )

        def test_connection(self, _connection: LDAPConnection) -> FlextResult[bool]:  # noqa: PT019
            """Test LDAP connection."""
            try:
                # Implementation would test actual LDAP connection
                return FlextResult[bool].ok(data=True)
            except Exception as e:
                return FlextResult[bool].fail(f"Connection test failed: {e}")

    # ========================================================================
    # NESTED HELPER CLASSES - Stream Services
    # ========================================================================

    class _StreamService:
        """Nested helper for LDAP stream operations."""

        def __init__(self) -> None:
            """Initialize stream service."""
            self._logger = FlextTapLdapUtilities.get_logger()

        def create_stream(
            self, params: StreamCreationParams
        ) -> FlextResult[LDAPStream]:
            """Create LDAP stream from parameters."""
            try:
                stream = LDAPStream(
                    name=params.stream_name,
                    base_dn=params.base_dn,
                    search_filter=params.search_filter,
                    attributes=params.attributes,
                    scope=params.scope,
                )
                return FlextResult[LDAPStream].ok(data=stream)
            except Exception as e:
                return FlextResult[LDAPStream].fail(f"Failed to create stream: {e}")

        def discover_streams(
            self, _connection: LDAPConnection
        ) -> FlextResult[list[LDAPStream]]:
            """Discover available LDAP streams."""
            try:
                # Implementation would discover actual LDAP streams
                streams = [
                    LDAPStream(
                        name="users",
                        base_dn="ou=users,dc=example,dc=com",
                        search_filter="(objectClass=person)",
                        attributes=["cn", "mail", "uid"],
                    )
                ]
                return FlextResult[list[LDAPStream]].ok(data=streams)
            except Exception as e:
                return FlextResult[list[LDAPStream]].fail(
                    f"Stream discovery failed: {e}"
                )

    # ========================================================================
    # NESTED HELPER CLASSES - Execution Services
    # ========================================================================

    class _ExecutionService:
        """Nested helper for tap execution operations."""

        def __init__(self) -> None:
            """Initialize execution service."""
            self._logger = FlextTapLdapUtilities.get_logger()
            self._executions: dict[str, TapExecution] = {}

        def start_execution(
            self,
            _connection: LDAPConnection,
            _streams: list[LDAPStream],
            config: FlextTypes.Dict | None = None,
        ) -> FlextResult[TapExecution]:
            """Start tap execution."""
            try:
                execution = TapExecution(
                    id=str(uuid4()),
                    connection_id=str(uuid4()),
                    command="run",
                    tap_status="running",
                    config=config or {},
                    catalog={},
                    state={},
                )
                self._executions[execution.id] = execution
                return FlextResult[TapExecution].ok(data=execution)
            except Exception as e:
                return FlextResult[TapExecution].fail(f"Failed to start execution: {e}")

        def get_execution_status(self, execution_id: str) -> FlextResult[TapExecution]:
            """Get execution status."""
            execution = self._executions.get(execution_id)
            if not execution:
                return FlextResult[TapExecution].fail(
                    f"Execution {execution_id} not found"
                )
            return FlextResult[TapExecution].ok(data=execution)

    # ========================================================================
    # NESTED HELPER CLASSES - Record Services
    # ========================================================================

    class _RecordService:
        """Nested helper for LDAP record operations."""

        def __init__(self) -> None:
            """Initialize record service."""
            self._logger = FlextTapLdapUtilities.get_logger()

        def extract_records(
            self,
            stream: LDAPStream,
            _connection: LDAPConnection,
            _ldap_filter: str | None = None,
            _base_dn: str | None = None,
            _attributes: FlextTypes.StringList | None = None,
        ) -> FlextResult[Iterable[FlextTapLdapTypes.Core.Dict]]:
            """Extract records from LDAP stream."""
            try:
                # Implementation would extract actual LDAP records
                records = [
                    {
                        "dn": f"uid=user1,{stream.base_dn}",
                        "cn": "User One",
                        "mail": "user1@example.com",
                        "uid": "user1",
                    }
                ]
                return FlextResult[Iterable[FlextTapLdapTypes.Core.Dict]].ok(
                    data=records
                )
            except Exception as e:
                return FlextResult[Iterable[FlextTapLdapTypes.Core.Dict]].fail(
                    f"Record extraction failed: {e}"
                )

    # ========================================================================
    # MAIN UNIFIED CLASS INTERFACE
    # ========================================================================

    def __init__(self) -> None:
        """Initialize unified LDAP tap services."""
        self._connection_service = self._ConnectionService()
        self._stream_service = self._StreamService()
        self._execution_service = self._ExecutionService()
        self._record_service = self._RecordService()

    # Connection operations
    def create_connection(
        self, params: LDAPConnectionParams
    ) -> FlextResult[LDAPConnection]:
        """Create LDAP connection."""
        return self._connection_service.create_connection(params)

    def test_connection(self, connection: LDAPConnection) -> FlextResult[bool]:
        """Test LDAP connection."""
        return self._connection_service.test_connection(connection)

    # Stream operations
    def create_stream(self, params: StreamCreationParams) -> FlextResult[LDAPStream]:
        """Create LDAP stream."""
        return self._stream_service.create_stream(params)

    def discover_streams(
        self, connection: LDAPConnection
    ) -> FlextResult[list[LDAPStream]]:
        """Discover LDAP streams."""
        return self._stream_service.discover_streams(connection)

    # Execution operations
    def start_execution(
        self,
        connection: LDAPConnection,
        streams: list[LDAPStream],
        config: FlextTypes.Dict | None = None,
    ) -> FlextResult[TapExecution]:
        """Start tap execution."""
        return self._execution_service.start_execution(connection, streams, config)

    def get_execution_status(self, execution_id: str) -> FlextResult[TapExecution]:
        """Get execution status."""
        return self._execution_service.get_execution_status(execution_id)

    # Record operations
    def extract_records(
        self,
        stream: LDAPStream,
        connection: LDAPConnection,
        ldap_filter: str | None = None,
        base_dn: str | None = None,
        attributes: FlextTypes.StringList | None = None,
    ) -> FlextResult[Iterable[FlextTapLdapTypes.Core.Dict]]:
        """Extract records from LDAP stream."""
        return self._record_service.extract_records(
            stream, connection, ldap_filter, base_dn, attributes
        )


# Aliases for backward compatibility
LDAPConnectionService = FlextTapLdapServices
LDAPRecordService = FlextTapLdapServices
LDAPStreamService = FlextTapLdapServices
TapExecutionService = FlextTapLdapServices


__all__ = [
    "FlextTapLdapServices",
    "LDAPConnectionParams",
    "LDAPConnectionService",
    "LDAPRecordService",
    "LDAPStreamService",
    "StreamCreationParams",
    "TapExecutionService",
]
