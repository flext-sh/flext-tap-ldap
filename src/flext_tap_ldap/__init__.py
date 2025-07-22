"""FLEXT TAP LDAP - Singer LDAP Data Extraction with simplified imports.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Version 0.7.0 - Singer LDAP Tap with simplified public API:
- All common imports available from root: from flext_tap_ldap import TapLDAP
- Built on flext-core foundation for robust LDAP integration
- Deprecation warnings for internal imports
"""

from __future__ import annotations

import contextlib
import importlib.metadata
import warnings

# Import from flext-core for foundational patterns
# Foundation patterns - ALWAYS from flext-core
from flext_core import (
    BaseConfig,
    BaseConfig as LDAPBaseConfig,  # Configuration base
    DomainBaseModel,
    DomainBaseModel as BaseModel,  # Base for LDAP models
    DomainError as LDAPError,  # LDAP-specific errors
    ValidationError as ValidationError,  # Validation errors
)
from flext_core.domain.shared_types import ServiceResult

try:
    __version__ = importlib.metadata.version("flext-tap-ldap")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.7.0"

__version_info__ = tuple(int(x) for x in __version__.split(".") if x.isdigit())


class FlextTapLDAPDeprecationWarning(DeprecationWarning):
    """Custom deprecation warning for FLEXT TAP LDAP import changes."""


def _show_deprecation_warning(old_import: str, new_import: str) -> None:
    """Show deprecation warning for import paths."""
    message_parts = [
        f"⚠️  DEPRECATED IMPORT: {old_import}",
        f"✅ USE INSTEAD: {new_import}",
        "🔗 This will be removed in version 1.0.0",
        "📖 See FLEXT TAP LDAP docs for migration guide",
    ]
    warnings.warn(
        "\n".join(message_parts),
        FlextTapLDAPDeprecationWarning,
        stacklevel=3,
    )


# ================================
# SIMPLIFIED PUBLIC API EXPORTS
# ================================

# Singer Tap exports - simplified imports
try:
    from flext_tap_ldap.tap import TapLDAP
except ImportError:
    # Tap not yet fully refactored - provide type stub
    from typing import TYPE_CHECKING
    if TYPE_CHECKING:
        from flext_tap_ldap.tap import TapLDAP
    else:
        TapLDAP = type("TapLDAP", (), {})

# LDAP Client exports - simplified imports
with contextlib.suppress(ImportError):
    from flext_tap_ldap.client import LDAPClient

# LDAP Streams exports - simplified imports
with contextlib.suppress(ImportError):
    from flext_tap_ldap.streams import (
        GroupsStream,
        OrganizationalUnitsStream,
        UsersStream,
    )

# ================================
# PUBLIC API EXPORTS
# ================================

__all__ = [
    "BaseModel",  # from flext_tap_ldap import BaseModel
    # Deprecation utilities
    "FlextTapLDAPDeprecationWarning",
    # LDAP Streams (simplified access)
    "GroupsStream",  # from flext_tap_ldap import GroupsStream
    # Core Patterns (from flext-core)
    "LDAPBaseConfig",  # from flext_tap_ldap import LDAPBaseConfig
    "LDAPClient",  # from flext_tap_ldap import LDAPClient
    "LDAPError",  # from flext_tap_ldap import LDAPError
    "OrganizationalUnitsStream",  # from flext_tap_ldap import OrganizationalUnitsStream
    "ServiceResult",  # from flext_tap_ldap import ServiceResult
    # Main Singer Tap (simplified access)
    "TapLDAP",  # from flext_tap_ldap import TapLDAP
    "UsersStream",  # from flext_tap_ldap import UsersStream
    "ValidationError",  # from flext_tap_ldap import ValidationError
    # Version
    "__version__",
    "__version_info__",
]
