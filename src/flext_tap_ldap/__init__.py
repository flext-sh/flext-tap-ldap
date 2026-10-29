# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Tap Ldap package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_ldap import ldap, ldif
    from flext_meltano import (
        build_lazy_import_map,
        cleanup_submodule_namespace,
        cli,
        core,
        d,
        e,
        h,
        install_lazy_exports,
        lazy,
        lazy_getattr,
        lazy_member,
        meltano,
        merge_lazy_imports,
        normalize_lazy_imports,
        r,
        resolve_lazy_members,
        x,
    )

    from flext_tap_ldap.__version__ import (
        FlextTapLdapVersion,
        __author__,
        __author_email__,
        __description__,
        __license__,
        __title__,
        __url__,
        __version__,
        __version_info__,
    )
    from flext_tap_ldap._config import FlextTapLdapConfig, config
    from flext_tap_ldap._settings import FlextTapLdapSettings, settings
    from flext_tap_ldap.api import FlextTapLdapService, tap_ldap
    from flext_tap_ldap.base import FlextTapLdapServiceBase, s
    from flext_tap_ldap.cli import main
    from flext_tap_ldap.constants import FlextTapLdapConstants, c
    from flext_tap_ldap.models import FlextModelsTapLdap, m
    from flext_tap_ldap.protocols import FlextTapLdapProtocols, p
    from flext_tap_ldap.typings import FlextTapLdapTypes, t
    from flext_tap_ldap.utilities import FlextTapLdapUtilities, u


__all__: tuple[str, ...] = (
    "FlextModelsTapLdap",
    "FlextTapLdapConfig",
    "FlextTapLdapConstants",
    "FlextTapLdapProtocols",
    "FlextTapLdapService",
    "FlextTapLdapServiceBase",
    "FlextTapLdapSettings",
    "FlextTapLdapTypes",
    "FlextTapLdapUtilities",
    "FlextTapLdapVersion",
    "__author__",
    "__author_email__",
    "__description__",
    "__license__",
    "__title__",
    "__url__",
    "__version__",
    "__version_info__",
    "build_lazy_import_map",
    "c",
    "cleanup_submodule_namespace",
    "cli",
    "config",
    "core",
    "d",
    "e",
    "h",
    "install_lazy_exports",
    "lazy",
    "lazy_getattr",
    "lazy_member",
    "ldap",
    "ldif",
    "m",
    "main",
    "meltano",
    "merge_lazy_imports",
    "normalize_lazy_imports",
    "p",
    "r",
    "resolve_lazy_members",
    "s",
    "settings",
    "t",
    "tap_ldap",
    "u",
    "x",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "FlextModelsTapLdap": ".models",
        "FlextTapLdapConfig": "._config",
        "FlextTapLdapConstants": ".constants",
        "FlextTapLdapProtocols": ".protocols",
        "FlextTapLdapService": ".api",
        "FlextTapLdapServiceBase": ".base",
        "FlextTapLdapSettings": "._settings",
        "FlextTapLdapTypes": ".typings",
        "FlextTapLdapUtilities": ".utilities",
        "FlextTapLdapVersion": ".__version__",
        "__author__": ".__version__",
        "__author_email__": ".__version__",
        "__description__": ".__version__",
        "__license__": ".__version__",
        "__title__": ".__version__",
        "__url__": ".__version__",
        "__version_info__": ".__version__",
        "build_lazy_import_map": "flext_meltano",
        "c": ".constants",
        "cleanup_submodule_namespace": "flext_meltano",
        "cli": "flext_meltano",
        "config": "._config",
        "core": "flext_meltano",
        "d": "flext_meltano",
        "e": "flext_meltano",
        "h": "flext_meltano",
        "install_lazy_exports": "flext_meltano",
        "lazy": "flext_meltano",
        "lazy_getattr": "flext_meltano",
        "lazy_member": "flext_meltano",
        "ldap": "flext_ldap",
        "ldif": "flext_ldap",
        "m": ".models",
        "main": ".cli",
        "meltano": "flext_meltano",
        "merge_lazy_imports": "flext_meltano",
        "normalize_lazy_imports": "flext_meltano",
        "p": ".protocols",
        "r": "flext_meltano",
        "resolve_lazy_members": "flext_meltano",
        "s": ".base",
        "settings": "._settings",
        "t": ".typings",
        "tap_ldap": ".api",
        "u": ".utilities",
        "x": "flext_meltano",
    }),
    public_exports=__all__,
)

if not TYPE_CHECKING:
    from flext_tap_ldap.__version__ import __version__
