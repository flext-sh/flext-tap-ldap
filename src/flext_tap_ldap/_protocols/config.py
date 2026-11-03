# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contracts.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_tap_ldap/_protocols/config
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from flext_meltano import FlextMeltanoProtocols

if TYPE_CHECKING:
    from flext_tap_ldap import t
    from flext_tap_ldap._protocols import FlextTapLdapProtocolsConfig


class FlextTapLdapProtocolsConfig:
    """Own the structural contracts declared by its model source."""

    @runtime_checkable
    class TapLdap(FlextMeltanoProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def streams(self) -> Sequence[FlextTapLdapProtocolsConfig.TapLdapStreamRule]:
            """Declarative stream business rules."""
            ...

    @runtime_checkable
    class TapLdapStreamRule(FlextMeltanoProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        @property
        def name(self) -> str:
            """Singer stream name."""
            ...

        @property
        def filter(self) -> str:
            """LDAP search filter."""
            ...

        @property
        def primary_keys(self) -> Sequence[str]:
            """Record primary keys."""
            ...

        @property
        def attributes(self) -> Sequence[str]:
            """LDAP attributes to request."""
            ...

        @property
        def stream_schema(self) -> t.JsonMapping:
            """Singer stream JSON schema."""
            ...

    @runtime_checkable
    class Root(FlextMeltanoProtocols.BaseModel, Protocol):
        """Structural data contract projected from the owning model."""

        TapLdap: FlextTapLdapProtocolsConfig.TapLdap


__all__: list[str] = [
    "FlextTapLdapProtocolsConfig",
]
