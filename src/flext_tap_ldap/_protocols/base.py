"""Base protocols for flext-tap-ldap private family.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_meltano import p as meltano_p


class FlextTapLdapProtocolsBase(meltano_p):
    """MRO root composing flext-meltano protocols into the ``_protocols`` family."""


__all__: list[str] = ["FlextTapLdapProtocolsBase"]
