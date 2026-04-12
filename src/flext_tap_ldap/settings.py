"""Tap LDAP settings models."""

from __future__ import annotations

from typing import Annotated, ClassVar

from flext_core import FlextSettings
from flext_ldap import FlextLdapSettings
from flext_tap_ldap import c, t, u


@FlextSettings.auto_register("tap-ldap")
class FlextTapLdapSettings(FlextLdapSettings):
    """Tap LDAP runtime settings."""

    model_config: ClassVar[c.SettingsConfigDict] = c.SettingsConfigDict(
        env_prefix="FLEXT_TAP_LDAP_", extra="ignore"
    )

    host: Annotated[str, u.Field(default=c.LOCALHOST)]
    port: Annotated[t.PortNumber, u.Field(default=c.Ldap.ConnectionDefaults.PORT, ge=1)]
    use_ssl: Annotated[bool, u.Field(default=c.Ldap.ConnectionDefaults.DEFAULT_USE_SSL)]
    timeout: Annotated[
        t.PositiveInt, u.Field(default=c.Ldap.ConnectionDefaults.TIMEOUT, ge=1)
    ]
    page_size: Annotated[t.PositiveInt, u.Field(default=c.DEFAULT_BATCH_SIZE, ge=1)]


__all__: list[str] = ["FlextTapLdapSettings"]
