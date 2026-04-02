"""FLEXT Tap LDAP Types — MRO composition of parent type namespaces.

All Singer protocol types are in ``FlextMeltanoTypes.Meltano.*``.
All LDAP domain types are in ``FlextLdapTypes.Ldap.*``.
This facade composes both via MRO — access as ``t.Meltano.*`` and ``t.Ldap.*``.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping

from flext_ldap import FlextLdapTypes
from flext_meltano import FlextMeltanoTypes
from pydantic import ConfigDict, TypeAdapter


class FlextTapLdapTypes(FlextMeltanoTypes, FlextLdapTypes):
    """MRO facade composing Meltano + LDAP type namespaces.

    Access: ``t.Meltano.*`` (Singer protocol), ``t.Ldap.*`` (LDAP domain),
    and all core ``t.*`` types via MRO inheritance.
    """

    CONFIG_MAP_ADAPTER: TypeAdapter[Mapping[str, FlextMeltanoTypes.ContainerValue]] = (
        TypeAdapter(
            Mapping[str, FlextMeltanoTypes.ContainerValue],
            config=ConfigDict(strict=False),
        )
    )
    STRICT_STR_ADAPTER: TypeAdapter[str] = TypeAdapter(
        str,
        config=ConfigDict(strict=True),
    )


t = FlextTapLdapTypes
__all__ = ["FlextTapLdapTypes", "t"]
