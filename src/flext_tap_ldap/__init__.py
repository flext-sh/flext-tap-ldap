# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Enterprise LDAP data extraction library for FLEXT ecosystem.

Single class per module pattern with nested classes.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

from flext_tap_ldap.__version__ import (
    __author__ as __author__,
    __author_email__ as __author_email__,
    __description__ as __description__,
    __license__ as __license__,
    __title__ as __title__,
    __url__ as __url__,
    __version__ as __version__,
    __version_info__ as __version_info__,
)

if TYPE_CHECKING:
    from flext_ldap import d, e, h, r, s, x

    from flext_tap_ldap import (
        client as client,
        constants as constants,
        ldif_streams as ldif_streams,
        models as models,
        processor as processor,
        protocols as protocols,
        services as services,
        settings as settings,
        streams as streams,
        tap as tap,
        typings as typings,
        utilities as utilities,
    )
    from flext_tap_ldap._utilities._processor import (
        FlextTapLdapUtilitiesProcessorMixin as FlextTapLdapUtilitiesProcessorMixin,
    )
    from flext_tap_ldap.client import FlextTapLdapClient as FlextTapLdapClient
    from flext_tap_ldap.constants import (
        FlextTapLdapConstants as FlextTapLdapConstants,
        FlextTapLdapConstants as c,
    )
    from flext_tap_ldap.ldif_streams import (
        FlextTapLdapLdifStreams as FlextTapLdapLdifStreams,
    )
    from flext_tap_ldap.models import (
        FlextTapLdapModels as FlextTapLdapModels,
        FlextTapLdapModels as m,
    )
    from flext_tap_ldap.processor import (
        FlextLdifDistinguishedName as FlextLdifDistinguishedName,
        FlextTapLdapEntry as FlextTapLdapEntry,
        FlextTapLdapProcessor as FlextTapLdapProcessor,
        FlextTapLdapTransformer as FlextTapLdapTransformer,
        FlextTapLdapValidator as FlextTapLdapValidator,
    )
    from flext_tap_ldap.protocols import (
        FlextTapLdapProtocols as FlextTapLdapProtocols,
        FlextTapLdapProtocols as p,
    )
    from flext_tap_ldap.services import FlextTapLdapServices as FlextTapLdapServices
    from flext_tap_ldap.settings import FlextTapLdapSettings as FlextTapLdapSettings
    from flext_tap_ldap.streams import FlextTapLdapStreams as FlextTapLdapStreams
    from flext_tap_ldap.tap import (
        CLI_COMMAND as CLI_COMMAND,
        FlextTapLdapTap as FlextTapLdapTap,
        logger as logger,
        main as main,
    )
    from flext_tap_ldap.typings import (
        FlextTapLdapTypes as FlextTapLdapTypes,
        FlextTapLdapTypes as t,
    )
    from flext_tap_ldap.utilities import (
        FlextTapLdapUtilities as FlextTapLdapUtilities,
        FlextTapLdapUtilities as u,
    )

