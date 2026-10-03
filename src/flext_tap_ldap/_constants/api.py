"""LDAP tap constants - API constants.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tap_ldap._constants.base import FlextTapLdapConstantsBase


class FlextTapLdapConstantsApi(FlextTapLdapConstantsBase):
    """LDAP tap API constants."""


__all__: list[str] = ["FlextTapLdapConstantsApi"]
