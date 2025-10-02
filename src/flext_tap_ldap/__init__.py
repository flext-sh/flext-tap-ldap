"""Enterprise LDAP data extraction library for FLEXT ecosystem.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Final

from flext_tap_ldap.client import LDAPClient, LDAPClientConfig
from flext_tap_ldap.config import (
    CustomStreamConfig,
    FlextTapLdapConfig,
    LDIFProcessingConfig,
)
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
    ConnectionTestedEvent,
    FlextTapLdapModels,
    LDAPAttribute,
    LDAPConnection,
    LDAPEntry,
    LDAPGroup,
    LDAPRecord,
    LDAPSchema,
    LDAPStream,
    LDAPUser,
    RecordExtractedEvent,
    StreamDiscoveredEvent,
    TapExecution,
    TapExecutionCompletedEvent,
    TapExecutionStartedEvent,
)
from flext_tap_ldap.protocols import FlextTapLdapProtocols
from flext_tap_ldap.services import (
    LDAPConnectionParams,
    LDAPConnectionService,
    LDAPRecordService,
    LDAPStreamService,
    StreamCreationParams,
    TapExecutionService,
)
from flext_tap_ldap.tap_client import FlextTapLDAP, FlextTapLDAPPlugin
from flext_tap_ldap.tap_streams import (
    CustomStream,
    GroupsStream,
    LDAPBaseStream,
    UsersStream,
)
from flext_tap_ldap.typings import FlextTapLdapTypes
from flext_tap_ldap.version import VERSION, FlextTapLdapVersion

PROJECT_VERSION: Final[FlextTapLdapVersion] = VERSION

__version__: str = VERSION.version
__version_info__: tuple[int | str, ...] = VERSION.version_info

__all__ = [
    "PROJECT_VERSION",
    "VERSION",
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
    "FlextTapLdapProtocols",
    "FlextTapLdapSearchError",
    "FlextTapLdapStreamError",
    "FlextTapLdapTimeoutError",
    "FlextTapLdapTypes",
    "FlextTapLdapValidationError",
    "FlextTapLdapVersion",
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
