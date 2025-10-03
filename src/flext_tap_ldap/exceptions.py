"""Domain-specific exceptions for LDAP tap operations using FlextExceptions patterns.

LDAP Tap Exception Hierarchy using flext-core FlextExceptions patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import override

from flext_core import FlextExceptions, FlextTypes
from flext_tap_ldap.typings import FlextTapLdapTypes


# LDAP Tap specific exceptions using FlextExceptions base patterns
class FlextTapLdapError(FlextExceptions.BaseError):
    """Base LDAP tap error."""

    @override
    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        context: FlextTypes.Dict | None = None,
        correlation_id: str | None = None,
    ) -> None:
        """Initialize base LDAP tap error."""
        super().__init__(
            message,
            code=code,
            context=context,
            correlation_id=correlation_id,
        )


class FlextTapLdapValidationError(FlextExceptions.BaseError):
    """LDAP tap validation error."""

    @override
    def __init__(
        self,
        message: str,
        *,
        field: str | None = None,
        value: object | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize LDAP tap validation error."""
        # Store field and value before extracting common kwargs
        self.field = field
        self.value = value

        # Extract common parameters using helper
        base_context, correlation_id, error_code = self._extract_common_kwargs(kwargs)

        # Build context with validation-specific fields
        context = self._build_context(
            base_context,
            field=field,
            value=value,
        )

        # Call parent with complete error information
        super().__init__(
            message,
            code=error_code or "TAP_LDAP_VALIDATION_ERROR",
            context=context,
            correlation_id=correlation_id,
        )


class FlextTapLdapConfigurationError(FlextExceptions.BaseError):
    """LDAP tap configuration error."""

    @override
    def __init__(
        self,
        message: str,
        **kwargs: object,
    ) -> None:
        """Initialize LDAP tap configuration error."""
        # Extract common parameters using helper
        base_context, correlation_id, error_code = self._extract_common_kwargs(kwargs)

        # Build context (configuration errors use base context only)
        context = self._build_context(base_context)

        # Call parent with complete error information
        super().__init__(
            message,
            code=error_code or "TAP_LDAP_CONFIGURATION_ERROR",
            context=context,
            correlation_id=correlation_id,
        )


class FlextTapLdapProcessingError(FlextExceptions.BaseError):
    """LDAP tap processing error."""

    @override
    def __init__(
        self,
        message: str,
        **kwargs: object,
    ) -> None:
        """Initialize LDAP tap processing error."""
        # Extract common parameters using helper
        base_context, correlation_id, error_code = self._extract_common_kwargs(kwargs)

        # Build context (processing errors use base context only)
        context = self._build_context(base_context)

        # Call parent with complete error information
        super().__init__(
            message,
            code=error_code or "TAP_LDAP_PROCESSING_ERROR",
            context=context,
            correlation_id=correlation_id,
        )


class FlextTapLdapConnectionError(FlextExceptions.BaseError):
    """LDAP tap connection error."""

    @override
    def __init__(
        self,
        message: str,
        **kwargs: object,
    ) -> None:
        """Initialize LDAP tap connection error."""
        # Extract common parameters using helper
        base_context, correlation_id, error_code = self._extract_common_kwargs(kwargs)

        # Build context (connection errors use base context only)
        context = self._build_context(base_context)

        # Call parent with complete error information
        super().__init__(
            message,
            code=error_code or "TAP_LDAP_CONNECTION_ERROR",
            context=context,
            correlation_id=correlation_id,
        )


class FlextTapLdapAuthenticationError(FlextExceptions.BaseError):
    """LDAP tap authentication error."""

    @override
    def __init__(
        self,
        message: str,
        **kwargs: object,
    ) -> None:
        """Initialize LDAP tap authentication error."""
        # Extract common parameters using helper
        base_context, correlation_id, error_code = self._extract_common_kwargs(kwargs)

        # Build context (authentication errors use base context only)
        context = self._build_context(base_context)

        # Call parent with complete error information
        super().__init__(
            message,
            code=error_code or "TAP_LDAP_AUTHENTICATION_ERROR",
            context=context,
            correlation_id=correlation_id,
        )


class FlextTapLdapTimeoutError(FlextExceptions.BaseError):
    """LDAP tap timeout error."""

    @override
    def __init__(
        self,
        message: str,
        **kwargs: object,
    ) -> None:
        """Initialize LDAP timeout error."""
        # Extract common parameters using helper
        base_context, correlation_id, error_code = self._extract_common_kwargs(kwargs)

        # Build context (timeout errors use base context only)
        context = self._build_context(base_context)

        # Call parent with complete error information
        super().__init__(
            message,
            code=error_code or "TAP_LDAP_TIMEOUT_ERROR",
            context=context,
            correlation_id=correlation_id,
        )


# Create convenience aliases for existing code
FlextTapLdapSearchError = FlextTapLdapProcessingError  # Search is processing
FlextTapLdapStreamError = FlextTapLdapProcessingError  # Stream errors are processing


__all__: FlextTapLdapTypes.Core.StringList = [
    "FlextTapLdapAuthenticationError",
    "FlextTapLdapConfigurationError",
    "FlextTapLdapConnectionError",
    "FlextTapLdapError",
    "FlextTapLdapProcessingError",
    "FlextTapLdapSearchError",
    "FlextTapLdapStreamError",
    "FlextTapLdapTimeoutError",
    "FlextTapLdapValidationError",
]
