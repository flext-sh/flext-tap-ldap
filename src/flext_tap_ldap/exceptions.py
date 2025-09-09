"""Domain-specific exceptions for LDAP tap operations using FlextExceptions patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

LDAP Tap Exception Hierarchy using flext-core FlextExceptions patterns.
"""

from __future__ import annotations

from flext_core.exceptions import FlextExceptions
from flext_core.typings import FlextTypes

# All exceptions inherit from FlextExceptions.BaseError for simplicity


# LDAP Tap specific exceptions using FlextExceptions base patterns
class FlextTapLdapError(FlextExceptions.BaseError):
    """Base LDAP tap error."""

    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        context: dict[str, object] | None = None,
        correlation_id: str | None = None,
    ) -> None:
        super().__init__(
            message, code=code, context=context, correlation_id=correlation_id
        )


class FlextTapLdapValidationError(FlextExceptions.BaseError):
    """LDAP tap validation error."""

    def __init__(
        self,
        message: str,
        *,
        field: str | None = None,
        value: object | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(message, field=field, value=value, **kwargs)


class FlextTapLdapConfigurationError(FlextExceptions.BaseError):
    """LDAP tap configuration error."""

    def __init__(self, message: str, **kwargs: object) -> None:
        super().__init__(message, **kwargs)


class FlextTapLdapProcessingError(FlextExceptions.BaseError):
    """LDAP tap processing error."""

    def __init__(self, message: str, **kwargs: object) -> None:
        super().__init__(message, **kwargs)


class FlextTapLdapConnectionError(FlextExceptions.BaseError):
    """LDAP tap connection error."""

    def __init__(self, message: str, **kwargs: object) -> None:
        super().__init__(message, **kwargs)


class FlextTapLdapAuthenticationError(FlextExceptions.BaseError):
    """LDAP tap authentication error."""

    def __init__(self, message: str, **kwargs: object) -> None:
        super().__init__(message, **kwargs)


class FlextTapLdapTimeoutError(FlextExceptions.BaseError):
    """LDAP tap timeout error."""

    def __init__(self, message: str, **kwargs: object) -> None:
        super().__init__(message, **kwargs)


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
