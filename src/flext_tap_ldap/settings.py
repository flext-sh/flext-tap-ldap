"""Tap LDAP settings models."""

from __future__ import annotations

from flext_ldap import FlextLdapSettings
from pydantic import Field
from pydantic_settings import SettingsConfigDict


class FlextTapLdapSettings(FlextLdapSettings):
    """Tap LDAP runtime settings."""

    model_config = SettingsConfigDict(extra="ignore")

    host: str = Field(default="localhost")
    port: int = Field(default=389, ge=1)
    use_ssl: bool = Field(default=False)
    timeout: int = Field(default=30, ge=1)
    page_size: int = Field(default=1000, ge=1)


__all__ = ["FlextTapLdapSettings"]
