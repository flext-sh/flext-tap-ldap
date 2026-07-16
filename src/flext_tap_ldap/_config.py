"""FlextTapLdapConfig — frozen config singleton for flext-tap-ldap.

Business-rule SSOT: the stream contracts (name, LDAP filter, attributes, Singer
schema, primary keys) live in ``config/tap-ldap.yaml`` at the project root under
the ``TapLdap`` key and are exposed through the open ``config.TapLdap`` namespace.
Config holds the business rules; ``settings`` holds the adjustable runtime
parameters (``.env`` / env vars / local settings / CLI).

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import ClassVar

from pydantic import BaseModel, ConfigDict

from flext_meltano import FlextMeltanoConfig


class FlextTapLdapConfig(FlextMeltanoConfig):
    """TapLdap config auto-loaded from the project-root ``config/*.yaml``.

    ``CONFIG_DIR`` is reset to the relative default so the loader anchors to this
    project's own root ``config/`` instead of inheriting an ancestor's absolute
    override (which would otherwise load the wrong package's config).
    """

    CONFIG_DIR: ClassVar[str] = "config"

    class _TapLdapNamespace(BaseModel):
        """Open, frozen namespace exposing every ``config/*.yaml`` domain."""

        model_config = ConfigDict(extra="allow", frozen=True)

    TapLdap: _TapLdapNamespace = _TapLdapNamespace()


config: FlextTapLdapConfig = FlextTapLdapConfig.fetch_global()
"""Pre-instantiated frozen config singleton — ``from flext_tap_ldap import config``."""

__all__: list[str] = ["FlextTapLdapConfig", "config"]
