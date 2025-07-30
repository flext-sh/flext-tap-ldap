"""LDAP tap exception hierarchy using flext-core patterns.

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT

Domain-specific exceptions for LDAP tap operations inheriting from flext-core.
"""

from __future__ import annotations

from flext_core.exceptions import (
    FlextAuthenticationError,
    FlextConfigurationError,
    FlextConnectionError,
    FlextError,
    FlextProcessingError,
    FlextValidationError,
)


class FlextTapLdapError(FlextError):
    """Base exception for LDAP tap operations."""

    def __init__(
        self,
        message: str = "LDAP tap error",
        stream_name: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize LDAP tap error with context."""
        context = kwargs.copy()
        if stream_name is not None:
            context["stream_name"] = stream_name

        super().__init__(message, error_code="LDAP_TAP_ERROR", context=context)


class FlextTapLdapConnectionError(FlextConnectionError):
    """LDAP tap connection errors."""

    def __init__(
        self,
        message: str = "LDAP tap connection failed",
        ldap_server: str | None = None,
        port: int | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize LDAP tap connection error with context."""
        context = kwargs.copy()
        if ldap_server is not None:
            context["ldap_server"] = ldap_server
        if port is not None:
            context["port"] = port

        super().__init__(f"LDAP tap connection: {message}", **context)


class FlextTapLdapAuthenticationError(FlextAuthenticationError):
    """LDAP tap authentication errors."""

    def __init__(
        self,
        message: str = "LDAP tap authentication failed",
        bind_dn: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize LDAP tap authentication error with context."""
        context = kwargs.copy()
        if bind_dn is not None:
            context["bind_dn"] = bind_dn

        super().__init__(f"LDAP tap auth: {message}", **context)


class FlextTapLdapValidationError(FlextValidationError):
    """LDAP tap validation errors."""

    def __init__(
        self,
        message: str = "LDAP tap validation failed",
        field: str | None = None,
        value: object = None,
        entry_dn: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize LDAP tap validation error with context."""
        validation_details: dict[str, object] = {}
        if field is not None:
            validation_details["field"] = field
        if value is not None:
            validation_details["value"] = str(value)[:100]  # Truncate long values

        context = kwargs.copy()
        if entry_dn is not None:
            context["entry_dn"] = entry_dn

        super().__init__(
            f"LDAP tap validation: {message}",
            validation_details=validation_details,
            context=context,
        )


class FlextTapLdapConfigurationError(FlextConfigurationError):
    """LDAP tap configuration errors."""

    def __init__(
        self,
        message: str = "LDAP tap configuration error",
        config_key: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize LDAP tap configuration error with context."""
        context = kwargs.copy()
        if config_key is not None:
            context["config_key"] = config_key

        super().__init__(f"LDAP tap config: {message}", **context)


class FlextTapLdapProcessingError(FlextProcessingError):
    """LDAP tap processing errors."""

    def __init__(
        self,
        message: str = "LDAP tap processing failed",
        stream_name: str | None = None,
        record_number: int | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize LDAP tap processing error with context."""
        context = kwargs.copy()
        if stream_name is not None:
            context["stream_name"] = stream_name
        if record_number is not None:
            context["record_number"] = record_number

        super().__init__(f"LDAP tap processing: {message}", **context)


class FlextTapLdapSearchError(FlextTapLdapError):
    """LDAP tap search operation errors."""

    def __init__(
        self,
        message: str = "LDAP tap search failed",
        search_base: str | None = None,
        search_filter: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize LDAP tap search error with context."""
        context = kwargs.copy()
        if search_base is not None:
            context["search_base"] = search_base
        if search_filter is not None:
            context["search_filter"] = search_filter

        super().__init__(f"LDAP tap search: {message}", stream_name=None, **context)


class FlextTapLdapStreamError(FlextTapLdapError):
    """LDAP tap stream processing errors."""

    def __init__(
        self,
        message: str = "LDAP tap stream error",
        stream_name: str | None = None,
        stream_type: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize LDAP tap stream error with context."""
        context = kwargs.copy()
        if stream_name is not None:
            context["stream_name"] = stream_name
        if stream_type is not None:
            context["stream_type"] = stream_type

        super().__init__(
            f"LDAP tap stream: {message}", stream_name=stream_name, **context,
        )


__all__ = [
    "FlextTapLdapAuthenticationError",
    "FlextTapLdapConfigurationError",
    "FlextTapLdapConnectionError",
    "FlextTapLdapError",
    "FlextTapLdapProcessingError",
    "FlextTapLdapSearchError",
    "FlextTapLdapStreamError",
    "FlextTapLdapValidationError",
]
