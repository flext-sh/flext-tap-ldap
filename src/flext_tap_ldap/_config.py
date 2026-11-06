"""FlextTapLdapConfig — frozen config singleton for flext-tap-ldap (ADR-005 §7).

Business-rule SSOT: the stream contracts (name, LDAP filter, attributes, Singer
schema, primary keys) live in the packaged ``flext_tap_ldap/config/tap-ldap.yaml``
under the ``TapLdap:`` key and are exposed through the open ``config.TapLdap``
namespace (``extra="allow"``). The typed validated view of that namespace is
built by the consumers in the ``u`` family (``u.TapLdap.tap_ldap()``) — config
never imports the model layer (ADR-005 §2).
Config holds the business rules; ``settings`` holds the adjustable runtime
parameters (``.env`` / env vars / local settings / CLI).

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import Annotated

from flext_meltano import FlextMeltanoConfig, m


class FlextTapLdapConfig(FlextMeltanoConfig):
    """TapLdap config auto-loaded from the packaged ``config/*.yaml``.

    ``FlextMeltanoConfig`` already carries ``FlextSettings`` first (ENFORCE-042),
    so the class stays a frozen, YAML-validated config singleton. The YAML
    ``TapLdap:`` slice is exposed as an open namespace; the typed validated
    view lives behind ``u.TapLdap.tap_ldap()``.
    """

    TapLdap: Annotated[
        m.Meltano.MeltanoNamespace,
        m.Field(
            description="Open namespace exposing ``config/*.yaml`` under ``TapLdap``.",
        ),
    ] = m.Meltano.MeltanoNamespace()


config: FlextTapLdapConfig = FlextTapLdapConfig.fetch_global()
"""Pre-instantiated frozen config singleton — ``from flext_tap_ldap import config``."""

__all__: list[str] = ["FlextTapLdapConfig", "config"]
