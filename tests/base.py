"""Service base for flext-tap-ldap tests."""

from __future__ import annotations

from typing import override

from flext_tests import s as tests_s

from flext_tap_ldap import m
from tests.settings import TestsFlextTapLdapSettings


class TestsFlextTapLdapServiceBase(tests_s):
    """Tap LDAP test service base with source and test settings namespaces."""

    @classmethod
    @override
    def fetch_settings(cls) -> TestsFlextTapLdapSettings:
        """Return the typed Tap LDAP+Tests settings singleton."""
        settings: TestsFlextTapLdapSettings = TestsFlextTapLdapSettings.fetch_global()
        return settings

    @classmethod
    @override
    def _runtime_bootstrap_options(cls) -> m.RuntimeBootstrapOptions:
        return m.RuntimeBootstrapOptions(settings_type=TestsFlextTapLdapSettings)


s = TestsFlextTapLdapServiceBase

__all__: list[str] = ["TestsFlextTapLdapServiceBase", "s"]
