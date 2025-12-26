"""Enterprise LDAP data extraction library for FLEXT ecosystem.

Single class per module pattern with nested classes.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_tap_ldap.client import FlextTapLdapClient
from flext_tap_ldap.ldif_streams import FlextTapLdapLdifStreams
from flext_tap_ldap.models import FlextMeltanoTapLdapModels, m, m_tap_ldap
from flext_tap_ldap.processor import FlextTapLdapProcessor
from flext_tap_ldap.settings import FlextTapLdapSettings
from flext_tap_ldap.streams import FlextTapLdapStreams
from flext_tap_ldap.tap import FlextTapLdapTap

__version__: str = "1.0.0"
__version_info__: tuple[int | str, ...] = (1, 0, 0)

__all__ = [
    "FlextMeltanoTapLdapModels",
    "FlextTapLdapClient",
    "FlextTapLdapLdifStreams",
    "FlextTapLdapModels",
    "FlextTapLdapProcessor",
    "FlextTapLdapSettings",
    "FlextTapLdapStreams",
    # Main container classes
    "FlextTapLdapTap",
    # Version info
    "__version__",
    "__version_info__",
    "m",
    "m_tap_ldap",
]
