"""Tap LDAP settings models."""

from __future__ import annotations

from typing import Annotated, ClassVar

from flext_ldap import FlextLdapSettings
from flext_tap_ldap import c, m, t, u


class FlextTapLdapSettings(FlextLdapSettings):
    """Tap LDAP runtime settings."""

    model_config: ClassVar[m.SettingsConfigDict] = m.SettingsConfigDict(
        env_prefix="FLEXT_TAP_LDAP_",
        extra="ignore",
    )

    host: Annotated[str, u.Field()] = c.LOCALHOST
    port: Annotated[t.PortNumber, u.Field(ge=1)] = c.Ldap.PORT
    use_ssl: Annotated[bool, u.Field()] = c.Ldap.DEFAULT_USE_SSL
    timeout: Annotated[t.PositiveInt, u.Field(ge=1)] = c.Ldap.TIMEOUT
    page_size: Annotated[t.PositiveInt, u.Field(ge=1)] = 1000


__all__: list[str] = ["FlextTapLdapSettings"]
