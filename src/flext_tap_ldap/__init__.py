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
    ("._utilities",),
    {
        "CLI_COMMAND": ".tap",
        "FlextTapLdapClient": ".client",
        "FlextTapLdapConstants": ".constants",
        "FlextTapLdapLdifStreams": ".ldif_streams",
        "FlextTapLdapModels": ".models",
        "FlextTapLdapProtocols": ".protocols",
        "FlextTapLdapService": ".api",
        "FlextTapLdapServices": ".services",
        "FlextTapLdapSettings": ".settings",
        "FlextTapLdapStreams": ".streams",
        "FlextTapLdapTap": ".tap",
        "FlextTapLdapTypes": ".typings",
        "FlextTapLdapUtilities": ".utilities",
        "__author__": ".__version__",
        "__author_email__": ".__version__",
        "__description__": ".__version__",
        "__license__": ".__version__",
        "__title__": ".__version__",
        "__url__": ".__version__",
        "__version__": ".__version__",
        "__version_info__": ".__version__",
        "c": (".constants", "FlextTapLdapConstants"),
        "d": ("flext_core.decorators", "FlextDecorators"),
        "e": ("flext_core.exceptions", "FlextExceptions"),
        "h": ("flext_core.handlers", "FlextHandlers"),
        "m": (".models", "FlextTapLdapModels"),
        "p": (".protocols", "FlextTapLdapProtocols"),
        "r": ("flext_core.result", "FlextResult"),
        "s": (".api", "FlextTapLdapService"),
        "t": (".typings", "FlextTapLdapTypes"),
        "u": (".utilities", "FlextTapLdapUtilities"),
        "x": ("flext_core.mixins", "FlextMixins"),
    },
    exclude_names=(
        "cleanup_submodule_namespace",
        "install_lazy_exports",
        "lazy_getattr",
        "logger",
        "merge_lazy_imports",
        "output",
        "output_reporting",
    ),
    module_name=__name__,
)

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
