"""Behavioral tests for FLEXT Tap LDAP models.

Exercises the public contract of ``FlextTapLdapModels.TapLdap`` models:
field defaults, validation constraints, immutability, value equality, and
serialization round-trips. No implementation internals are touched.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Callable

import pytest
from pydantic import ValidationError

from flext_tap_ldap import FlextTapLdapModels, c

_TapLdap = FlextTapLdapModels.TapLdap
_Params = _TapLdap.LdapConnectionParams

__all__: list[str] = ["TestsFlextTapLdapModelsUnit"]


class TestsFlextTapLdapModelsUnit:
    """Public-contract behavior for tap-LDAP models."""

    # ── CustomPropertyDefinition ─────────────────────────────────────────

    def test_custom_property_definition_defaults_to_string_type(self) -> None:
        definition = _TapLdap.CustomPropertyDefinition()

        assert definition.type == "string"
        assert definition.description is None

    def test_custom_property_definition_accepts_explicit_values(self) -> None:
        definition = _TapLdap.CustomPropertyDefinition(
            type="integer",
            description="a numeric property",
        )

        assert definition.model_dump() == {
            "type": "integer",
            "description": "a numeric property",
        }

    # ── LdapConnectionParams: valid construction ─────────────────────────

    def test_connection_params_expose_supplied_and_default_fields(self) -> None:
        params = _TapLdap.LdapConnectionParams(
            host="ldap.example.com",
            port=636,
            use_ssl=True,
            timeout_seconds=30,
        )

        assert params.host == "ldap.example.com"
        assert params.port == 636
        assert params.use_ssl is True
        assert params.timeout_seconds == 30
        # Optional auth/search fields default to None.
        assert params.bind_dn is None
        assert params.bind_password is None
        assert params.base_dn is None
        # Documented defaults.
        assert params.page_size == c.TapLdap.DEFAULT_PAGE_SIZE
        assert params.max_retries == 3

    @pytest.mark.parametrize("port", [1, 389, 65535])
    def test_connection_params_accept_valid_port_boundaries(
        self,
        port: int,
    ) -> None:
        params = _TapLdap.LdapConnectionParams(
            host="h",
            port=port,
            use_ssl=False,
            timeout_seconds=1,
        )

        assert params.port == port

    # ── LdapConnectionParams: validation contract ────────────────────────

    @pytest.mark.parametrize(
        ("build", "invalid_field"),
        [
            (
                lambda: _TapLdap.LdapConnectionParams(
                    host="",
                    port=389,
                    use_ssl=False,
                    timeout_seconds=30,
                ),
                "host",
            ),
            (
                lambda: _TapLdap.LdapConnectionParams(
                    host="h",
                    port=0,
                    use_ssl=False,
                    timeout_seconds=30,
                ),
                "port",
            ),
            (
                lambda: _TapLdap.LdapConnectionParams(
                    host="h",
                    port=70000,
                    use_ssl=False,
                    timeout_seconds=30,
                ),
                "port",
            ),
            (
                lambda: _TapLdap.LdapConnectionParams(
                    host="h",
                    port=389,
                    use_ssl=False,
                    timeout_seconds=0,
                ),
                "timeout_seconds",
            ),
            (
                lambda: _TapLdap.LdapConnectionParams(
                    host="h",
                    port=389,
                    use_ssl=False,
                    timeout_seconds=30,
                    page_size=0,
                ),
                "page_size",
            ),
            (
                lambda: _TapLdap.LdapConnectionParams(
                    host="h",
                    port=389,
                    use_ssl=False,
                    timeout_seconds=30,
                    max_retries=-1,
                ),
                "max_retries",
            ),
        ],
    )
    def test_connection_params_reject_out_of_contract_values(
        self,
        build: Callable[[], _Params],
        invalid_field: str,
    ) -> None:
        with pytest.raises(ValidationError) as exc_info:
            build()

        offending = {error["loc"][0] for error in exc_info.value.errors()}
        assert invalid_field in offending

    def test_connection_params_require_mandatory_fields(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            _TapLdap.LdapConnectionParams(host="h")

        missing = {
            error["loc"][0]
            for error in exc_info.value.errors()
            if error["type"] == "missing"
        }
        assert {"port", "use_ssl", "timeout_seconds"} <= missing

    # ── LdapConnectionParams: value semantics ────────────────────────────

    def test_connection_params_are_value_objects_with_structural_equality(
        self,
    ) -> None:
        left = _TapLdap.LdapConnectionParams(
            host="h",
            port=389,
            use_ssl=True,
            timeout_seconds=30,
        )
        right = _TapLdap.LdapConnectionParams(
            host="h",
            port=389,
            use_ssl=True,
            timeout_seconds=30,
        )

        assert left == right

    def test_connection_params_are_immutable(self) -> None:
        params = _TapLdap.LdapConnectionParams(
            host="h",
            port=389,
            use_ssl=True,
            timeout_seconds=30,
        )

        with pytest.raises(ValidationError):
            setattr(params, "host", "other")

    def test_connection_params_round_trip_through_model_dump(self) -> None:
        original = _TapLdap.LdapConnectionParams(
            host="dir.example.org",
            port=389,
            bind_dn="cn=admin",
            use_ssl=True,
            timeout_seconds=45,
            page_size=250,
            max_retries=5,
        )

        rebuilt = _TapLdap.LdapConnectionParams.model_validate(
            original.model_dump(),
        )

        assert rebuilt == original
