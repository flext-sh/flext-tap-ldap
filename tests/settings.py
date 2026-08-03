"""Runtime settings for flext-tap-ldap tests."""

from __future__ import annotations

from flext_tap_ldap import FlextTapLdapSettings
from flext_tests import FlextTestsSettings


class TestsFlextTapLdapSettings(FlextTapLdapSettings, FlextTestsSettings):
    """Tap LDAP settings extended with the shared test namespace."""


__all__: list[str] = ["TestsFlextTapLdapSettings"]
