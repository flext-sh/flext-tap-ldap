"""flext-tap-ldap config models — typed business-rule shapes.

Frozen Pydantic shapes for the ``config/tap-ldap.yaml`` business-rule SSOT,
reusing the flext-meltano ``m`` base models. The ``_config.py`` facade validates
the model-less YAML slice into these classes and exposes the ready objects under
``config.TapLdap``.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_meltano import m, t, u


class FlextTapLdapConfigModels:
    """Namespace of typed flext-tap-ldap config models."""

    class TapLdap(m.FrozenModel):
        """TapLdap business rules from ``config/tap-ldap.yaml``."""

        class StreamRule(m.FrozenModel):
            """One declarative stream business rule."""

            name: str = u.Field(description="Singer stream name")
            filter: str = u.Field(description="LDAP search filter")
            primary_keys: t.StrSequence = u.Field(description="Record primary keys")
            attributes: t.StrSequence = u.Field(
                description="LDAP attributes to request"
            )
            stream_schema: t.JsonMapping = u.Field(
                alias="schema", description="Singer stream JSON schema"
            )

        streams: t.SequenceOf[StreamRule] = u.Field(
            default=(), description="Declarative stream business rules"
        )

    class Root(m.FrozenModel):
        """Root flext-tap-ldap config validated from ``config/*.yaml``."""

        TapLdap: FlextTapLdapConfigModels.TapLdap = u.Field(
            description="TapLdap business-rule config domain",
        )


__all__: list[str] = ["FlextTapLdapConfigModels"]
