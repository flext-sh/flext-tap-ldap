# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contract.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_tap_ldap/_protocols/generated_models_entity
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from collections.abc import MutableSequence as collections_abc_MutableSequence
    from datetime import datetime as datetime_datetime

    import pydantic

    from flext_tap_ldap._protocols import (
        FlextTapLdapProtocolsGeneratedModelsDomainEvent,
    )


class FlextTapLdapProtocolsGeneratedModelsEntity:
    """Own the structural model contract declared by this module."""

    @runtime_checkable
    class Entity(Protocol):
        """Structural data contract projected from the owning model."""

        version: pydantic.NonNegativeInt
        unique_id: str
        created_at: datetime_datetime
        updated_at: datetime_datetime | None
        domain_events: collections_abc_MutableSequence[
            FlextTapLdapProtocolsGeneratedModelsDomainEvent.DomainEvent
        ]


__all__: list[str] = [
    "FlextTapLdapProtocolsGeneratedModelsEntity",
]
