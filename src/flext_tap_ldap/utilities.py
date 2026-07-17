"""Tap LDAP utilities facade — MRO of ``_utilities`` mixins and composed libs.

Composes the tap's own ``_utilities`` helpers with the flext-meltano and
flext-ldap utility facades. ``services/*`` and ``cli.py`` reach every helper
through ``u.TapLdap.*``.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_ldap import FlextLdapUtilities
from flext_meltano import u
from flext_tap_ldap._utilities.extract_support import (
    FlextTapLdapUtilitiesExtractSupport,
)


class FlextTapLdapUtilities(
    FlextTapLdapUtilitiesExtractSupport,
    u,
    FlextLdapUtilities,
):
    """Unified LDAP tap utility facade."""

    class TapLdap(FlextTapLdapUtilitiesExtractSupport.TapLdap):
        """Tap-LDAP helper namespace for cross-project access."""


u = FlextTapLdapUtilities

__all__: list[str] = ["FlextTapLdapUtilities", "u"]
