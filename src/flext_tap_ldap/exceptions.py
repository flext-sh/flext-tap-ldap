"""Domain-specific exceptions for LDAP tap operations using FlextExceptions patterns.

LDAP Tap Exception Hierarchy using flext-core FlextExceptions patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import override

from flext_core import FlextExceptions, FlextTypes


# LDAP Tap specific exceptions using FlextExceptions base patterns
class FlextTapLdapError(FlextExceptions.BaseError):
    """Base LDAP tap error."""

    @override
    @override
    @override
    @override
    @override
    @override
    @override
    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        context: dict[str, object] | None = None,
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
    @override
    @override
    @override
    @override
    @override
    @override
    def __init__(
        self,
        message: str,
        *,
        field: str | None = None,
        value: object | None = None,
        code: str | None = None,
        context: dict[str, object] | None = None,
        correlation_id: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize LDAP tap validation error."""
        # Merge extra kwargs and field/value into context
        merged_context: dict[str, object] = dict(context) if context else {}
        if field is not None:
            merged_context["field"] = field
        if value is not None:
            merged_context["value"] = value
        merged_context.update(kwargs)
        super().__init__(
            message,
            code=code,
            context=merged_context or None,
            correlation_id=correlation_id,
        )


class FlextTapLdapConfigurationError(FlextExceptions.BaseError):
    """LDAP tap configuration error."""

    @override
    @override
    @override
    @override
    @override
    @override
    @override
    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        context: dict[str, object] | None = None,
        correlation_id: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize LDAP tap configuration error."""
        # Merge extra kwargs into context
        merged_context: dict[str, object] = dict(context) if context else {}
        merged_context.update(kwargs)
        super().__init__(
            message,
            code=code,
            context=merged_context or None,
            correlation_id=correlation_id,
        )


class FlextTapLdapProcessingError(FlextExceptions.BaseError):
    """LDAP tap processing error."""

    @override
    @override
    @override
    @override
    @override
    @override
    @override
    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        context: dict[str, object] | None = None,
        correlation_id: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize LDAP tap processing error."""
        # Merge extra kwargs into context
        merged_context: dict[str, object] = dict(context) if context else {}
        merged_context.update(kwargs)
        super().__init__(
            message,
            code=code,
            context=merged_context or None,
            correlation_id=correlation_id,
        )


class FlextTapLdapConnectionError(FlextExceptions.BaseError):
    """LDAP tap connection error."""

    @override
    @override
    @override
    @override
    @override
    @override
    @override
    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        context: dict[str, object] | None = None,
        correlation_id: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize LDAP tap connection error."""
        # Merge extra kwargs into context
        merged_context: dict[str, object] = dict(context) if context else {}
        merged_context.update(kwargs)
        super().__init__(
            message,
            code=code,
            context=merged_context or None,
            correlation_id=correlation_id,
        )


class FlextTapLdapAuthenticationError(FlextExceptions.BaseError):
    """LDAP tap authentication error."""

    @override
    @override
    @override
    @override
    @override
    @override
    @override
    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        context: dict[str, object] | None = None,
        correlation_id: str | None = None,
        **kwargs: object,
    ) -> None:
        """Initialize LDAP tap authentication error."""
        # Merge extra kwargs into context
        merged_context: dict[str, object] = dict(context) if context else {}
        merged_context.update(kwargs)
        super().__init__(
            message,
            code=code,
            context=merged_context or None,
            correlation_id=correlation_id,
        )


class FlextTapLdapTimeoutError(FlextExceptions.BaseError):
    """LDAP tap timeout error."""

    @override
    @override
    @override
    @override
    @override
    @override
    @override
    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        context: dict[str, object] | None = None,
        correlation_id: str | None = None,
        **kwargs: object,
    ) -> None:
        # Merge extra kwargs into context
        """Initialize LDAP timeout error."""
        merged_context: dict[str, object] = dict(context) if context else {}
        merged_context.update(kwargs)
        super().__init__(
            message,
            code=code,
            context=merged_context or None,
            correlation_id=correlation_id,
        )


# Create convenience aliases for existing code
FlextTapLdapSearchError = FlextTapLdapProcessingError  # Search is processing
FlextTapLdapStreamError = FlextTapLdapProcessingError  # Stream errors are processing


__all__: FlextTypes.Core.StringList = [
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
