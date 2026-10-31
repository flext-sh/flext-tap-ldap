# AUTO-GENERATED FILE — Regenerate with: make gen
"""Source-derived structural model contract.

Copyright (c) 2026 FLEXT Team. All rights reserved.
src/flext_tap_ldap/_protocols/generated_models_domainevent
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal as typing_Literal, Protocol, runtime_checkable

if TYPE_CHECKING:
    from datetime import datetime as datetime_datetime

    from flext_core import c as flext_core_c
    from flext_core._models import (
        FlextModelsContainers as flext_core__models_FlextModelsContainers,
    )


class FlextTapLdapProtocolsGeneratedModelsDomainEvent:
    """Own the structural model contract declared by this module."""

    @runtime_checkable
    class DomainEvent(Protocol):
        """Structural data contract projected from the owning model."""

        created_at: datetime_datetime
        updated_at: datetime_datetime | None
        unique_id: str
        message_type: typing_Literal[flext_core_c.HandlerType.EVENT]
        event_type: str
        aggregate_id: str
        data: flext_core__models_FlextModelsContainers.ConfigMap


__all__: list[str] = [
    "FlextTapLdapProtocolsGeneratedModelsDomainEvent",
]
