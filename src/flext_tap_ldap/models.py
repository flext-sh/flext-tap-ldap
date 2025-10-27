"""FLEXT Tap LDAP models - tap-specific events only.

Uses models from parent libraries (flext-ldap, flext-ldif).
Defines only tap-execution and event models specific to LDAP data extraction.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from datetime import UTC, datetime

from flext_core import FlextModels
from pydantic import BaseModel, Field


class FlextTapLdapModels(FlextModels):
    """Tap-specific event models for LDAP extraction.

    Only contains Singer tap execution events.
    LDAP directory models are inherited from flext-ldap.
    LDIF processing models are inherited from flext-ldif.
    """

    class TapExecutionStartedEvent(DomainEvent):
        """Event raised when tap execution starts."""

        timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
        tap_name: str = "tap-ldap"
        execution_id: str
        config_hash: str | None = None

        def __init__(
            self,
            event_type: str,
            aggregate_id: str,
            execution_id: str,
            config: dict[str, object] | None = None,
            config_hash: str | None = None,
            **kwargs: object,
        ) -> None:
            """Initialize with config data."""
            super().__init__(
                event_type=event_type,
                aggregate_id=aggregate_id,
                data={"config": config} if config else {},
                **kwargs,
            )
            self.execution_id = execution_id
            self.config_hash = config_hash

        @property
        def config(self) -> dict[str, object] | None:
            """Get config from data field."""
            return self.data.get("config")

    class TapExecutionCompletedEvent(DomainEvent):
        """Event raised when tap execution completes."""

        timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
        tap_name: str = "tap-ldap"
        execution_id: str
        records_processed: int = 0
        streams_discovered: int = 0
        duration_seconds: float = 0.0

        def __init__(
            self,
            event_type: str,
            aggregate_id: str,
            execution_id: str,
            records_processed: int = 0,
            streams_discovered: int = 0,
            duration_seconds: float = 0.0,
            **kwargs: object,
        ) -> None:
            """Initialize with execution data."""
            super().__init__(
                event_type=event_type,
                aggregate_id=aggregate_id,
                data={
                    "records_processed": records_processed,
                    "streams_discovered": streams_discovered,
                    "duration_seconds": duration_seconds,
                },
                **kwargs,
            )
            self.execution_id = execution_id
            self.records_processed = records_processed
            self.streams_discovered = streams_discovered
            self.duration_seconds = duration_seconds

        @property
        def records_extracted(self) -> int:
            """Alias for records_processed for backward compatibility."""
            return self.records_processed

        @property
        def duration(self) -> float:
            """Alias for duration_seconds for backward compatibility."""
            return self.duration_seconds

    class StreamDiscoveredEvent(BaseModel):
        """Event raised when a stream is discovered."""

        timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
        stream_name: str
        stream_key_properties: list[str] = Field(default_factory=list)
        bookmark_key: str | None = None

    class RecordExtractedEvent(BaseModel):
        """Event raised when a record is extracted."""

        timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
        stream_name: str
        record_id: str | None = None
        record_size_bytes: int = 0

    class ConnectionTestedEvent(BaseModel):
        """Event raised after connection test."""

        timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
        success: bool
        server_uri: str
        error_message: str | None = None


__all__: list[str] = [
    "FlextTapLdapModels",
]