_LAZY_IMPORTS: Mapping[str, Sequence[str]] = {
    "CLI_COMMAND": ["flext_tap_ldap.tap", "CLI_COMMAND"],
    "FlextLdifDistinguishedName": ["flext_tap_ldap.processor", "FlextLdifDistinguishedName"],
    "FlextTapLdapClient": ["flext_tap_ldap.client", "FlextTapLdapClient"],
    "FlextTapLdapConstants": ["flext_tap_ldap.constants", "FlextTapLdapConstants"],
    "FlextTapLdapEntry": ["flext_tap_ldap.processor", "FlextTapLdapEntry"],
    "FlextTapLdapLdifStreams": ["flext_tap_ldap.ldif_streams", "FlextTapLdapLdifStreams"],
    "FlextTapLdapModels": ["flext_tap_ldap.models", "FlextTapLdapModels"],
    "FlextTapLdapProcessor": ["flext_tap_ldap.processor", "FlextTapLdapProcessor"],
    "FlextTapLdapProtocols": ["flext_tap_ldap.protocols", "FlextTapLdapProtocols"],
    "FlextTapLdapServices": ["flext_tap_ldap.services", "FlextTapLdapServices"],
    "FlextTapLdapSettings": ["flext_tap_ldap.settings", "FlextTapLdapSettings"],
    "FlextTapLdapStreams": ["flext_tap_ldap.streams", "FlextTapLdapStreams"],
    "FlextTapLdapTap": ["flext_tap_ldap.tap", "FlextTapLdapTap"],
    "FlextTapLdapTransformer": ["flext_tap_ldap.processor", "FlextTapLdapTransformer"],
    "FlextTapLdapTypes": ["flext_tap_ldap.typings", "FlextTapLdapTypes"],
    "FlextTapLdapUtilities": ["flext_tap_ldap.utilities", "FlextTapLdapUtilities"],
    "FlextTapLdapUtilitiesProcessorMixin": ["flext_tap_ldap._utilities._processor", "FlextTapLdapUtilitiesProcessorMixin"],
    "FlextTapLdapValidator": ["flext_tap_ldap.processor", "FlextTapLdapValidator"],
    "c": ["flext_tap_ldap.constants", "FlextTapLdapConstants"],
    "client": ["flext_tap_ldap.client", ""],
    "constants": ["flext_tap_ldap.constants", ""],
    "d": ["flext_ldap", "d"],
    "e": ["flext_ldap", "e"],
    "h": ["flext_ldap", "h"],
    "ldif_streams": ["flext_tap_ldap.ldif_streams", ""],
    "logger": ["flext_tap_ldap.tap", "logger"],
    "m": ["flext_tap_ldap.models", "FlextTapLdapModels"],
    "main": ["flext_tap_ldap.tap", "main"],
    "models": ["flext_tap_ldap.models", ""],
    "p": ["flext_tap_ldap.protocols", "FlextTapLdapProtocols"],
    "processor": ["flext_tap_ldap.processor", ""],
    "protocols": ["flext_tap_ldap.protocols", ""],
    "r": ["flext_ldap", "r"],
    "s": ["flext_ldap", "s"],
    "services": ["flext_tap_ldap.services", ""],
    "settings": ["flext_tap_ldap.settings", ""],
    "streams": ["flext_tap_ldap.streams", ""],
    "t": ["flext_tap_ldap.typings", "FlextTapLdapTypes"],
    "tap": ["flext_tap_ldap.tap", ""],
    "typings": ["flext_tap_ldap.typings", ""],
    "u": ["flext_tap_ldap.utilities", "FlextTapLdapUtilities"],
    "utilities": ["flext_tap_ldap.utilities", ""],
    "x": ["flext_ldap", "x"],
}

_EXPORTS: Sequence[str] = [
    "CLI_COMMAND",
    "FlextLdifDistinguishedName",
    "FlextTapLdapClient",
    "FlextTapLdapConstants",
    "FlextTapLdapEntry",
    "FlextTapLdapLdifStreams",
    "FlextTapLdapModels",
    "FlextTapLdapProcessor",
    "FlextTapLdapProtocols",
    "FlextTapLdapServices",
    "FlextTapLdapSettings",
    "FlextTapLdapStreams",
    "FlextTapLdapTap",
    "FlextTapLdapTransformer",
    "FlextTapLdapTypes",
    "FlextTapLdapUtilities",
    "FlextTapLdapUtilitiesProcessorMixin",
    "FlextTapLdapValidator",
    "__author__",
    "__author_email__",
    "__description__",
    "__license__",
    "__title__",
    "__url__",
    "__version__",
    "__version_info__",
    "c",
    "client",
    "constants",
    "d",
    "e",
    "h",
    "ldif_streams",
    "logger",
    "m",
    "main",
    "models",
    "p",
    "processor",
    "protocols",
    "r",
    "s",
    "services",
    "settings",
    "streams",
    "t",
    "tap",
    "typings",
    "u",
    "utilities",
    "x",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, _EXPORTS)
