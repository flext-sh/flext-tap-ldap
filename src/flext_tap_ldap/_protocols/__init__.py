# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Tap Ldap. Protocols package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_tap_ldap._protocols.base import FlextTapLdapProtocolsBase
    from flext_tap_ldap._protocols.generated_models_domainevent import (
        FlextTapLdapProtocolsGeneratedModelsDomainEvent,
    )
    from flext_tap_ldap._protocols.generated_models_entity import (
        FlextTapLdapProtocolsGeneratedModelsEntity,
    )


__all__: tuple[str, ...] = (
    "FlextTapLdapProtocolsBase",
    "FlextTapLdapProtocolsGeneratedModelsDomainEvent",
    "FlextTapLdapProtocolsGeneratedModelsEntity",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "FlextTapLdapProtocolsBase": ".base",
        "FlextTapLdapProtocolsGeneratedModelsDomainEvent": (
            ".generated_models_domainevent"
        ),
        "FlextTapLdapProtocolsGeneratedModelsEntity": ".generated_models_entity",
    }),
    public_exports=__all__,
)
