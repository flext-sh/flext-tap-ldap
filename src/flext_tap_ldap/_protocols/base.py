"""Base protocols for flext-tap-ldap private family.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from flext_meltano import FlextMeltanoProtocols


class FlextTapLdapProtocolsBase:
    """MRO root composing flext-meltano protocols into the ``_protocols`` family."""

    @runtime_checkable
    class ConfigNamespace(FlextMeltanoProtocols.Model, Protocol):
        """Structural data contract projected from the owning model."""


__all__: list[str] = ["FlextTapLdapProtocolsBase"]
