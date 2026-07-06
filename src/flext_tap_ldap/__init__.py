# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Tap Ldap package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports
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
from flext_tap_ldap._exports import FLEXT_TAP_LDAP_LAZY_IMPORTS

if TYPE_CHECKING:
    from flext_ldap import d as d, e as e, h as h, r as r, s as s, x as x
    from flext_tap_ldap.api import (
        FlextTapLdapService as FlextTapLdapService,
        tap_ldap as tap_ldap,
    )
    from flext_tap_ldap.constants import (
        FlextTapLdapConstants as FlextTapLdapConstants,
        c as c,
    )
    from flext_tap_ldap.models import FlextTapLdapModels as FlextTapLdapModels, m as m
    from flext_tap_ldap.protocols import (
        FlextTapLdapProtocols as FlextTapLdapProtocols,
        p as p,
    )
    from flext_tap_ldap.settings import FlextTapLdapSettings as FlextTapLdapSettings
    from flext_tap_ldap.tap import FlextTapLdapTap as FlextTapLdapTap
    from flext_tap_ldap.typings import FlextTapLdapTypes as FlextTapLdapTypes, t as t
    from flext_tap_ldap.utilities import (
        FlextTapLdapUtilities as FlextTapLdapUtilities,
        u as u,
    )


_LAZY_IMPORTS = FLEXT_TAP_LDAP_LAZY_IMPORTS


_EAGER_EXPORTS = (
    __author__,
    __author_email__,
    __description__,
    __license__,
    __title__,
    __url__,
    __version__,
    __version_info__,
)


_PUBLIC_EXPORTS: tuple[str, ...] = (
    "FlextTapLdapConstants",
    "FlextTapLdapModels",
    "FlextTapLdapProtocols",
    "FlextTapLdapService",
    "FlextTapLdapSettings",
    "FlextTapLdapTap",
    "FlextTapLdapTypes",
    "FlextTapLdapUtilities",
    "tap_ldap",
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
)

__all__: tuple[str, ...] = (
    "FlextTapLdapConstants",
    "FlextTapLdapModels",
    "FlextTapLdapProtocols",
    "FlextTapLdapService",
    "FlextTapLdapSettings",
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
)


install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    public_exports=_PUBLIC_EXPORTS,
)
