# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make codegen
#
"""Enterprise LDAP data extraction library for FLEXT ecosystem.

Single class per module pattern with nested classes.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import cleanup_submodule_namespace, lazy_getattr

if TYPE_CHECKING:
    from flext_core.typings import FlextTypes
    from flext_ldap import d, e, h, r, s, x

    from flext_tap_ldap.__version__ import (
        __all__,
        __author__,
        __author_email__,
        __description__,
        __license__,
        __title__,
        __url__,
        __version__,
        __version_info__,
    )
    from flext_tap_ldap.client import (
        FlextTapLdapClient,
        LDAPClient,
        LDAPClientConfig,
        LDAPConnectionConfig,
        LDAPEntry,
    )
    from flext_tap_ldap.constants import FlextTapLdapConstants, c
    from flext_tap_ldap.ldif_streams import FlextTapLdapLdifStreams
    from flext_tap_ldap.models import FlextTapLdapModels, m
    from flext_tap_ldap.processor import (
        Entry,
        FlextLdifDistinguishedName,
        FlextTapLdapProcessor,
        Transformer,
        Validator,
    )
    from flext_tap_ldap.protocols import FlextTapLdapProtocols, p
    from flext_tap_ldap.services import FlextTapLdapServices
    from flext_tap_ldap.settings import FlextTapLdapSettings
    from flext_tap_ldap.streams import FlextTapLdapStreams
    from flext_tap_ldap.tap import FlextTapLdapTap, logger, main
    from flext_tap_ldap.typings import FlextTapLdapTypes, t
    from flext_tap_ldap.utilities import FlextTapLdapUtilities, u

_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    "Entry": ("flext_tap_ldap.processor", "Entry"),
    "FlextLdifDistinguishedName": (
        "flext_tap_ldap.processor",
        "FlextLdifDistinguishedName",
    ),
    "FlextTapLdapClient": ("flext_tap_ldap.client", "FlextTapLdapClient"),
    "FlextTapLdapConstants": ("flext_tap_ldap.constants", "FlextTapLdapConstants"),
    "FlextTapLdapLdifStreams": (
        "flext_tap_ldap.ldif_streams",
        "FlextTapLdapLdifStreams",
    ),
    "FlextTapLdapModels": ("flext_tap_ldap.models", "FlextTapLdapModels"),
    "FlextTapLdapProcessor": ("flext_tap_ldap.processor", "FlextTapLdapProcessor"),
    "FlextTapLdapProtocols": ("flext_tap_ldap.protocols", "FlextTapLdapProtocols"),
    "FlextTapLdapServices": ("flext_tap_ldap.services", "FlextTapLdapServices"),
    "FlextTapLdapSettings": ("flext_tap_ldap.settings", "FlextTapLdapSettings"),
    "FlextTapLdapStreams": ("flext_tap_ldap.streams", "FlextTapLdapStreams"),
    "FlextTapLdapTap": ("flext_tap_ldap.tap", "FlextTapLdapTap"),
    "FlextTapLdapTypes": ("flext_tap_ldap.typings", "FlextTapLdapTypes"),
    "FlextTapLdapUtilities": ("flext_tap_ldap.utilities", "FlextTapLdapUtilities"),
    "LDAPClient": ("flext_tap_ldap.client", "LDAPClient"),
    "LDAPClientConfig": ("flext_tap_ldap.client", "LDAPClientConfig"),
    "LDAPConnectionConfig": ("flext_tap_ldap.client", "LDAPConnectionConfig"),
    "LDAPEntry": ("flext_tap_ldap.client", "LDAPEntry"),
    "Transformer": ("flext_tap_ldap.processor", "Transformer"),
    "Validator": ("flext_tap_ldap.processor", "Validator"),
    "__all__": ("flext_tap_ldap.__version__", "__all__"),
    "__author__": ("flext_tap_ldap.__version__", "__author__"),
    "__author_email__": ("flext_tap_ldap.__version__", "__author_email__"),
    "__description__": ("flext_tap_ldap.__version__", "__description__"),
    "__license__": ("flext_tap_ldap.__version__", "__license__"),
    "__title__": ("flext_tap_ldap.__version__", "__title__"),
    "__url__": ("flext_tap_ldap.__version__", "__url__"),
    "__version__": ("flext_tap_ldap.__version__", "__version__"),
    "__version_info__": ("flext_tap_ldap.__version__", "__version_info__"),
    "c": ("flext_tap_ldap.constants", "c"),
    "d": ("flext_ldap", "d"),
    "e": ("flext_ldap", "e"),
    "h": ("flext_ldap", "h"),
    "logger": ("flext_tap_ldap.tap", "logger"),
    "m": ("flext_tap_ldap.models", "m"),
    "main": ("flext_tap_ldap.tap", "main"),
    "p": ("flext_tap_ldap.protocols", "p"),
    "r": ("flext_ldap", "r"),
    "s": ("flext_ldap", "s"),
    "t": ("flext_tap_ldap.typings", "t"),
    "u": ("flext_tap_ldap.utilities", "u"),
    "x": ("flext_ldap", "x"),
}

__all__ = [
    "Entry",
    "FlextLdifDistinguishedName",
    "FlextTapLdapClient",
    "FlextTapLdapConstants",
    "FlextTapLdapLdifStreams",
    "FlextTapLdapModels",
    "FlextTapLdapProcessor",
    "FlextTapLdapProtocols",
    "FlextTapLdapServices",
    "FlextTapLdapSettings",
    "FlextTapLdapStreams",
    "FlextTapLdapTap",
    "FlextTapLdapTypes",
    "FlextTapLdapUtilities",
    "LDAPClient",
    "LDAPClientConfig",
    "LDAPConnectionConfig",
    "LDAPEntry",
    "Transformer",
    "Validator",
    "__all__",
    "__author__",
    "__author_email__",
    "__description__",
    "__license__",
    "__title__",
    "__url__",
    "__version__",
    "__version_info__",
    "c",
    "d",
    "e",
    "h",
    "logger",
    "m",
    "main",
    "p",
    "r",
    "s",
    "t",
    "u",
    "x",
]


def __getattr__(name: str) -> FlextTypes.ModuleExport:
    """Lazy-load module attributes on first access (PEP 562)."""
    return lazy_getattr(name, _LAZY_IMPORTS, globals(), __name__)


def __dir__() -> list[str]:
    """Return list of available attributes for dir() and autocomplete."""
    return sorted(__all__)


cleanup_submodule_namespace(__name__, _LAZY_IMPORTS)
