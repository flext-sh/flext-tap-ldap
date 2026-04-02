"""Tap LDAP settings models."""

from __future__ import annotations

from typing import Annotated, ClassVar

from pydantic import Field
from pydantic_settings import SettingsConfigDict

from flext_ldap import FlextLdapSettings


class FlextTapLdapSettings(FlextLdapSettings):
    """Tap LDAP runtime settings."""

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(extra="ignore")

    host: Annotated[str, Field(default="localhost")]
    port: Annotated[int, Field(default=389, ge=1)]
    use_ssl: Annotated[bool, Field(default=False)]
    timeout: Annotated[int, Field(default=30, ge=1)]
    page_size: Annotated[int, Field(default=1000, ge=1)]


__all__ = ["FlextTapLdapSettings"]
