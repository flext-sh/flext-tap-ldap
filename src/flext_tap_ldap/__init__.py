"""Enterprise LDAP data extraction library for FLEXT ecosystem.

Single class per module pattern with nested classes.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from flext_core import cleanup_submodule_namespace, lazy_getattr

if TYPE_CHECKING:
    from flext_tap_ldap.__version__ import __version__, __version_info__
    from flext_tap_ldap.client import FlextTapLdapClient
    from flext_tap_ldap.constants import FlextMeltanoTapLdapConstants as c
    from flext_tap_ldap.ldif_streams import FlextTapLdapLdifStreams
    from flext_tap_ldap.models import (
        FlextMeltanoTapLdapModels,
        FlextMeltanoTapLdapModels as m,
    )
    from flext_tap_ldap.processor import FlextTapLdapProcessor
    from flext_tap_ldap.protocols import (
        FlextMeltanoTapLdapProtocols,
        FlextMeltanoTapLdapProtocols as p,
    )
    from flext_tap_ldap.settings import FlextTapLdapSettings
    from flext_tap_ldap.streams import FlextTapLdapStreams
    from flext_tap_ldap.tap import FlextTapLdapTap
    from flext_tap_ldap.typings import t
    from flext_tap_ldap.utilities import (
        FlextTapLdapUtilities,
        FlextTapLdapUtilities as u,
    )

# Lazy import mapping: export_name -> (module_path, attr_name)
_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    "FlextMeltanoTapLdapModels": ("flext_tap_ldap.models", "FlextMeltanoTapLdapModels"),
    "FlextMeltanoTapLdapProtocols": ("flext_tap_ldap.protocols", "FlextMeltanoTapLdapProtocols"),
    "FlextTapLdapClient": ("flext_tap_ldap.client", "FlextTapLdapClient"),
    "FlextTapLdapLdifStreams": ("flext_tap_ldap.ldif_streams", "FlextTapLdapLdifStreams"),
    "FlextTapLdapProcessor": ("flext_tap_ldap.processor", "FlextTapLdapProcessor"),
    "FlextTapLdapSettings": ("flext_tap_ldap.settings", "FlextTapLdapSettings"),
    "FlextTapLdapStreams": ("flext_tap_ldap.streams", "FlextTapLdapStreams"),
    "FlextTapLdapTap": ("flext_tap_ldap.tap", "FlextTapLdapTap"),
    "FlextTapLdapUtilities": ("flext_tap_ldap.utilities", "FlextTapLdapUtilities"),
    "__version__": ("flext_tap_ldap.__version__", "__version__"),
    "__version_info__": ("flext_tap_ldap.__version__", "__version_info__"),
    "c": ("flext_tap_ldap.constants", "FlextMeltanoTapLdapConstants"),
    "m": ("flext_tap_ldap.models", "FlextMeltanoTapLdapModels"),
    "p": ("flext_tap_ldap.protocols", "FlextMeltanoTapLdapProtocols"),
    "t": ("flext_tap_ldap.typings", "t"),
    "u": ("flext_tap_ldap.utilities", "FlextTapLdapUtilities"),
}

__all__ = [
    "FlextMeltanoTapLdapConstants",
    "FlextMeltanoTapLdapModels",
    "FlextMeltanoTapLdapProtocols",
    "FlextTapLdapClient",
    "FlextTapLdapLdifStreams",
    "FlextTapLdapProcessor",
    "FlextTapLdapSettings",
    "FlextTapLdapStreams",
    "FlextTapLdapTap",
    "FlextTapLdapUtilities",
    "__version__",
    "__version_info__",
    "c",
    "m",
    "p",
    "t",
    "u",
]


def __getattr__(name: str) -> Any:  # noqa: ANN401
    """Lazy-load module attributes on first access (PEP 562)."""
    return lazy_getattr(name, _LAZY_IMPORTS, globals(), __name__)


def __dir__() -> list[str]:
    """Return list of available attributes for dir() and autocomplete."""
    return sorted(__all__)


cleanup_submodule_namespace(__name__, _LAZY_IMPORTS)
