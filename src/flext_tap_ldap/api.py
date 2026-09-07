"""FLEXT service orchestrator for tap-ldap — declarative Singer tap.

Thin facade over ``meltano.Tap``: declares the tap by building a
``m.Meltano.TapSpec`` from config business rules and delegating record fetching
to ``FlextTapLdapExtractService``. flext-meltano owns every ``singer_sdk`` detail.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Annotated, override

from flext_meltano import meltano
from flext_tap_ldap import c, p, t, u
from flext_tap_ldap.services.extract import FlextTapLdapExtractService


class FlextTapLdapService(meltano.Tap):
    """Declarative tap-ldap orchestrator built from config + settings SSOT."""

    tap_name: Annotated[
        t.NonEmptyStr, u.Field(description="Canonical Singer tap identifier.")
    ] = c.TapLdap.TAP_NAME

    @override
    def create_tap_instance(
        self, settings: p.Settings | None = None
    ) -> p.Meltano.SingerTapInstance:
        """Build the declarative Singer tap from config streams + a fetcher."""
        _ = settings
        tap: p.Meltano.SingerTapInstance = self.build_declarative_tap(
            u.TapLdap.tap_spec(), FlextTapLdapExtractService()
        )
        return tap


tap_ldap = FlextTapLdapService

__all__: list[str] = ["FlextTapLdapService", "tap_ldap"]
