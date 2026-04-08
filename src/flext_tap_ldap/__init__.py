# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Tap Ldap package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import (
    build_lazy_import_map,
    install_lazy_exports,
    merge_lazy_imports,
)
from flext_tap_ldap.__version__ import *

if _t.TYPE_CHECKING:
    from flext_core.decorators import d
    from flext_core.exceptions import e
    from flext_core.handlers import h
    from flext_core.mixins import x
    from flext_core.result import r
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
    build_lazy_import_map(
        {
            ".__version__": (
                "__author__",
                "__author_email__",
                "__description__",
                "__license__",
                "__title__",
                "__url__",
                "__version__",
                "__version_info__",
            ),
            ".api": ("FlextTapLdapService",),
            ".client": ("FlextTapLdapClient",),
            ".constants": ("FlextTapLdapConstants",),
            ".ldif_streams": ("FlextTapLdapLdifStreams",),
            ".models": ("FlextTapLdapModels",),
            ".protocols": ("FlextTapLdapProtocols",),
            ".services": ("FlextTapLdapServices",),
            ".settings": ("FlextTapLdapSettings",),
            ".streams": ("FlextTapLdapStreams",),
            ".tap": (
                "CLI_COMMAND",
                "FlextTapLdapTap",
            ),
            ".typings": ("FlextTapLdapTypes",),
            ".utilities": ("FlextTapLdapUtilities",),
            "flext_core.decorators": ("d",),
            "flext_core.exceptions": ("e",),
            "flext_core.handlers": ("h",),
            "flext_core.mixins": ("x",),
            "flext_core.result": ("r",),
        },
        alias_groups={
            ".api": (("s", "FlextTapLdapService"),),
            ".constants": (("c", "FlextTapLdapConstants"),),
            ".models": (("m", "FlextTapLdapModels"),),
            ".protocols": (("p", "FlextTapLdapProtocols"),),
            ".typings": (("t", "FlextTapLdapTypes"),),
            ".utilities": (("u", "FlextTapLdapUtilities"),),
        },
    ),
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
