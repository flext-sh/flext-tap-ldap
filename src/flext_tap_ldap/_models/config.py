"""flext-tap-ldap config models — typed business-rule shapes.

Frozen Pydantic shapes for the ``config/tap-ldap.yaml`` business-rule SSOT,
reusing the flext-meltano ``m`` base models. The ``_config.py`` facade validates
the model-less YAML slice into these classes and exposes the ready objects under
``config.tap_ldap``.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_meltano import m, t


class FlextModelsTapLdapConfig:
    """Namespace of typed flext-tap-ldap config models."""

    class TapLdap(m.FrozenModel):
        """TapLdap business rules from ``config/tap-ldap.yaml``."""

        class StreamRule(m.FrozenModel):
            """One declarative stream business rule."""

            name: str = m.Field(description="Singer stream name")
            filter: str = m.Field(description="LDAP search filter")
            primary_keys: t.StrSequence = m.Field(description="Record primary keys")
            attributes: t.StrSequence = m.Field(
                description="LDAP attributes to request",
            )
            stream_schema: t.JsonMapping = m.Field(
                alias="schema",
                description="Singer stream JSON schema",
            )

        streams: t.SequenceOf[StreamRule] = m.Field(
            default=(),
            description="Declarative stream business rules",
        )

    class Root(m.FrozenModel):
        """Root flext-tap-ldap config validated from ``config/*.yaml``.

        The ``config/`` directory is shared across domains (fleet tooling drops
        sibling YAML files), so unknown top-level keys are tolerated; the
        ``TapLdap`` branch itself stays strictly validated.

        """

        model_config = m.ConfigDict(extra="allow")

        TapLdap: FlextModelsTapLdapConfig.TapLdap = m.Field(
            description="TapLdap business-rule config domain",
        )


__all__: list[str] = ["FlextModelsTapLdapConfig"]
