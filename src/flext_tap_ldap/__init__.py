"""FLEXT Tap LDAP - Singer tap for LDAP data extraction.

This module implements the main tap class for LDAP data extraction
using the centralized patterns from flext-core and flext-meltano.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

# Import local implementations
from flext_tap_ldap.config import TapLDAPConfig
from flext_tap_ldap.tap import FlextTapLDAP

# Backward compatibility aliases
FlextTapLDAPConfig = TapLDAPConfig
LDAPTap = FlextTapLDAP
TapConfig = TapLDAPConfig

__version__ = "0.9.0-wrapper"

__all__: list[str] = [
    # Backward compatibility
    "FlextTapLDAP",
    "FlextTapLDAPConfig",
    "LDAPTap",
    "TapConfig",
    "TapLDAPConfig",
    "__version__",
]
