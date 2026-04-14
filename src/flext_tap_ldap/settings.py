"""Tap LDAP settings models."""

from __future__ import annotations

from typing import Annotated, ClassVar

from pydantic import Field

from flext_core import FlextSettings
from flext_ldap import FlextLdapSettings
from flext_tap_ldap import c, t


@FlextSettings.auto_register("tap-ldap")
class FlextTapLdapSettings(FlextLdapSettings):
    """Tap LDAP runtime settings."""

    model_config: ClassVar[c.SettingsConfigDict] = c.SettingsConfigDict(
        env_prefix="FLEXT_TAP_LDAP_", extra="ignore"
    )

    host: Annotated[str, Field(default=c.LOCALHOST)]
    port: Annotated[t.PortNumber, Field(default=c.Ldap.ConnectionDefaults.PORT, ge=1)]
    use_ssl: Annotated[bool, Field(default=c.Ldap.ConnectionDefaults.DEFAULT_USE_SSL)]
    timeout: Annotated[
        t.PositiveInt, Field(default=c.Ldap.ConnectionDefaults.TIMEOUT, ge=1)
    ]
    page_size: Annotated[t.PositiveInt, Field(default=c.DEFAULT_BATCH_SIZE, ge=1)]


__all__: list[str] = ["FlextTapLdapSettings"]
