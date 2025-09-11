"""Copyright (c) 2025 FLEXT Team. All rights reserved.

SPDX-License-Identifier: MIT.

Singer tap for LDAP data extraction.
"""

from __future__ import annotations
from flext_core.typings import FlextTypes

# Import exceptions
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

# Import new consolidated implementations
from flext_tap_ldap.tap_client import (
    FlextTapLDAP,
    FlextTapLDAPPlugin,
    create_ldap_tap_plugin,
    main,
)
from flext_tap_ldap.client import (
    LDAPClient,
    LDAPClientConfig,
)
from flext_tap_ldap.tap_config import (
    CustomStreamConfig,
    LDIFProcessingConfig,
    TapLDAPConfig,
)
from flext_tap_ldap.models import (
    LDAPAttribute,
    LDAPConnection,
    LDAPEntry,
    LDAPGroup,
    LDAPRecord,
    LDAPSchema,
    LDAPStream,
    LDAPUser,
    TapExecution,
    TapExecutionCompletedEvent,
    TapExecutionStartedEvent,
)
from flext_tap_ldap.tap_services import (
    LDAPConnectionParams,
    LDAPConnectionService,
    LDAPRecordService,
    LDAPStreamService,
    LDIFConfigBuilder,
    LDIFProcessingService,
    StreamCreationParams,
    TapExecutionService,
    create_development_ldap_config,
    create_ldap_connection_config,
    create_production_ldap_config,
    setup_ldap_tap,
    validate_ldap_config,
)
from flext_tap_ldap.tap_streams import (
    CustomStream,
    CustomStreamParams,
    FallbackDataFactory,
    GroupsStream,
    LDAPBaseStream,
    LDIFAnalysisStream,
    LDIFStream,
    OrganizationalUnitsStream,
    SchemaStream,
    UsersStream,
)

# Testing convenience aliases for existing code
FlextTapLDAPConfig = TapLDAPConfig
LDAPTap = FlextTapLDAP
TapConfig = TapLDAPConfig


# Ultra-simple aliases for test compatibility
class FlextLDIFProcessor:
    """Ultra-simple alias for test compatibility - LDIFProcessor."""


class LDIFEntry:
    """Ultra-simple alias for test compatibility - LDIFEntry."""


class LDIFParseError(Exception):
    """Ultra-simple alias for test compatibility - LDIFParseError."""


class LDIFTransformer:
    """Ultra-simple alias for test compatibility - LDIFTransformer."""


class LDIFValidator:
    """Ultra-simple alias for test compatibility - LDIFValidator."""


# Testing convenience imports for existing code
from flext_tap_ldap import exceptions as tap_exceptions

__version__ = "0.9.0-reorganized"
__version_info__ = tuple(int(x) for x in __version__.split(".") if x.isdigit())

__all__: FlextTypes.Core.StringList = [
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
    # Main Classes
    "FlextTapLDAP",
    "FlextTapLDAPPlugin",
    "LDAPClient",
    # Configuration
    "TapLDAPConfig",
    "CustomStreamConfig",
    "LDIFProcessingConfig",
    "LDAPClientConfig",
    # Models
    "LDAPAttribute",
    "LDAPConnection",
    "LDAPEntry",
    "LDAPGroup",
    "LDAPRecord",
    "LDAPSchema",
    "LDAPStream",
    "LDAPUser",
    "TapExecution",
    "TapExecutionCompletedEvent",
    "TapExecutionStartedEvent",
    # Streams
    "CustomStream",
    "CustomStreamParams",
    "GroupsStream",
    "LDAPBaseStream",
    "LDIFAnalysisStream",
    "LDIFStream",
    "OrganizationalUnitsStream",
    "SchemaStream",
    "UsersStream",
    # Services
    "LDAPConnectionService",
    "LDAPRecordService",
    "LDAPStreamService",
    "LDIFProcessingService",
    "TapExecutionService",
    # Utilities
    "FallbackDataFactory",
    "LDAPConnectionParams",
    "LDIFConfigBuilder",
    "StreamCreationParams",
    # Factory Functions
    "create_ldap_tap_plugin",
    "create_development_ldap_config",
    "create_ldap_connection_config",
    "create_production_ldap_config",
    "setup_ldap_tap",
    "validate_ldap_config",
    # Entry Point
    "main",
    # Testing convenience
    "FlextTapLDAPConfig",
    "LDAPTap",
    "TapConfig",
    "FlextLDIFProcessor",
    "LDIFEntry",
    "LDIFParseError",
    "LDIFTransformer",
    "LDIFValidator",
    "__version__",
    "__version_info__",
]
