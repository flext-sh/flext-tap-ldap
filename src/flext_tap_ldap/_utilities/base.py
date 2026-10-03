"""Base utilities for flext-tap-ldap private family.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_meltano import u as meltano_u


class FlextTapLdapUtilitiesBase(meltano_u):
    """Base utilities for _utilities family."""


__all__: list[str] = ["FlextTapLdapUtilitiesBase"]
