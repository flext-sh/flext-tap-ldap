"""Behavioral e2e tests for the tap-ldap Singer CLI contract.

Runs the REAL installed console script through the flext-cli SSOT runner
(``u.Cli.capture``) and asserts the observable stdout catalog, exactly as an
orchestrator invokes the tap. All fixed data comes from the shared
``c.Ldap.Tests`` constants.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from flext_tests import tm, u
from tests import c, t

if TYPE_CHECKING:
    from pathlib import Path


class TestsFlextTapLdapIntegration:
    """Observable-contract tests for the real tap-ldap Singer CLI."""

    # Singer discovery builds the full catalog against the real tap CLI and
    # therefore uses the config-owned slow-item budget.
    pytestmark = pytest.mark.slow

    @staticmethod
    def _discover_streams(tmp_path: Path) -> tuple[bool, list[t.JsonMapping]]:
        config_path = tmp_path / "config.json"
        config_path.write_text(
            json.dumps({
                "base_dn": c.Ldap.Tests.BASE_DN,
                "host": c.Ldap.Tests.HOST,
                "port": c.Ldap.Tests.PORT,
            })
        )
        result = u.Cli.capture(
            [
                c.Ldap.Tests.CONSOLE_SCRIPT,
                c.Ldap.Tests.FLAG_CONFIG,
                str(config_path),
                c.Ldap.Tests.FLAG_DISCOVER,
            ],
            remove_env_keys=("PYTHONPATH",),
        )
        if not result.success:
            return False, []
        catalog = t.Cli.JSON_MAPPING_ADAPTER.validate_json(result.value)
        streams = [
            t.Cli.JSON_MAPPING_ADAPTER.validate_python(entry)
            for entry in t.Cli.JSON_LIST_ADAPTER.validate_python(catalog["streams"])
        ]
        return True, streams

    def test_discover_publishes_every_standard_ldap_stream(
        self, tmp_path: Path
    ) -> None:
        """Discovery advertises every standard LDAP stream at exit 0."""
        success, streams = self._discover_streams(tmp_path)
        tm.that(success, eq=True)
        stream_ids = [str(entry["tap_stream_id"]) for entry in streams]
        for expected in c.Ldap.Tests.STANDARD_STREAMS:
            tm.that(stream_ids, has=expected)

    def test_discover_streams_declare_dn_primary_key(self, tmp_path: Path) -> None:
        """Each discovered stream declares the LDAP dn as its key property."""
        success, streams = self._discover_streams(tmp_path)
        tm.that(success, eq=True)
        for entry in streams:
            keys = t.Cli.JSON_LIST_ADAPTER.validate_python(entry["key_properties"])
            tm.that(list(keys), eq=list(c.Ldap.Tests.PRIMARY_KEY))


__all__: list[str] = ["TestsFlextTapLdapIntegration"]
