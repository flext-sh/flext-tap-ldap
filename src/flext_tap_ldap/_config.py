"""FlextTapLdapConfig — frozen config singleton for flext-tap-ldap (ADR-005 §7).

Business-rule SSOT: the stream contracts (name, LDAP filter, attributes, Singer
schema, primary keys) live in the packaged ``flext_tap_ldap/config/tap-ldap.yaml``
under the ``TapLdap:`` key and are exposed through the open ``config.TapLdap``
namespace (``extra="allow"``).
``config.tap_ldap`` is the validated typed view of that namespace.
Config holds the business rules; ``settings`` holds the adjustable runtime
parameters (``.env`` / env vars / local settings / CLI).

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from functools import cached_property
from typing import Annotated

from flext_meltano import FlextMeltanoConfig, m

from flext_tap_ldap._models.config import FlextTapLdapConfigModels


class FlextTapLdapConfig(FlextMeltanoConfig):
    """TapLdap config auto-loaded from the packaged ``config/*.yaml``.

    ``FlextMeltanoConfig`` already carries ``FlextSettings`` first (ENFORCE-042),
    so the class stays a frozen, YAML-validated config singleton. The YAML
    ``TapLdap:`` slice is exposed as an open namespace and validated once into the
    typed config models behind ``config.tap_ldap``.
    """

    TapLdap: Annotated[
        m.Meltano.MeltanoNamespace,
        m.Field(
            description="Open namespace exposing ``config/*.yaml`` under ``TapLdap``.",
        ),
    ] = m.Meltano.MeltanoNamespace()

    @cached_property
    def tap_ldap(self) -> FlextTapLdapConfigModels.TapLdap:
        """Validated TapLdap business-rule config (streams and their contracts)."""
        payload = self.TapLdap.model_dump()
        return FlextTapLdapConfigModels.TapLdap.model_validate(payload)


config: FlextTapLdapConfig = FlextTapLdapConfig.fetch_global()
"""Pre-instantiated frozen config singleton — ``from flext_tap_ldap import config``."""

__all__: list[str] = ["FlextTapLdapConfig", "config"]
