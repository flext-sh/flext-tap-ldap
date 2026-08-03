"""Tap LDAP settings — namespaced under ``settings.TapLdap``.

Universal fields via MRO; project fields in the ``TapLdap`` group with simple
scalar types (env-settable).

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated

from pydantic_settings import SettingsConfigDict

from flext_ldap import FlextLdapSettings, m


class FlextTapLdapSettings(FlextLdapSettings):
    """Tap LDAP runtime settings; fields under ``settings.TapLdap.*``."""

    model_config = SettingsConfigDict(
        env_prefix="FLEXT_TAP_LDAP_", env_nested_delimiter="__", extra="ignore"
    )

    class _TapLdap(m.BaseModel):
        """Tap-specific adjustable params (``settings.TapLdap.*``).

        All fields are set by ``.env`` / env vars / local settings / CLI / API and
        parametrize the run. Connection params (host, port, bind_dn, bind_password,
        use_ssl, timeout) are NOT redeclared here — they are reused from the parent
        ``settings.Ldap.*`` via MRO and parametrized the same way.
        """

        base_dn: Annotated[str, m.Field(default="", description="Search base DN")]
        page_size: Annotated[int, m.Field(default=1000, ge=1, description="Page size")]

    if TYPE_CHECKING:
        TapLdap: _TapLdap
    else:
        TapLdap: _TapLdap = m.Field(
            default_factory=_TapLdap, description="Namespaced tap-LDAP settings."
        )


settings: FlextTapLdapSettings = FlextTapLdapSettings.fetch_global()
"""Pre-instantiated project settings singleton — ``from flext_tap_ldap import settings``."""

__all__: list[str] = ["FlextTapLdapSettings", "settings"]
