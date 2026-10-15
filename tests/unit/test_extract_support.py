"""Behavioral tests for the tap-ldap extract-support helpers.

Expected values are read from the ``config.tap_ldap`` business-rule SSOT, so the
tests stay valid for any configured stream set.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_tap_ldap import config
from tests import c, tm, u


class TestsFlextTapLdapExtractSupport:
    """Public-contract behavior for ``u.TapLdap`` extract helpers."""

    @staticmethod
    def test_tap_spec_declares_every_configured_stream() -> None:
        """The tap spec mirrors the configured stream rules and tap name."""
        spec = u.TapLdap.tap_spec()

        tm.that(spec.tap_name, eq=c.TapLdap.TAP_NAME)
        tm.that(
            [stream.name for stream in spec.streams],
            eq=[rule.name for rule in config.tap_ldap.streams],
        )
        tm.that(
            [list(stream.primary_keys) for stream in spec.streams],
            eq=[list(rule.primary_keys) for rule in config.tap_ldap.streams],
        )

    @staticmethod
    def test_stream_search_resolves_configured_rule() -> None:
        """A configured stream resolves into its filter, attributes and base DN."""
        source = {"base_dn": c.Ldap.Tests.BASE_DN}
        for rule in config.tap_ldap.streams:
            options = tm.ok(u.TapLdap.stream_search(rule.name, source))

            tm.that(options.filter_str, eq=rule.filter)
            tm.that(list(options.attributes or ()), eq=list(rule.attributes))
            tm.that(options.base_dn, eq=c.Ldap.Tests.BASE_DN)

    @staticmethod
    def test_stream_search_fails_without_base_dn() -> None:
        """An empty base DN is a failed result, never a raised exception."""
        for rule in config.tap_ldap.streams:
            tm.fail(u.TapLdap.stream_search(rule.name, {"base_dn": ""}))

    @staticmethod
    def test_stream_search_rejects_unknown_stream() -> None:
        """An undeclared stream name fails instead of guessing a rule."""
        unknown = "-".join(rule.name for rule in config.tap_ldap.streams) + "-unknown"

        tm.fail(u.TapLdap.stream_search(unknown, {}))
