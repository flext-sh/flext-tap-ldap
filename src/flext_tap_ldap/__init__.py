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
from flext_tap_ldap.ldif_processor import (
    FlextLdifProcessor,
    LDIFEntry,
    LDIFTransformer,
    LDIFValidator,
)
from flext_tap_ldap.ldif_stream import (
    LDIFAnalysisStream,
    LDIFStream,
)
from flext_tap_ldap.models import (
    ConnectionTestedEvent,
    FlextMeltanoTapLdapModels,
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
from flext_tap_ldap.protocols import FlextMeltanoTapLdapProtocols
from flext_tap_ldap.services import FlextMeltanoTapLdapServices
from flext_tap_ldap.tap_client import FlextMeltanoTapLDAP, FlextMeltanoTapLDAPPlugin
from flext_tap_ldap.tap_streams import (
    CustomStream,
    GroupsStream,
    LDAPBaseStream,
    UsersStream,
)
from flext_tap_ldap.typings import FlextMeltanoTapLdapTypes
from flext_tap_ldap.version import VERSION, FlextMeltanoTapLdapVersion

PROJECT_VERSION: Final[FlextMeltanoTapLdapVersion] = VERSION

__version__: str = VERSION.version
__version_info__: tuple[int | str, ...] = VERSION.version_info

__all__ = [
    "PROJECT_VERSION",
    "VERSION",
    "ConnectionTestedEvent",
    "CustomStream",
    "CustomStreamConfig",
    "FlextLdifProcessor",
    "FlextMeltanoTapLDAP",
    "FlextMeltanoTapLDAPPlugin",
    "FlextMeltanoTapLdapAuthenticationError",
    "FlextMeltanoTapLdapConfig",
    "FlextMeltanoTapLdapConfigurationError",
    "FlextMeltanoTapLdapConnectionError",
    "FlextMeltanoTapLdapError",
    "FlextMeltanoTapLdapModels",
    "FlextMeltanoTapLdapProcessingError",
    "FlextMeltanoTapLdapProtocols",
    "FlextMeltanoTapLdapSearchError",
    "FlextMeltanoTapLdapServices",
    "FlextMeltanoTapLdapServices.LDAPConnectionService",
    "FlextMeltanoTapLdapServices.LDAPRecordService",
    "FlextMeltanoTapLdapServices.LDAPStreamService",
    "FlextMeltanoTapLdapServices.StreamCreationParams",
    "FlextMeltanoTapLdapServices.TapExecutionService",
    "FlextMeltanoTapLdapStreamError",
    "FlextMeltanoTapLdapTimeoutError",
    "FlextMeltanoTapLdapTypes",
    "FlextMeltanoTapLdapValidationError",
    "FlextMeltanoTapLdapVersion",
    "FlextTapLdapConfig",
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
