# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tap LDAP utilities facade — MRO of ``_utilities`` mixins and composed libs.

Composes the tap's own ``_utilities`` helpers with the flext-meltano and
flext-ldap utility facades. ``services/*`` and ``cli.py`` reach every helper
through ``u.TapLdap.*``.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_ldap import u as flext_ldap_u
from flext_meltano import u as flext_meltano_u

from flext_tap_ldap._utilities import (
    FlextTapLdapUtilitiesBase,
    FlextTapLdapUtilitiesExtractSupport,
)


class FlextTapLdapUtilities(
    flext_meltano_u,
    flext_ldap_u,
):
    """Unified LDAP tap utility facade."""

    class TapLdap(
        FlextTapLdapUtilitiesExtractSupport,
        FlextTapLdapUtilitiesBase,
    ):
        """Tap-LDAP helper namespace for cross-project access."""


u = FlextTapLdapUtilities
__all__: list[str] = ["FlextTapLdapUtilities", "u"]
