"""Enterprise LDAP data extraction library for FLEXT ecosystem.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextTypes

from flext_tap_ldap.client import LDAPClient, LDAPClientConfig
from flext_tap_ldap.exceptions import (
    FlextTapLdapConnectionError,
    FlextTapLdapError,
    FlextTapLdapValidationError,
)
from flext_tap_ldap.models import (
    LDAPAttribute,
    LDAPEntry,
    LDAPGroup,
    LDAPSchema,
    LDAPUser,
)
from flext_tap_ldap.tap_client import FlextTapLDAP, FlextTapLDAPPlugin
from flext_tap_ldap.tap_config import (
    CustomStreamConfig,
    LDIFProcessingConfig,
    TapLDAPConfig,
)
from flext_tap_ldap.tap_services import (
    LDAPConnectionService,
    LDAPRecordService,
    LDAPStreamService,
    TapExecutionService,
)
from flext_tap_ldap.tap_streams import (
    CustomStream,
    GroupsStream,
    LDAPBaseStream,
    UsersStream,
)

__version__ = "0.9.0-reorganized"
__version_info__ = tuple(int(x) for x in __version__.split(".") if x.isdigit())

__all__: FlextTypes.Core.StringList = [
    "CustomStream",
    "CustomStreamConfig",
    "FlextTapLDAP",
    "FlextTapLDAPPlugin",
    "FlextTapLdapConnectionError",
    "FlextTapLdapError",
    "FlextTapLdapValidationError",
    "GroupsStream",
    "LDAPAttribute",
    "LDAPBaseStream",
    "LDAPClient",
    "LDAPClientConfig",
    "LDAPConnectionService",
    "LDAPEntry",
    "LDAPGroup",
    "LDAPRecordService",
    "LDAPSchema",
    "LDAPStreamService",
    "LDAPUser",
    "LDIFProcessingConfig",
    "TapExecutionService",
    "TapLDAPConfig",
    "UsersStream",
    "__version__",
    "__version_info__",
]
