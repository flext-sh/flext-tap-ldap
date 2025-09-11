"""Copyright (c) 2025 FLEXT Team. All rights reserved.

SPDX-License-Identifier: MIT.

Singer tap for LDAP data extraction.
"""

from __future__ import annotations

from flext_core.typings import FlextTypes

from flext_tap_ldap.client import (
    LDAPClient,
    LDAPClientConfig,
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
from flext_tap_ldap.tap_client import (
    FlextTapLDAP,
    FlextTapLDAPPlugin,
    create_ldap_tap_plugin,
    main,
)
from flext_tap_ldap.tap_config import (
    CustomStreamConfig,
    LDIFProcessingConfig,
    TapLDAPConfig,
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
