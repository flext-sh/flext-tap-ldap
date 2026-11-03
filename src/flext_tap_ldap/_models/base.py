"""Base models for flext-tap-ldap private family.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_meltano import m


class FlextTapLdapModelsBase:
    """Base models for the flext-tap-ldap ``_models`` family."""

    class ConfigNamespace(m.BaseModel):
        """Open, frozen namespace exposing every ``config/*.yaml`` domain."""

        model_config = m.ConfigDict(extra="allow", frozen=True)


__all__: list[str] = ["FlextTapLdapModelsBase"]
