# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Flext tap ldap package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import install_lazy_exports, merge_lazy_imports
from flext_tap_ldap.__version__ import *

if _t.TYPE_CHECKING:
    from flext_core.decorators import FlextDecorators as d
    from flext_core.exceptions import FlextExceptions as e
    from flext_core.handlers import FlextHandlers as h
    from flext_core.mixins import FlextMixins as x
    from flext_core.result import FlextResult as r
    from flext_tap_ldap._utilities._processor import FlextTapLdapUtilitiesProcessorMixin
    from flext_tap_ldap.api import FlextTapLdapService, FlextTapLdapService as s
    from flext_tap_ldap.client import FlextTapLdapClient
    from flext_tap_ldap.constants import (
        FlextTapLdapConstants,
        FlextTapLdapConstants as c,
    )
    from flext_tap_ldap.ldif_streams import FlextTapLdapLdifStreams
    from flext_tap_ldap.models import FlextTapLdapModels, FlextTapLdapModels as m
    from flext_tap_ldap.protocols import (
        FlextTapLdapProtocols,
        FlextTapLdapProtocols as p,
    )
    from flext_tap_ldap.services import FlextTapLdapServices
    from flext_tap_ldap.settings import FlextTapLdapSettings
    from flext_tap_ldap.streams import FlextTapLdapStreams
    from flext_tap_ldap.tap import CLI_COMMAND, FlextTapLdapTap
    from flext_tap_ldap.typings import FlextTapLdapTypes, FlextTapLdapTypes as t
    from flext_tap_ldap.utilities import (
        FlextTapLdapUtilities,
        FlextTapLdapUtilities as u,
    )
_LAZY_IMPORTS = merge_lazy_imports(
    ("flext_tap_ldap._utilities",),
    {
        "CLI_COMMAND": ("flext_tap_ldap.tap", "CLI_COMMAND"),
        "FlextTapLdapClient": ("flext_tap_ldap.client", "FlextTapLdapClient"),
        "FlextTapLdapConstants": ("flext_tap_ldap.constants", "FlextTapLdapConstants"),
        "FlextTapLdapLdifStreams": (
            "flext_tap_ldap.ldif_streams",
            "FlextTapLdapLdifStreams",
        ),
        "FlextTapLdapModels": ("flext_tap_ldap.models", "FlextTapLdapModels"),
        "FlextTapLdapProtocols": ("flext_tap_ldap.protocols", "FlextTapLdapProtocols"),
        "FlextTapLdapService": ("flext_tap_ldap.api", "FlextTapLdapService"),
        "FlextTapLdapServices": ("flext_tap_ldap.services", "FlextTapLdapServices"),
        "FlextTapLdapSettings": ("flext_tap_ldap.settings", "FlextTapLdapSettings"),
        "FlextTapLdapStreams": ("flext_tap_ldap.streams", "FlextTapLdapStreams"),
        "FlextTapLdapTap": ("flext_tap_ldap.tap", "FlextTapLdapTap"),
        "FlextTapLdapTypes": ("flext_tap_ldap.typings", "FlextTapLdapTypes"),
        "FlextTapLdapUtilities": ("flext_tap_ldap.utilities", "FlextTapLdapUtilities"),
        "__author__": ("flext_tap_ldap.__version__", "__author__"),
        "__author_email__": ("flext_tap_ldap.__version__", "__author_email__"),
        "__description__": ("flext_tap_ldap.__version__", "__description__"),
        "__license__": ("flext_tap_ldap.__version__", "__license__"),
        "__title__": ("flext_tap_ldap.__version__", "__title__"),
        "__url__": ("flext_tap_ldap.__version__", "__url__"),
        "__version__": ("flext_tap_ldap.__version__", "__version__"),
        "__version_info__": ("flext_tap_ldap.__version__", "__version_info__"),
        "c": ("flext_tap_ldap.constants", "FlextTapLdapConstants"),
        "d": ("flext_core.decorators", "FlextDecorators"),
        "e": ("flext_core.exceptions", "FlextExceptions"),
        "h": ("flext_core.handlers", "FlextHandlers"),
        "m": ("flext_tap_ldap.models", "FlextTapLdapModels"),
        "p": ("flext_tap_ldap.protocols", "FlextTapLdapProtocols"),
        "r": ("flext_core.result", "FlextResult"),
        "s": ("flext_tap_ldap.api", "FlextTapLdapService"),
        "t": ("flext_tap_ldap.typings", "FlextTapLdapTypes"),
        "u": ("flext_tap_ldap.utilities", "FlextTapLdapUtilities"),
        "x": ("flext_core.mixins", "FlextMixins"),
    },
)
_ = _LAZY_IMPORTS.pop("cleanup_submodule_namespace", None)
_ = _LAZY_IMPORTS.pop("install_lazy_exports", None)
_ = _LAZY_IMPORTS.pop("lazy_getattr", None)
_ = _LAZY_IMPORTS.pop("logger", None)
_ = _LAZY_IMPORTS.pop("merge_lazy_imports", None)
_ = _LAZY_IMPORTS.pop("output", None)
_ = _LAZY_IMPORTS.pop("output_reporting", None)

__all__ = [
    "CLI_COMMAND",
    "FlextTapLdapClient",
    "FlextTapLdapConstants",
    "FlextTapLdapLdifStreams",
    "FlextTapLdapModels",
    "FlextTapLdapProtocols",
    "FlextTapLdapService",
    "FlextTapLdapServices",
    "FlextTapLdapSettings",
    "FlextTapLdapStreams",
    "FlextTapLdapTap",
    "FlextTapLdapTypes",
    "FlextTapLdapUtilities",
    "FlextTapLdapUtilitiesProcessorMixin",
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
    "m",
    "p",
    "r",
    "s",
    "t",
    "u",
    "x",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)
