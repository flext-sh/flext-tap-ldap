# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Enterprise LDAP data extraction library for FLEXT ecosystem.

Single class per module pattern with nested classes.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import cleanup_submodule_namespace, lazy_getattr

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

if TYPE_CHECKING:
    from flext_core import FlextTypes
    from flext_ldap import d, e, h, r, s, x

    from flext_tap_ldap import (
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
    from flext_tap_ldap._utilities._processor import FlextTapLdapUtilitiesProcessorMixin
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

_LAZY_IMPORTS: Mapping[str, Sequence[str]] = {
    "CLI_COMMAND": ["flext_tap_ldap.tap", "CLI_COMMAND"],
    "FlextLdifDistinguishedName": [
        "flext_tap_ldap.processor",
        "FlextLdifDistinguishedName",
    ],
    "FlextTapLdapClient": ["flext_tap_ldap.client", "FlextTapLdapClient"],
    "FlextTapLdapConstants": ["flext_tap_ldap.constants", "FlextTapLdapConstants"],
    "FlextTapLdapEntry": ["flext_tap_ldap.processor", "FlextTapLdapEntry"],
    "FlextTapLdapLdifStreams": [
        "flext_tap_ldap.ldif_streams",
        "FlextTapLdapLdifStreams",
    ],
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
    "FlextTapLdapUtilitiesProcessorMixin": [
        "flext_tap_ldap._utilities._processor",
        "FlextTapLdapUtilitiesProcessorMixin",
    ],
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

__all__ = [
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


_LAZY_CACHE: MutableMapping[str, FlextTypes.ModuleExport] = {}


def __getattr__(name: str) -> FlextTypes.ModuleExport:
    """Lazy-load module attributes on first access (PEP 562).

    A local cache ``_LAZY_CACHE`` persists resolved objects across repeated
    accesses during process lifetime.

    Args:
        name: Attribute name requested by dir()/import.

    Returns:
        Lazy-loaded module export type.

    Raises:
        AttributeError: If attribute not registered.

    """
    if name in _LAZY_CACHE:
        return _LAZY_CACHE[name]

    value = lazy_getattr(name, _LAZY_IMPORTS, globals(), __name__)
    _LAZY_CACHE[name] = value
    return value


def __dir__() -> Sequence[str]:
    """Return list of available attributes for dir() and autocomplete.

    Returns:
        List of public names from module exports.

    """
    return sorted(__all__)


cleanup_submodule_namespace(__name__, _LAZY_IMPORTS)
