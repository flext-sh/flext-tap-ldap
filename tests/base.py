"""Service base for flext-tap-ldap tests."""

from __future__ import annotations

from typing import override

from flext_tap_ldap import m
from flext_tests import s as tests_s
from tests.settings import TestsFlextTapLdapSettings


class TestsFlextTapLdapServiceBase(tests_s):
    """Tap LDAP test service base with source and test settings namespaces."""

    # NOTE (multi-agent): flext-tests owns fetch_settings; this project
    # declares only its more-specific bootstrap settings type (canonical
    # pattern per flext-cli tests/base.py — returning the raw production
    # singleton violates the Tests settings contract).
    @classmethod
    @override
    def _runtime_bootstrap_options(cls) -> m.RuntimeBootstrapOptions:
        return m.RuntimeBootstrapOptions(settings_type=TestsFlextTapLdapSettings)


s = TestsFlextTapLdapServiceBase

__all__: list[str] = ["TestsFlextTapLdapServiceBase", "s"]
