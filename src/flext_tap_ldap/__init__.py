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
from typing import TYPE_CHECKING as _TYPE_CHECKING

from flext_core.lazy import install_lazy_exports, merge_lazy_imports
from flext_tap_ldap.__version__ import (
    __author__,
    __author_email__,
    __description__,
    __license__,
    __title__,
    __url__,
    __version__,
    __version_info__,
)

if _TYPE_CHECKING:
    from flext_core import FlextTypes
    from flext_core.decorators import FlextDecorators as d
    from flext_core.exceptions import FlextExceptions as e
    from flext_core.handlers import FlextHandlers as h
    from flext_core.mixins import FlextMixins as x
    from flext_core.result import FlextResult as r
    from flext_core.service import FlextService as s
    from flext_tap_ldap import (
        _utilities,
        api,
        client,
        constants,
        ldif_streams,
        models,
        processor,
        protocols,
        services,
        settings,
        streams,
        tap,
        typings,
        utilities,
    )
    from flext_tap_ldap._utilities import FlextTapLdapUtilitiesProcessorMixin
    from flext_tap_ldap.api import FlextTapLdapService
    from flext_tap_ldap.client import FlextTapLdapClient
    from flext_tap_ldap.constants import (
        FlextTapLdapConstants,
        FlextTapLdapConstants as c,
    )
    from flext_tap_ldap.ldif_streams import FlextTapLdapLdifStreams
    from flext_tap_ldap.models import FlextTapLdapModels, FlextTapLdapModels as m
    from flext_tap_ldap.processor import (
        FlextLdifDistinguishedName,
        FlextTapLdapEntry,
        FlextTapLdapProcessor,
        FlextTapLdapTransformer,
        FlextTapLdapValidator,
    )
    from flext_tap_ldap.protocols import (
        FlextTapLdapProtocols,
        FlextTapLdapProtocols as p,
    )
    from flext_tap_ldap.services import FlextTapLdapServices
    from flext_tap_ldap.settings import FlextTapLdapSettings
    from flext_tap_ldap.streams import FlextTapLdapStreams
    from flext_tap_ldap.tap import CLI_COMMAND, FlextTapLdapTap, logger, main
    from flext_tap_ldap.typings import FlextTapLdapTypes, FlextTapLdapTypes as t
    from flext_tap_ldap.utilities import (
        FlextTapLdapUtilities,
        FlextTapLdapUtilities as u,
    )

_LAZY_IMPORTS: FlextTypes.LazyImportIndex = merge_lazy_imports(
    ("flext_tap_ldap._utilities",),
    {
        "CLI_COMMAND": "flext_tap_ldap.tap",
        "FlextLdifDistinguishedName": "flext_tap_ldap.processor",
        "FlextTapLdapClient": "flext_tap_ldap.client",
        "FlextTapLdapConstants": "flext_tap_ldap.constants",
        "FlextTapLdapEntry": "flext_tap_ldap.processor",
        "FlextTapLdapLdifStreams": "flext_tap_ldap.ldif_streams",
        "FlextTapLdapModels": "flext_tap_ldap.models",
        "FlextTapLdapProcessor": "flext_tap_ldap.processor",
        "FlextTapLdapProtocols": "flext_tap_ldap.protocols",
        "FlextTapLdapService": "flext_tap_ldap.api",
        "FlextTapLdapServices": "flext_tap_ldap.services",
        "FlextTapLdapSettings": "flext_tap_ldap.settings",
        "FlextTapLdapStreams": "flext_tap_ldap.streams",
        "FlextTapLdapTap": "flext_tap_ldap.tap",
        "FlextTapLdapTransformer": "flext_tap_ldap.processor",
        "FlextTapLdapTypes": "flext_tap_ldap.typings",
        "FlextTapLdapUtilities": "flext_tap_ldap.utilities",
        "FlextTapLdapValidator": "flext_tap_ldap.processor",
        "_utilities": "flext_tap_ldap._utilities",
        "api": "flext_tap_ldap.api",
        "c": ("flext_tap_ldap.constants", "FlextTapLdapConstants"),
        "client": "flext_tap_ldap.client",
        "constants": "flext_tap_ldap.constants",
        "d": ("flext_core.decorators", "FlextDecorators"),
        "e": ("flext_core.exceptions", "FlextExceptions"),
        "h": ("flext_core.handlers", "FlextHandlers"),
        "ldif_streams": "flext_tap_ldap.ldif_streams",
        "logger": "flext_tap_ldap.tap",
        "m": ("flext_tap_ldap.models", "FlextTapLdapModels"),
        "main": "flext_tap_ldap.tap",
        "models": "flext_tap_ldap.models",
        "p": ("flext_tap_ldap.protocols", "FlextTapLdapProtocols"),
        "processor": "flext_tap_ldap.processor",
        "protocols": "flext_tap_ldap.protocols",
        "r": ("flext_core.result", "FlextResult"),
        "s": ("flext_core.service", "FlextService"),
        "services": "flext_tap_ldap.services",
        "settings": "flext_tap_ldap.settings",
        "streams": "flext_tap_ldap.streams",
        "t": ("flext_tap_ldap.typings", "FlextTapLdapTypes"),
        "tap": "flext_tap_ldap.tap",
        "typings": "flext_tap_ldap.typings",
        "u": ("flext_tap_ldap.utilities", "FlextTapLdapUtilities"),
        "utilities": "flext_tap_ldap.utilities",
        "x": ("flext_core.mixins", "FlextMixins"),
    },
)


install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    [
        "__author__",
        "__author_email__",
        "__description__",
        "__license__",
        "__title__",
        "__url__",
        "__version__",
        "__version_info__",
    ],
)
