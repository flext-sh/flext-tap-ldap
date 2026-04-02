"""FLEXT Tap LDAP Types — MRO composition of parent type namespaces.

All Singer protocol types are in ``FlextMeltanoTypes.Meltano.*``.
All LDAP domain types are in ``FlextLdapTypes.Ldap.*``.
This facade composes both via MRO — access as ``FlextMeltanoTypes.Meltano.*`` and ``FlextMeltanoTypes.Ldap.*``.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from pydantic import ConfigDict, TypeAdapter

from flext_ldap import FlextLdapTypes
from flext_meltano import FlextMeltanoTypes


class FlextTapLdapTypes(FlextMeltanoTypes, FlextLdapTypes):
    """MRO facade composing Meltano + LDAP type namespaces.

    Access: ``FlextMeltanoTypes.Meltano.*`` (Singer protocol), ``FlextMeltanoTypes.Ldap.*`` (LDAP domain),
    and all core ``FlextMeltanoTypes.*`` types via MRO inheritance.
    """

    CONFIG_MAP_ADAPTER: TypeAdapter[FlextMeltanoTypes.ContainerValueMapping] = (
        TypeAdapter(
            FlextMeltanoTypes.ContainerValueMapping,
            config=ConfigDict(strict=False),
        )
    )
    STRICT_STR_ADAPTER: TypeAdapter[FlextMeltanoTypes.TextValue] = TypeAdapter(
        FlextMeltanoTypes.TextValue,
        config=ConfigDict(strict=True),
    )
    INTEGER_ADAPTER: TypeAdapter[FlextMeltanoTypes.IntegerValue] = TypeAdapter(
        FlextMeltanoTypes.IntegerValue,
    )
    OBJECT_LIST_ADAPTER: TypeAdapter[
        Sequence[FlextMeltanoTypes.ContainerValueMapping]
    ] = TypeAdapter(
        Sequence[FlextMeltanoTypes.ContainerValueMapping],
        config=ConfigDict(strict=False),
    )
    COUNTER_MAP_ADAPTER: TypeAdapter[FlextMeltanoTypes.HeaderMapping] = TypeAdapter(
        FlextMeltanoTypes.HeaderMapping,
        config=ConfigDict(strict=False),
    )
    SINGER_OUTPUT_ADAPTER: TypeAdapter[FlextMeltanoTypes.ContainerMapping] = (
        TypeAdapter(
            FlextMeltanoTypes.ContainerMapping,
            config=ConfigDict(strict=False),
        )
    )
    CONFIG_STREAM_MAP_ADAPTER: TypeAdapter[
        Mapping[str, FlextMeltanoTypes.ContainerMapping]
    ] = TypeAdapter(
        Mapping[str, FlextMeltanoTypes.ContainerMapping],
        config=ConfigDict(strict=False),
    )


t = FlextTapLdapTypes
__all__ = ["FlextTapLdapTypes", "t"]
