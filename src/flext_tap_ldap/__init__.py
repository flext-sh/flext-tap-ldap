"""Enterprise LDAP data extraction library for FLEXT ecosystem.

Single class per module pattern with nested classes.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from flext_core.lazy import cleanup_submodule_namespace, lazy_getattr

if TYPE_CHECKING:
    from flext_tap_ldap.__version__ import __version__, __version_info__
    from flext_tap_ldap.client import FlextTapLdapClient
    from flext_tap_ldap.constants import (
        FlextTapLdapConstants,
        FlextTapLdapConstants as c,
    )
    from flext_tap_ldap.ldif_streams import FlextTapLdapLdifStreams
    from flext_tap_ldap.models import FlextTapLdapModels, FlextTapLdapModels as m
    from flext_tap_ldap.processor import FlextTapLdapProcessor
    from flext_tap_ldap.protocols import (
        FlextTapLdapProtocols,
        FlextTapLdapProtocols as p,
    )
    from flext_tap_ldap.settings import FlextTapLdapSettings
    from flext_tap_ldap.streams import FlextTapLdapStreams
    from flext_tap_ldap.tap import FlextTapLdapTap
    from flext_tap_ldap.typings import FlextTapLdapTypes, FlextTapLdapTypes as t
    from flext_tap_ldap.utilities import (
        FlextTapLdapUtilities,
        FlextTapLdapUtilities as u,
    )

# Lazy import mapping: export_name -> (module_path, attr_name)
_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    "FlextTapLdapClient": ("flext_tap_ldap.client", "FlextTapLdapClient"),
    "FlextTapLdapConstants": ("flext_tap_ldap.constants", "FlextTapLdapConstants"),
    "FlextTapLdapLdifStreams": (
        "flext_tap_ldap.ldif_streams",
        "FlextTapLdapLdifStreams",
    ),
    "FlextTapLdapModels": ("flext_tap_ldap.models", "FlextTapLdapModels"),
    "FlextTapLdapProcessor": ("flext_tap_ldap.processor", "FlextTapLdapProcessor"),
    "FlextTapLdapProtocols": ("flext_tap_ldap.protocols", "FlextTapLdapProtocols"),
    "FlextTapLdapSettings": ("flext_tap_ldap.settings", "FlextTapLdapSettings"),
    "FlextTapLdapStreams": ("flext_tap_ldap.streams", "FlextTapLdapStreams"),
    "FlextTapLdapTap": ("flext_tap_ldap.tap", "FlextTapLdapTap"),
    "FlextTapLdapTypes": ("flext_tap_ldap.typings", "FlextTapLdapTypes"),
    "FlextTapLdapUtilities": ("flext_tap_ldap.utilities", "FlextTapLdapUtilities"),
    "__version__": ("flext_tap_ldap.__version__", "__version__"),
    "__version_info__": ("flext_tap_ldap.__version__", "__version_info__"),
    "c": ("flext_tap_ldap.constants", "FlextTapLdapConstants"),
    "m": ("flext_tap_ldap.models", "FlextTapLdapModels"),
    "p": ("flext_tap_ldap.protocols", "FlextTapLdapProtocols"),
    "t": ("flext_tap_ldap.typings", "FlextTapLdapTypes"),
    "u": ("flext_tap_ldap.utilities", "FlextTapLdapUtilities"),
}

__all__ = [
    "FlextTapLdapClient",
    "FlextTapLdapConstants",
    "FlextTapLdapLdifStreams",
    "FlextTapLdapModels",
    "FlextTapLdapProcessor",
    "FlextTapLdapProtocols",
    "FlextTapLdapSettings",
    "FlextTapLdapStreams",
    "FlextTapLdapTap",
    "FlextTapLdapTypes",
    "FlextTapLdapUtilities",
    "__version__",
    "__version_info__",
    "c",
    "m",
    "p",
    "t",
    "u",
]


def __getattr__(name: str) -> Any:  # noqa: ANN401  # JUSTIFIED: Ruff (any-type) with PEP 562 dynamic module exports — https://docs.astral.sh/ruff/rules/any-type/
    """Lazy-load module attributes on first access (PEP 562)."""
    return lazy_getattr(name, _LAZY_IMPORTS, globals(), __name__)


def __dir__() -> list[str]:
    """Return list of available attributes for dir() and autocomplete."""
    return sorted(__all__)


cleanup_submodule_namespace(__name__, _LAZY_IMPORTS)
