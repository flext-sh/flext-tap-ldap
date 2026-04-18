# AUTO-GENERATED FILE — Regenerate with: make gen
"""Package version and metadata for flext-tap-ldap.

Subclass of ``FlextVersion`` — overrides only ``_metadata``.
All derived attributes (``__version__``, ``__title__``, etc.) are
computed automatically via ``FlextVersion.__init_subclass__``.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from importlib.metadata import PackageMetadata, metadata

from flext_core import FlextVersion


class FlextTapLdapVersion(FlextVersion):
    """flext-tap-ldap version — MRO-derived from FlextVersion."""

    _metadata: PackageMetadata = metadata("flext-tap-ldap")


__version__ = FlextTapLdapVersion.__version__
__version_info__ = FlextTapLdapVersion.__version_info__
__title__ = FlextTapLdapVersion.__title__
__description__ = FlextTapLdapVersion.__description__
__author__ = FlextTapLdapVersion.__author__
__author_email__ = FlextTapLdapVersion.__author_email__
__license__ = FlextTapLdapVersion.__license__
__url__ = FlextTapLdapVersion.__url__
__all__: list[str] = [
    "FlextTapLdapVersion",
    "__author__",
    "__author_email__",
    "__description__",
    "__license__",
    "__title__",
    "__url__",
    "__version__",
    "__version_info__",
]
