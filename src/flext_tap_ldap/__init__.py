"""FLEXT Tap LDAP - Singer tap for LDAP data extraction.

This module implements the main tap class for LDAP data extraction
using the centralized patterns from flext-core and flext-meltano.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

# Import new consolidated implementations
from flext_tap_ldap.tap_client import (
    FlextTapLDAP,
    FlextTapLDAPPlugin,
    LDAPClient,
    LDAPClientConfig,
    create_ldap_tap_plugin,
    main,
)
from flext_tap_ldap.tap_config import (
    CustomStreamConfig,
    LDIFProcessingConfig,
    TapLDAPConfig,
)
from flext_tap_ldap.tap_models import (
    LDAPAttribute,
    LDAPConnection,
    LDAPEntry,
    LDAPGroup,
    LDAPRecord,
    LDAPSchema,
    LDAPStream,
    LDAPUser,
    TapExecution,
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

# Backward compatibility aliases for existing code
FlextTapLDAPConfig = TapLDAPConfig
LDAPTap = FlextTapLDAP
TapConfig = TapLDAPConfig

# Legacy imports for backward compatibility
from flext_tap_ldap import exceptions as tap_exceptions

__version__ = "0.9.0-reorganized"

__all__: list[str] = [
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
    # Backward compatibility
    "FlextTapLDAPConfig",
    "LDAPTap",
    "TapConfig",
    "__version__",
]
