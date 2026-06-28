# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Tap Ldap package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import (
    build_lazy_import_map,
    install_lazy_exports,
    merge_lazy_imports,
)
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

if _t.TYPE_CHECKING:
    from flext_meltano import d as d, e as e, h as h, r as r, s as s, x as x
    from flext_tap_ldap._utilities._processor import (
        FlextTapLdapUtilitiesProcessorMixin as FlextTapLdapUtilitiesProcessorMixin,
    )
    from flext_tap_ldap.api import (
        FlextTapLdapService as FlextTapLdapService,
        tap_ldap as tap_ldap,
    )
    from flext_tap_ldap.client import FlextTapLdapClient as FlextTapLdapClient
    from flext_tap_ldap.constants import (
        FlextTapLdapConstants as FlextTapLdapConstants,
        c as c,
    )
    from flext_tap_ldap.ldif_streams import (
        FlextTapLdapLdifStreams as FlextTapLdapLdifStreams,
    )
    from flext_tap_ldap.models import FlextTapLdapModels as FlextTapLdapModels, m as m
    from flext_tap_ldap.protocols import (
        FlextTapLdapProtocols as FlextTapLdapProtocols,
        p as p,
    )
    from flext_tap_ldap.settings import FlextTapLdapSettings as FlextTapLdapSettings
    from flext_tap_ldap.streams import FlextTapLdapStreams as FlextTapLdapStreams
    from flext_tap_ldap.tap import FlextTapLdapTap as FlextTapLdapTap
    from flext_tap_ldap.typings import FlextTapLdapTypes as FlextTapLdapTypes, t as t
    from flext_tap_ldap.utilities import (
        FlextTapLdapUtilities as FlextTapLdapUtilities,
        u as u,
    )
_LAZY_IMPORTS = merge_lazy_imports(
    ("._utilities",),
    build_lazy_import_map(
        {
            "._utilities._processor": ("FlextTapLdapUtilitiesProcessorMixin",),
            ".api": (
                "FlextTapLdapService",
                "tap_ldap",
            ),
            ".client": ("FlextTapLdapClient",),
            ".constants": (
                "FlextTapLdapConstants",
                "c",
            ),
            ".ldif_streams": ("FlextTapLdapLdifStreams",),
            ".models": (
                "FlextTapLdapModels",
                "m",
            ),
            ".protocols": (
                "FlextTapLdapProtocols",
                "p",
            ),
            ".settings": ("FlextTapLdapSettings",),
            ".streams": ("FlextTapLdapStreams",),
            ".tap": ("FlextTapLdapTap",),
            ".typings": (
                "FlextTapLdapTypes",
                "t",
            ),
            ".utilities": (
                "FlextTapLdapUtilities",
                "u",
            ),
            "flext_meltano": (
                "d",
                "e",
                "h",
                "r",
                "s",
                "x",
            ),
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
        "pytest_addoption",
        "pytest_collect_file",
        "pytest_collection_modifyitems",
        "pytest_configure",
        "pytest_runtest_setup",
        "pytest_runtest_teardown",
        "pytest_sessionfinish",
        "pytest_sessionstart",
        "pytest_terminal_summary",
        "pytest_warning_recorded",
    ),
    module_name=__name__,
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

__all__: list[str] = [
    "FlextTapLdapClient",
    "FlextTapLdapConstants",
    "FlextTapLdapLdifStreams",
    "FlextTapLdapModels",
    "FlextTapLdapProtocols",
    "FlextTapLdapService",
    "FlextTapLdapSettings",
    "FlextTapLdapStreams",
    "FlextTapLdapTap",
    "FlextTapLdapTypes",
    "FlextTapLdapUtilities",
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
    "tap_ldap",
    "u",
    "x",
]
