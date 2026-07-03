"""FLEXT service orchestrator for tap-ldap.

Thin facade — all infrastructure from ``FlextMeltanoTapServiceBase`` via MRO.
The tap uses FlextMeltanoAbstractions (CLI dispatch), not singer_sdk.Tap.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Annotated, Never, override

from flext_meltano.services.consumer_bases.tap_service_base import (
    FlextMeltanoTapServiceBase,
)
from flext_tap_ldap import t, u


class FlextTapLdapService(FlextMeltanoTapServiceBase):
    """Orchestrator for tap-ldap. CLI dispatch, not Singer SDK."""

    tap_name: Annotated[
        t.NonEmptyStr,
        u.Field(description="Canonical Singer tap identifier."),
    ] = "tap-ldap"

    @override
    def create_tap_instance(
        self,
        settings: t.JsonMapping | None = None,
    ) -> Never:
        """Not supported — use FlextTapLdapTap directly."""
        msg = "tap-ldap uses CLI dispatch, not singer_sdk.Tap"
        raise TypeError(msg)


tap_ldap = FlextTapLdapService

__all__: list[str] = ["FlextTapLdapService", "tap_ldap"]
