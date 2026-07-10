"""Tap LDAP settings — namespaced under ``settings.TapLdap``.

Universal fields via MRO; project fields in the ``TapLdap`` group with simple
scalar types (env-settable).

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated

from pydantic import BaseModel, Field
from pydantic_settings import SettingsConfigDict

from flext_ldap import FlextLdapSettings


class FlextTapLdapSettings(FlextLdapSettings):
    """Tap LDAP runtime settings; fields under ``settings.TapLdap.*``."""

    model_config = SettingsConfigDict(
        env_prefix="FLEXT_TAP_LDAP_",
        env_nested_delimiter="__",
        extra="ignore",
    )

    class _TapLdap(BaseModel):
        """Namespaced tap-LDAP settings."""

        host: Annotated[str, Field(default="localhost", description="LDAP host")]
        port: Annotated[
            int, Field(default=389, ge=1, le=65535, description="LDAP port")
        ]
        use_ssl: Annotated[bool, Field(default=False, description="Use SSL")]
        timeout: Annotated[int, Field(default=30, ge=1, description="Timeout (s)")]
        page_size: Annotated[int, Field(default=1000, ge=1, description="Page size")]

    if TYPE_CHECKING:
        TapLdap: _TapLdap
    else:
        TapLdap: _TapLdap = Field(
            default_factory=_TapLdap,
            description="Namespaced tap-LDAP settings.",
        )


settings: FlextTapLdapSettings = FlextTapLdapSettings.fetch_global()
"""Pre-instantiated project settings singleton — ``from flext_tap_ldap import settings``."""

__all__: list[str] = ["FlextTapLdapSettings", "settings"]
