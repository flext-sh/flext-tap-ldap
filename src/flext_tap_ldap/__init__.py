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
    # Streams
    "CustomStream",
    "CustomStreamConfig",
    "CustomStreamParams",
    # Utilities
    "FallbackDataFactory",
    "FlextLDIFProcessor",
    # Main Classes
    "FlextTapLDAP",
    # Testing convenience
    "FlextTapLDAPConfig",
    "FlextTapLDAPPlugin",
    # Exceptions
    "FlextTapLdapAuthenticationError",
    "FlextTapLdapConfigurationError",
    "FlextTapLdapConnectionError",
    "FlextTapLdapError",
    "FlextTapLdapProcessingError",
    "FlextTapLdapSearchError",
    "FlextTapLdapStreamError",
    "FlextTapLdapTimeoutError",
    "FlextTapLdapValidationError",
    "GroupsStream",
    # Models
    "LDAPAttribute",
    "LDAPBaseStream",
    "LDAPClient",
    "LDAPClientConfig",
    "LDAPConnection",
    "LDAPConnectionParams",
    # Services
    "LDAPConnectionService",
    "LDAPEntry",
    "LDAPGroup",
    "LDAPRecord",
    "LDAPRecordService",
    "LDAPSchema",
    "LDAPStream",
    "LDAPStreamService",
    "LDAPTap",
    "LDAPUser",
    "LDIFAnalysisStream",
    "LDIFConfigBuilder",
    "LDIFEntry",
    "LDIFParseError",
    "LDIFProcessingConfig",
    "LDIFProcessingService",
    "LDIFStream",
    "LDIFTransformer",
    "LDIFValidator",
    "OrganizationalUnitsStream",
    "SchemaStream",
    "StreamCreationParams",
    "TapConfig",
    "TapExecution",
    "TapExecutionCompletedEvent",
    "TapExecutionService",
    "TapExecutionStartedEvent",
    # Configuration
    "TapLDAPConfig",
    "UsersStream",
    "__version__",
    "__version_info__",
    "create_development_ldap_config",
    "create_ldap_connection_config",
    # Factory Functions
    "create_ldap_tap_plugin",
    "create_production_ldap_config",
    # Entry Point
    "main",
    "setup_ldap_tap",
    "tap_exceptions",
    "validate_ldap_config",
]
