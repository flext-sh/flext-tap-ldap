"""Enterprise LDAP data extraction library for FLEXT ecosystem.

Single class per module pattern with nested classes.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_tap_ldap.__version__ import __version__, __version_info__
from flext_tap_ldap.client import FlextTapLdapClient
from flext_tap_ldap.ldif_streams import FlextTapLdapLdifStreams
from flext_tap_ldap.models import FlextMeltanoTapLdapModels, m
from flext_tap_ldap.processor import FlextTapLdapProcessor
from flext_tap_ldap.protocols import FlextMeltanoTapLdapProtocols, p
from flext_tap_ldap.settings import FlextTapLdapSettings
from flext_tap_ldap.streams import FlextTapLdapStreams
from flext_tap_ldap.tap import FlextTapLdapTap
from flext_tap_ldap.typings import t
from flext_tap_ldap.utilities import FlextMeltanoTapLdapUtilities, u

__all__ = [
    "FlextMeltanoTapLdapModels",
    "FlextMeltanoTapLdapProtocols",
    "FlextMeltanoTapLdapUtilities",
    "FlextTapLdapClient",
    "FlextTapLdapLdifStreams",
    "FlextTapLdapProcessor",
    "FlextTapLdapSettings",
    "FlextTapLdapStreams",
    "FlextTapLdapTap",
    "__version__",
    "__version_info__",
    "m",
    "p",
    "t",
    "u",
]
