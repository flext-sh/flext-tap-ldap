"""Enterprise LDAP data extraction library for FLEXT ecosystem.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tap_ldap.client import LDAPClient, LDAPClientConfig
from flext_tap_ldap.config import FlextTapLdapConfig
from flext_tap_ldap.exceptions import (
    FlextTapLdapAuthenticationError,
    FlextTapLdapConfigurationError,
    FlextTapLdapConnectionError,
    FlextTapLdapError,
    FlextTapLdapProcessingError,
    FlextTapLdapSearchError,
    FlextTapLdapStreamError,
    FlextTapLdapTimeoutError,
    FlextTapLdapValidationError,
)
from flext_tap_ldap.ldif_processor import (
    FlextLdifProcessor,
    LDIFEntry,
    LDIFParseError,
    LDIFTransformer,
    LDIFValidator,
)
from flext_tap_ldap.ldif_stream import (
    LDIFAnalysisStream,
    LDIFStream,
)
from flext_tap_ldap.models import (
    FlextTapLdapModels,
    FlextTapLdapUtilities,
    LDAPAttribute,
    LDAPEntry,
    LDAPGroup,
    LDAPSchema,
    LDAPUser,
)
from flext_tap_ldap.services import (
    LDAPConnectionParams,
    LDAPConnectionService,
    LDAPRecordService,
    LDAPStreamService,
    StreamCreationParams,
    TapExecutionService,
)
from flext_tap_ldap.tap_client import FlextTapLDAP, FlextTapLDAPPlugin
from flext_tap_ldap.tap_config import (
    CustomStreamConfig,
    LDIFProcessingConfig,
)
from flext_tap_ldap.tap_models import (
    ConnectionTestedEvent,
    LDAPConnection,
    LDAPRecord,
    LDAPStream,
    RecordExtractedEvent,
    StreamDiscoveredEvent,
    TapExecution,
    TapExecutionCompletedEvent,
    TapExecutionStartedEvent,
)
from flext_tap_ldap.tap_streams import (
    CustomStream,
    GroupsStream,
    LDAPBaseStream,
    UsersStream,
)
from flext_tap_ldap.typings import FlextTapLdapTypes

__version__ = "0.9.0-reorganized"
__version_info__ = tuple(int(x) for x in __version__.split(".") if x.isdigit())

__all__: FlextTapLdapTypes.Core.StringList = [
    "ConnectionTestedEvent",
    "CustomStream",
    "CustomStreamConfig",
    "FlextLdifProcessor",
    "FlextTapLDAP",
    "FlextTapLDAPPlugin",
    "FlextTapLdapAuthenticationError",
    "FlextTapLdapConfig",
    "FlextTapLdapConfigurationError",
    "FlextTapLdapConnectionError",
    "FlextTapLdapError",
    "FlextTapLdapModels",
    "FlextTapLdapProcessingError",
    "FlextTapLdapSearchError",
    "FlextTapLdapStreamError",
    "FlextTapLdapTimeoutError",
    "FlextTapLdapUtilities",
    "FlextTapLdapValidationError",
    "GroupsStream",
    "LDAPAttribute",
    "LDAPBaseStream",
    "LDAPClient",
    "LDAPClientConfig",
    "LDAPConnection",
    "LDAPConnectionParams",
    "LDAPConnectionService",
    "LDAPEntry",
    "LDAPGroup",
    "LDAPRecord",
    "LDAPRecordService",
    "LDAPSchema",
    "LDAPStream",
    "LDAPStreamService",
    "LDAPUser",
    "LDIFAnalysisStream",
    "LDIFEntry",
    "LDIFParseError",
    "LDIFProcessingConfig",
    "LDIFStream",
    "LDIFTransformer",
    "LDIFValidator",
    "RecordExtractedEvent",
    "StreamCreationParams",
    "StreamDiscoveredEvent",
    "TapExecution",
    "TapExecutionCompletedEvent",
    "TapExecutionService",
    "TapExecutionStartedEvent",
    "UsersStream",
    "__version__",
    "__version_info__",
]
