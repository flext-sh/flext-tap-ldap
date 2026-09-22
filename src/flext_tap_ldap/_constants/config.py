"""LDAP tap constants - configuration constants."""

from __future__ import annotations

from typing import Final

from flext_ldap import FlextLdapConstants

from .base import FlextTapLdapConstantsBase


class FlextTapLdapConstantsConfig(FlextTapLdapConstantsBase):
    """LDAP tap configuration constants."""

    class TapLdap:
        """Tap LDAP namespace for cross-project access."""

        DEFAULT_PAGE_SIZE: Final[int] = 1000
        DEFAULT_SEARCH_TIMEOUT: Final[int] = FlextLdapConstants.Ldap.TIMEOUT
        TAP_NAME: Final[str] = "tap-ldap"

        class Ldap:
            """LDAP tap-specific connection constants."""

            MAX_PORT: Final[int] = 65535

        class Replication:
            """LDAP replication method constants."""

            class Method:
                """LDAP replication methods."""

                FULL_TABLE = "FULL_TABLE"
                INCREMENTAL = "INCREMENTAL"

        class Connection:
            """LDAP tap connection configuration."""

            DEFAULT_HOST: Final[str] = FlextLdapConstants.LOCALHOST
            DEFAULT_BASE_DN: Final[str] = ""

        class Search:
            """LDAP search configuration."""

            DEFAULT_SCOPE: Final[str] = "SUBTREE"


class FlextTapLdapConfigValues:
    """Scalar constants for the frozen config singleton.

    Mixed into ``FlextTapLdapConfig`` so the values stay out of its
    ``vars()`` while every ``Cls.NAME`` consumer path keeps resolving.
    """

    class Config:
        """Config singleton scalar constants."""

        CONFIG_DIR: Final[str] = "config"


__all__: list[str] = ["FlextTapLdapConfigValues", "FlextTapLdapConstantsConfig"]
