"""FLEXT Tap LDAP Types — MRO composition of parent type namespaces.

All Singer protocol types are in ``FlextMeltanoTypes.Meltano.*``.
All LDAP domain types are in ``FlextLdapTypes.Ldap.*``.
This facade composes both via MRO — access as ``FlextMeltanoTypes.Meltano.*`` and ``FlextMeltanoTypes.Ldap.*``.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from flext_ldap import FlextLdapTypes
from flext_meltano import FlextMeltanoTypes
from flext_tap_ldap import c, u


class FlextTapLdapTypes(FlextMeltanoTypes, FlextLdapTypes):
    """MRO facade composing Meltano + LDAP type namespaces.

    Access: ``FlextMeltanoTypes.Meltano.*`` (Singer protocol), ``FlextMeltanoTypes.Ldap.*`` (LDAP domain),
    and all core ``FlextMeltanoTypes.*`` types via MRO inheritance.
    """

    CONFIG_MAP_ADAPTER: u.TypeAdapter[FlextMeltanoTypes.ContainerValueMapping] = (
        u.TypeAdapter(
            FlextMeltanoTypes.ContainerValueMapping,
            config=c.ConfigDict(strict=False),
        )
    )
    STRICT_STR_ADAPTER: u.TypeAdapter[FlextMeltanoTypes.TextValue] = u.TypeAdapter(
        FlextMeltanoTypes.TextValue,
        config=c.ConfigDict(strict=True),
    )
    INTEGER_ADAPTER: u.TypeAdapter[FlextMeltanoTypes.IntegerValue] = u.TypeAdapter(
        FlextMeltanoTypes.IntegerValue,
    )
    OBJECT_LIST_ADAPTER: u.TypeAdapter[
        Sequence[FlextMeltanoTypes.ContainerValueMapping]
    ] = u.TypeAdapter(
        Sequence[FlextMeltanoTypes.ContainerValueMapping],
        config=c.ConfigDict(strict=False),
    )
    COUNTER_MAP_ADAPTER: u.TypeAdapter[FlextMeltanoTypes.HeaderMapping] = u.TypeAdapter(
        FlextMeltanoTypes.HeaderMapping,
        config=c.ConfigDict(strict=False),
    )
    SINGER_OUTPUT_ADAPTER: u.TypeAdapter[FlextMeltanoTypes.ContainerMapping] = (
        u.TypeAdapter(
            FlextMeltanoTypes.ContainerMapping,
            config=c.ConfigDict(strict=False),
        )
    )
    CONFIG_STREAM_MAP_ADAPTER: u.TypeAdapter[
        Mapping[str, FlextMeltanoTypes.ContainerMapping]
    ] = u.TypeAdapter(
        Mapping[str, FlextMeltanoTypes.ContainerMapping],
        config=c.ConfigDict(strict=False),
    )


t = FlextTapLdapTypes
__all__: list[str] = ["FlextTapLdapTypes", "t"]
