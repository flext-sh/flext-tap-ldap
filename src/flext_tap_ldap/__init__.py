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

    from flext_tap_ldap.client import (
        FlextTapLdapClient,
        LDAPClient,
        LDAPClientConfig,
        LDAPConnectionConfig,
        LDAPEntry,
    )
    from flext_tap_ldap.constants import FlextTapLdapConstants, c
    from flext_tap_ldap.ldif_streams import FlextTapLdapLdifStreams
    from flext_tap_ldap.models import FlextTapLdapModels, TapExecution, m
    from flext_tap_ldap.processor import (
        Entry,
        FlextLdifDistinguishedName,
        FlextTapLdapProcessor,
        Transformer,
        Validator,
    )
    from flext_tap_ldap.protocols import FlextTapLdapProtocols, Tap, TapConfig, p
    from flext_tap_ldap.services import FlextTapLdapServices
    from flext_tap_ldap.settings import FlextTapLdapSettings
    from flext_tap_ldap.streams import FlextTapLdapStreams
    from flext_tap_ldap.tap import FlextTapLdapTap, logger, main
    from flext_tap_ldap.typings import FlextTapLdapTypes, t
    from flext_tap_ldap.utilities import FlextTapLdapUtilities, u
    from flext_tap_ldap.version import VERSION, FlextTapLdapVersion

# Lazy import mapping: export_name -> (module_path, attr_name)
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
    "FlextTapLdapVersion": ("flext_tap_ldap.version", "FlextTapLdapVersion"),
    "LDAPClient": ("flext_tap_ldap.client", "LDAPClient"),
    "LDAPClientConfig": ("flext_tap_ldap.client", "LDAPClientConfig"),
    "LDAPConnectionConfig": ("flext_tap_ldap.client", "LDAPConnectionConfig"),
    "LDAPEntry": ("flext_tap_ldap.client", "LDAPEntry"),
    "Tap": ("flext_tap_ldap.protocols", "Tap"),
    "TapConfig": ("flext_tap_ldap.protocols", "TapConfig"),
    "TapExecution": ("flext_tap_ldap.models", "TapExecution"),
    "Transformer": ("flext_tap_ldap.processor", "Transformer"),
    "VERSION": ("flext_tap_ldap.version", "VERSION"),
    "Validator": ("flext_tap_ldap.processor", "Validator"),
    "c": ("flext_tap_ldap.constants", "c"),
    "logger": ("flext_tap_ldap.tap", "logger"),
    "m": ("flext_tap_ldap.models", "m"),
    "main": ("flext_tap_ldap.tap", "main"),
    "p": ("flext_tap_ldap.protocols", "p"),
    "t": ("flext_tap_ldap.typings", "t"),
    "u": ("flext_tap_ldap.utilities", "u"),
}

__all__ = [
    "VERSION",
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
    "FlextTapLdapVersion",
    "LDAPClient",
    "LDAPClientConfig",
    "LDAPConnectionConfig",
    "LDAPEntry",
    "Tap",
    "TapConfig",
    "TapExecution",
    "Transformer",
    "Validator",
    "c",
    "logger",
    "m",
    "main",
    "p",
    "t",
    "u",
]


def __getattr__(name: str) -> FlextTypes.ModuleExport:
    """Lazy-load module attributes on first access (PEP 562)."""
    return lazy_getattr(name, _LAZY_IMPORTS, globals(), __name__)


def __dir__() -> list[str]:
    """Return list of available attributes for dir() and autocomplete."""
    return sorted(__all__)


cleanup_submodule_namespace(__name__, _LAZY_IMPORTS)
