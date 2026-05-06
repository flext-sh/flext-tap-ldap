"""FLEXT Tap LDAP Types — MRO composition of parent type namespaces.

All Singer protocol types are in ``t.Meltano.*``.
All LDAP domain types are in ``FlextLdapTypes.Ldap.*``.
This facade composes both via MRO — access as ``t.Meltano.*`` and ``t.Ldap.*``.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_ldap import FlextLdapTypes
from flext_meltano import m, t, u


class FlextTapLdapTypes(t, FlextLdapTypes):
    """MRO facade composing Meltano + LDAP type namespaces.

    Access: ``t.Meltano.*`` (Singer protocol), ``t.Ldap.*`` (LDAP domain),
    ``t.TapLdap.*`` (tap-specific adapters), and all core ``t.*`` types via MRO.
    """

    class TapLdap:
        """Tap-LDAP-specific type adapters (project slot namespace)."""

        CONFIG_MAP_ADAPTER: u.TypeAdapter[t.JsonMapping] = u.TypeAdapter(
            t.JsonMapping,
            config=m.ConfigDict(strict=False),
        )
        STRICT_STR_ADAPTER: u.TypeAdapter[t.StrictStr] = u.TypeAdapter(
            t.StrictStr,
            config=m.ConfigDict(strict=True),
        )
        INTEGER_ADAPTER: u.TypeAdapter[t.StrictInt] = u.TypeAdapter(
            t.StrictInt,
        )
        OBJECT_LIST_ADAPTER: u.TypeAdapter[t.SequenceOf[t.JsonMapping]] = u.TypeAdapter(
            t.SequenceOf[t.JsonMapping],
            config=m.ConfigDict(strict=False),
        )
        COUNTER_MAP_ADAPTER: u.TypeAdapter[t.HeaderMapping] = u.TypeAdapter(
            t.HeaderMapping,
            config=m.ConfigDict(strict=False),
        )
        SINGER_OUTPUT_ADAPTER: u.TypeAdapter[t.JsonMapping] = u.TypeAdapter(
            t.JsonMapping,
            config=m.ConfigDict(strict=False),
        )
        CONFIG_STREAM_MAP_ADAPTER: u.TypeAdapter[t.MappingKV[str, t.JsonMapping]] = (
            u.TypeAdapter(
                t.MappingKV[str, t.JsonMapping],
                config=m.ConfigDict(strict=False),
            )
        )


t = FlextTapLdapTypes
__all__: list[str] = ["FlextTapLdapTypes", "t"]
