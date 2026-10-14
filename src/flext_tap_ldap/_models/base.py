"""Base models for flext-tap-ldap private family.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_meltano import m as meltano_m


class FlextTapLdapModelsBase(meltano_m):
    """Base models for _models family."""

    class ConfigNamespace(meltano_m.BaseModel):
        """Open, frozen namespace exposing every ``config/*.yaml`` domain."""

        model_config = meltano_m.ConfigDict(extra="allow", frozen=True)


__all__: list[str] = ["FlextTapLdapModelsBase"]
