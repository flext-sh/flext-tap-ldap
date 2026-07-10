"""FlextTapLdapConfig — frozen config singleton for flext-tap-ldap (ADR-005 §7).

Model-less: business rules live in ``config/*.yaml`` under the ``TapLdap:`` key and
are exposed through the open ``config.TapLdap`` namespace (``extra="allow"``), with
no per-domain model. Access is ``config.TapLdap.<domain>[<key>...]``.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from flext_meltano import FlextMeltanoConfig


class _TapLdapNamespace(BaseModel):
    """Open, frozen namespace exposing every ``config/*.yaml`` domain model-less."""

    model_config = ConfigDict(extra="allow", frozen=True)


class FlextTapLdapConfig(FlextMeltanoConfig):
    """TapLdap config auto-loaded model-less from ``config/*.yaml``."""

    TapLdap: _TapLdapNamespace = _TapLdapNamespace()


config: FlextTapLdapConfig = FlextTapLdapConfig.fetch_global()
"""Pre-instantiated frozen config singleton — ``from flext_tap_ldap import config``."""

__all__: list[str] = ["FlextTapLdapConfig", "config"]
