"""LDAP tap exception hierarchy using flext-core Singer base patterns.

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT

Domain-specific exceptions for LDAP tap operations inheriting from Singer base classes.
Eliminates duplication by using centralized Singer exception patterns from flext-core.
"""

from __future__ import annotations

from flext_core import (
    FlextSingerAuthenticationError,
    FlextSingerConfigurationError,
    FlextSingerConnectionError,
    FlextSingerProcessingError,
    FlextSingerValidationError,
    FlextTapError,
)


class _FlextTapLdapErrorMixin:
    """Mixin for LDAP tap errors to eliminate code duplication.

    Implements Single Responsibility Principle by handling only context building.
    Follows DRY principle by centralizing common initialization logic.
    """

    def _build_ldap_context(
        self,
        kwargs: dict[str, object],
        **specific_params: object,
    ) -> dict[str, object]:
        """Build context dict with LDAP-specific parameters.

        Args:
            kwargs: Base kwargs from caller
            **specific_params: LDAP-specific parameters to add to context

        Returns:
            Context dictionary with non-None parameters added

        """
        context = kwargs.copy()
        for param_name, param_value in specific_params.items():
            if param_value is not None:
                context[param_name] = param_value
        return context

    def _format_ldap_message(self, base_message: str, prefix: str) -> str:
        """Format LDAP error message with consistent prefix.

        Args:
            base_message: The base error message
            prefix: LDAP-specific prefix (e.g., 'connection', 'auth')

        Returns:
            Formatted message with LDAP tap prefix

        """
        return f"LDAP tap {prefix}: {base_message}"

    def _initialize_ldap_error(
        self,
        message: str,
        prefix: str,
        stream_name: str | None = None,
        kwargs: dict[str, object] | None = None,
        **specific_params: object,
    ) -> tuple[str, dict[str, object]]:
        """Common initialization for LDAP errors to eliminate code duplication.

        Single Responsibility: Handle common initialization pattern.
        Follows DRY principle by centralizing initialization logic.

        Args:
            message: Base error message
            prefix: LDAP-specific prefix for message formatting
            stream_name: Optional stream name
            kwargs: Optional additional kwargs dict
            **specific_params: LDAP-specific parameters

        Returns:
            Tuple of (formatted_message, context_dict) for super().__init__()

        """
        formatted_message = self._format_ldap_message(message, prefix)

        # Handle kwargs if provided
        base_kwargs = kwargs or {}
        context = self._build_ldap_context(base_kwargs, **specific_params)

        return formatted_message, {
            "component_type": "tap",
            "stream_name": stream_name,
            **context,
        }


class FlextTapLdapError(FlextTapError, _FlextTapLdapErrorMixin):
    """Base exception for LDAP tap operations."""

    def __init__(
        self,
        message: str = "LDAP tap error",
        ldap_server: str | None = None,
        stream_name: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize LDAP tap error with context using Template Method Pattern."""
        formatted_message, init_kwargs = self._initialize_ldap_error(
            message=message,
            prefix="operation",
            stream_name=stream_name,
            kwargs=dict(kwargs),
            ldap_server=ldap_server,
        )

        # Add specific FlextTapError requirements
        init_kwargs["source_system"] = "ldap"
        super().__init__(formatted_message, **init_kwargs)


class FlextTapLdapConnectionError(FlextSingerConnectionError, _FlextTapLdapErrorMixin):
    """LDAP tap connection errors."""

    def __init__(
        self,
        message: str = "LDAP tap connection failed",
        ldap_server: str | None = None,
        port: int | None = None,
        stream_name: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize LDAP tap connection error with context using Template Method Pattern."""
        formatted_message, init_kwargs = self._initialize_ldap_error(
            message=message,
            prefix="connection",
            stream_name=stream_name,
            kwargs=dict(kwargs),
            ldap_server=ldap_server,
            port=port,
        )

        super().__init__(formatted_message, **init_kwargs)


class FlextTapLdapAuthenticationError(
    FlextSingerAuthenticationError,
    _FlextTapLdapErrorMixin,
):
    """LDAP tap authentication errors."""

    def __init__(
        self,
        message: str = "LDAP tap authentication failed",
        bind_dn: str | None = None,
        stream_name: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize LDAP tap authentication error with context."""
        formatted_message, init_kwargs = self._initialize_ldap_error(
            message=message,
            prefix="auth",
            stream_name=stream_name,
            kwargs=dict(kwargs),
            bind_dn=bind_dn,
        )

        super().__init__(formatted_message, **init_kwargs)


class FlextTapLdapValidationError(FlextSingerValidationError, _FlextTapLdapErrorMixin):
    """LDAP tap validation errors."""

    def __init__(
        self,
        message: str = "LDAP tap validation failed",
        field: str | None = None,
        value: object = None,
        entry_dn: str | None = None,
        stream_name: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize LDAP tap validation error with context."""
        # Build validation details separately as required by parent class
        validation_details: dict[str, object] = {}
        if field is not None:
            validation_details["field"] = field
        if value is not None:
            validation_details["value"] = str(value)[:100]  # Truncate long values

        formatted_message, init_kwargs = self._initialize_ldap_error(
            message=message,
            prefix="validation",
            stream_name=stream_name,
            kwargs=dict(kwargs),
            entry_dn=entry_dn,
        )

        # Add validation-specific details
        init_kwargs["validation_details"] = validation_details
        super().__init__(formatted_message, **init_kwargs)


class FlextTapLdapConfigurationError(
    FlextSingerConfigurationError,
    _FlextTapLdapErrorMixin,
):
    """LDAP tap configuration errors."""

    def __init__(
        self,
        message: str = "LDAP tap configuration error",
        config_key: str | None = None,
        stream_name: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize LDAP tap configuration error with context."""
        formatted_message, init_kwargs = self._initialize_ldap_error(
            message=message,
            prefix="config",
            stream_name=stream_name,
            kwargs=dict(kwargs),
            config_key=config_key,
        )

        super().__init__(formatted_message, **init_kwargs)


class FlextTapLdapProcessingError(FlextSingerProcessingError, _FlextTapLdapErrorMixin):
    """LDAP tap processing errors."""

    def __init__(
        self,
        message: str = "LDAP tap processing failed",
        stream_name: str | None = None,
        record_number: int | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize LDAP tap processing error with context."""
        formatted_message, init_kwargs = self._initialize_ldap_error(
            message=message,
            prefix="processing",
            stream_name=stream_name,
            kwargs=dict(kwargs),
            record_number=record_number,
        )

        super().__init__(formatted_message, **init_kwargs)


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
        context = self._build_ldap_context(
            dict(kwargs),
            search_base=search_base,
            search_filter=search_filter,
        )

        super().__init__(
            self._format_ldap_message(message, "search"),
            ldap_server=None,
            stream_name=None,
            **context,
        )


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
        context = self._build_ldap_context(dict(kwargs), stream_type=stream_type)

        super().__init__(
            self._format_ldap_message(message, "stream"),
            ldap_server=None,
            stream_name=stream_name,
            **context,
        )


__all__: list[str] = [
    "FlextTapLdapAuthenticationError",
    "FlextTapLdapConfigurationError",
    "FlextTapLdapConnectionError",
    "FlextTapLdapError",
    "FlextTapLdapProcessingError",
    "FlextTapLdapSearchError",
    "FlextTapLdapStreamError",
    "FlextTapLdapValidationError",
]
