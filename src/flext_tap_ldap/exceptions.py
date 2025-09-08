"""Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT.
"""

from __future__ import annotations

from flext_core import FlextTypes

"""Domain-specific exceptions for LDAP tap operations using FlextExceptions patterns.

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT

LDAP Tap Exception Hierarchy using flext-core FlextExceptions patterns.
"""


from flext_core.exceptions import FlextExceptions
from flext_core.typings import FlextTypes


# LDAP Tap specific exceptions using FlextExceptions base patterns
class FlextTapLdapError(FlextExceptions.Error):
    """Base LDAP tap error."""

    def __init__(self, message: str, **kwargs: object) -> None:
        super().__init__(message, **kwargs)


class FlextTapLdapValidationError(FlextExceptions.ValidationError):
    """LDAP tap validation error."""

    def __init__(self, message: str, **kwargs: object) -> None:
        super().__init__(message, **kwargs)


class FlextTapLdapConfigurationError(FlextExceptions.ConfigurationError):
    """LDAP tap configuration error."""

    def __init__(self, message: str, **kwargs: object) -> None:
        super().__init__(message, **kwargs)


class FlextTapLdapProcessingError(FlextExceptions.ProcessingError):
    """LDAP tap processing error."""

    def __init__(self, message: str, **kwargs: object) -> None:
        super().__init__(message, **kwargs)


class FlextTapLdapConnectionError(FlextExceptions.ConnectionError):
    """LDAP tap connection error."""

    def __init__(self, message: str, **kwargs: object) -> None:
        super().__init__(message, **kwargs)


class FlextTapLdapAuthenticationError(FlextExceptions.AuthenticationError):
    """LDAP tap authentication error."""

    def __init__(self, message: str, **kwargs: object) -> None:
        super().__init__(message, **kwargs)


class FlextTapLdapTimeoutError(FlextExceptions.TimeoutError):
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
