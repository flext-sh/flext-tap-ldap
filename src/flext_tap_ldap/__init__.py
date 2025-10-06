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
from flext_tap_ldap.services import FlextTapLdapServices
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
    "FlextTapLdapServices",
    "FlextTapLdapServices.LDAPConnectionService",
    "FlextTapLdapServices.LDAPRecordService",
    "FlextTapLdapServices.LDAPStreamService",
    "FlextTapLdapServices.StreamCreationParams",
    "FlextTapLdapServices.TapExecutionService",
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
    "LDAPEntry",
    "LDAPGroup",
    "LDAPRecord",
    "LDAPSchema",
    "LDAPStream",
    "LDAPUser",
    "LDIFAnalysisStream",
    "LDIFEntry",
    "LDIFParseError",
    "LDIFProcessingConfig",
    "LDIFStream",
    "LDIFTransformer",
    "LDIFValidator",
    "RecordExtractedEvent",
    "StreamDiscoveredEvent",
    "TapExecution",
    "TapExecutionCompletedEvent",
    "TapExecutionStartedEvent",
    "UsersStream",
    "__version__",
    "__version_info__",
]
