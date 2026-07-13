"""Behavioral tests for the LDAP client public contract.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import asyncio
import contextlib
from collections.abc import Generator
from unittest.mock import Mock, patch

import pytest

from flext_ldap import FlextLdap
from flext_tap_ldap.client import FlextTapLdapClient
from tests import t, u

__all__: t.StrSequence = ("TestsFlextTapLdapClientQuick",)


class TestsFlextTapLdapClientQuick:
    """Observable-behavior tests for FlextTapLdapClient.LDAPClient and support."""

    @staticmethod
    def _ldap_result(
        entries: list[t.JsonMapping],
        *,
        success: bool = True,
    ) -> Mock:
        """Build a stand-in for the external flext-ldap search result."""
        result = Mock()
        result.success = success
        result.value = Mock(entries=entries)
        return result

    @staticmethod
    @contextlib.contextmanager
    def _client(
        *,
        search_result: Mock | None = None,
        search_error: BaseException | None = None,
        host: str = "test.ldap.com",
        port: int = 389,
        use_ssl: bool = False,
    ) -> Generator[FlextTapLdapClient.LDAPClient]:
        """Yield a client whose only mocked dependency is the LDAP boundary."""
        api = Mock(spec=FlextLdap)
        if search_error is not None:
            api.search.side_effect = search_error
        else:
            api.search.return_value = search_result
        with patch("flext_tap_ldap.client.FlextLdap", return_value=api):
            yield FlextTapLdapClient.LDAPClient(
                host=host,
                port=port,
                use_ssl=use_ssl,
            )

    # ---- server_uri contract --------------------------------------------

    @pytest.mark.parametrize(
        ("host", "port", "use_ssl", "expected"),
        [
            ("test.com", 389, False, "ldap://test.com:389"),
            ("secure.com", 636, True, "ldaps://secure.com:636"),
        ],
    )
    def test_server_uri_reflects_scheme_host_and_port(
        self,
        host: str,
        port: int,
        *,
        use_ssl: bool,
        expected: str,
    ) -> None:
        """server_uri renders ldap/ldaps scheme with the configured endpoint."""
        with self._client(host=host, port=port, use_ssl=use_ssl) as client:
            assert client.server_uri == expected

    # ---- scope normalization contract -----------------------------------

    @pytest.mark.parametrize(
        ("given", "expected"),
        [
            ("BASE", "BASE"),
            ("ONELEVEL", "ONELEVEL"),
            ("SUBTREE", "SUBTREE"),
            ("base", "BASE"),
            ("INVALID", "SUBTREE"),
        ],
    )
    def test_normalize_scope_maps_to_canonical_scope(
        self,
        given: str,
        expected: str,
    ) -> None:
        """Unknown scopes fall back to SUBTREE; known scopes upper-case."""
        assert u.TapLdap.ClientSupport.normalize_scope(given) == expected

    # ---- entry mapping contract -----------------------------------------

    def test_to_entry_mapping_returns_success_for_dict_entry(self) -> None:
        """A well-formed entry maps to a successful result preserving the dn."""
        entry: t.JsonMapping = {
            "dn": "uid=dict,dc=example,dc=com",
            "attributes": {"mail": ["test@example.com"]},
        }
        result = u.TapLdap.ClientSupport.to_entry_mapping(entry)
        assert result.success
        assert result.value["dn"] == "uid=dict,dc=example,dc=com"

    def test_to_entry_mapping_preserves_scalar_and_list_attributes(self) -> None:
        """Both scalar and multi-valued attributes survive normalization."""
        entry: t.JsonMapping = {
            "dn": "uid=test,dc=example,dc=com",
            "uid": "test",
            "cn": ["Test", "T. User"],
        }
        result = u.TapLdap.ClientSupport.to_entry_mapping(entry)
        assert result.success
        assert result.value["uid"] == "test"
        assert result.value["cn"] == ["Test", "T. User"]

    def test_to_entry_mapping_fails_on_none(self) -> None:
        """A missing entry yields a failure result, never a silent default."""
        result = u.TapLdap.ClientSupport.to_entry_mapping(None)
        assert result.failure

    # ---- search-result size limiting contract ---------------------------

    @pytest.mark.parametrize(
        ("size_limit", "expected_count"),
        [(0, 2), (1, 1)],
    )
    def test_process_search_results_honors_size_limit(
        self,
        size_limit: int,
        expected_count: int,
    ) -> None:
        """size_limit=0 keeps all entries; a positive limit truncates."""
        entries: t.SequenceOf[t.JsonMapping] = [
            {"dn": "uid=user1,dc=test,dc=com", "uid": ["user1"]},
            {"dn": "uid=user2,dc=test,dc=com", "uid": ["user2"]},
        ]
        results = u.TapLdap.ClientSupport.process_search_results(
            entries,
            size_limit=size_limit,
        )
        assert len(results) == expected_count

    def test_process_search_results_empty_input_yields_empty(self) -> None:
        """No input entries produce no output entries."""
        assert not u.TapLdap.ClientSupport.process_search_results([], size_limit=0)

    # ---- search() end-to-end contract -----------------------------------

    def test_search_returns_normalized_entries(self) -> None:
        """search() surfaces the entries produced by the LDAP backend."""
        entries: list[t.JsonMapping] = [{"dn": "uid=test,dc=test,dc=com"}]
        with self._client(search_result=self._ldap_result(entries)) as client:
            assert client.search("dc=test,dc=com") == entries

    def test_search_size_limit_truncates_returned_entries(self) -> None:
        """The size_limit argument observably bounds the returned entries."""
        entries: list[t.JsonMapping] = [
            {"dn": "uid=a,dc=test,dc=com"},
            {"dn": "uid=b,dc=test,dc=com"},
        ]
        with self._client(search_result=self._ldap_result(entries)) as client:
            limited = client.search("dc=test,dc=com", size_limit=1)
        assert limited == [{"dn": "uid=a,dc=test,dc=com"}]

    def test_search_returns_empty_when_backend_reports_no_success(self) -> None:
        """An unsuccessful backend response yields an empty result list."""
        result = self._ldap_result([], success=False)
        with self._client(search_result=result) as client:
            assert client.search("dc=test,dc=com") == []

    # ---- test_connection() contract -------------------------------------

    @pytest.mark.parametrize("backend_success", [True, False])
    def test_test_connection_reflects_backend_success(
        self,
        *,
        backend_success: bool,
    ) -> None:
        """test_connection mirrors whether the probe search succeeded."""
        result = self._ldap_result([], success=backend_success)
        with self._client(search_result=result) as client:
            assert client.test_connection() is backend_success

    def test_test_connection_returns_false_on_backend_error(self) -> None:
        """A raising backend degrades to a False connection verdict."""
        with self._client(search_error=RuntimeError("boom")) as client:
            assert client.test_connection() is False

    # ---- health_check() contract ----------------------------------------

    def test_health_check_reports_healthy_when_connection_ok(self) -> None:
        """A working connection produces a healthy, timed health report."""
        with self._client(search_result=self._ldap_result([])) as client:
            health = client.health_check()
        assert health["status"] == "healthy"
        assert health["connection_test"] is True
        assert health["server_uri"] == "ldap://test.ldap.com:389"
        assert isinstance(health["response_time_ms"], (int, float))

    def test_health_check_reports_unhealthy_when_connection_fails(self) -> None:
        """A failing connection produces an unhealthy report."""
        with self._client(search_error=RuntimeError("boom")) as client:
            health = client.health_check()
        assert health["status"] == "unhealthy"
        assert health["connection_test"] is False

    # ---- Oracle entry normalization contract ----------------------------

    def test_normalize_oracle_entry_mirrors_password_to_userpassword(self) -> None:
        """OrclPassword is exposed as the standard userPassword attribute."""
        entry: t.MutableJsonMapping = {
            "dn": "uid=test,dc=oracle,dc=com",
            "attributes": {
                "uid": ["test"],
                "orclPassword": ["hashed_password"],
                "objectClass": ["inetOrgPerson"],
            },
        }
        result = u.TapLdap.ClientSupport.normalize_oracle_entry(entry)
        attributes = result.get("attributes")
        assert isinstance(attributes, dict)
        assert attributes["userPassword"] == ["hashed_password"]

    @pytest.mark.parametrize(
        "object_class",
        [["orclContainer"], "orclContainer"],
    )
    def test_normalize_oracle_entry_maps_container_object_class(
        self,
        object_class: t.JsonValue,
    ) -> None:
        """OrclContainer becomes organizationalUnit whether scalar or list."""
        entry: t.MutableJsonMapping = {
            "dn": "ou=test,dc=oracle,dc=com",
            "attributes": {"objectClass": object_class},
        }
        result = u.TapLdap.ClientSupport.normalize_oracle_entry(entry)
        attributes = result.get("attributes")
        assert isinstance(attributes, dict)
        obj_classes = attributes.get("objectClass")
        assert isinstance(obj_classes, list)
        assert "organizationalUnit" in obj_classes

    def test_normalize_oracle_entry_leaves_malformed_attributes_untouched(
        self,
    ) -> None:
        """A non-dict attributes payload passes through unchanged."""
        entry: t.MutableJsonMapping = {
            "dn": "uid=test,dc=oracle,dc=com",
            "attributes": "not_a_dict",
        }
        assert u.TapLdap.ClientSupport.normalize_oracle_entry(entry) == entry

    # ---- Oracle attribute extension contract ----------------------------

    def test_extend_attributes_adds_oracle_extras_when_enabled(self) -> None:
        """Enabling Oracle mode appends the canonical Oracle attributes."""
        extended = u.TapLdap.ClientSupport.extend_attributes_with_oracle_support(
            ["uid", "cn"],
            oracle_oid_mode=True,
        )
        assert extended is not None
        assert {"uid", "cn", "orclPassword", "userPassword"} <= set(extended)

    def test_extend_attributes_is_noop_when_disabled(self) -> None:
        """Disabled Oracle mode returns the caller's attributes unchanged."""
        base = ["uid", "cn"]
        assert (
            u.TapLdap.ClientSupport.extend_attributes_with_oracle_support(
                base,
                oracle_oid_mode=False,
            )
            == base
        )

    def test_extend_attributes_preserves_none_request(self) -> None:
        """A None attribute request stays None (request all attributes)."""
        assert (
            u.TapLdap.ClientSupport.extend_attributes_with_oracle_support(
                None,
                oracle_oid_mode=True,
            )
            is None
        )

    # ---- Oracle search-result processing contract -----------------------

    def test_process_oracle_search_results_enriches_when_enabled(self) -> None:
        """Oracle mode enriches each entry with the userPassword mirror."""
        search_results: t.SequenceOf[t.JsonMapping] = [
            {
                "dn": "uid=test1,dc=oracle,dc=com",
                "attributes": {"orclPassword": ["pass1"]},
            },
        ]
        results = u.TapLdap.ClientSupport.process_oracle_search_results(
            search_results,
            oracle_oid_mode=True,
        )
        attributes = results[0].get("attributes")
        assert isinstance(attributes, dict)
        assert attributes["userPassword"] == ["pass1"]

    def test_process_oracle_search_results_passthrough_when_disabled(self) -> None:
        """Disabled Oracle mode returns entries verbatim."""
        search_results: t.SequenceOf[t.JsonMapping] = [
            {"dn": "uid=test2,dc=oracle,dc=com", "attributes": {"uid": ["test2"]}},
        ]
        results = u.TapLdap.ClientSupport.process_oracle_search_results(
            search_results,
            oracle_oid_mode=False,
        )
        assert list(results) == list(search_results)

    # ---- search_with_oracle_support() contract --------------------------

    def test_search_with_oracle_support_enriches_entries(self) -> None:
        """Outside an event loop, Oracle search returns enriched entries."""
        entries: list[t.JsonMapping] = [
            {"dn": "uid=t,dc=oracle,dc=com", "attributes": {"orclPassword": ["p"]}},
        ]
        with self._client(search_result=self._ldap_result(entries)) as client:
            results = list(
                client.search_with_oracle_support(
                    "dc=oracle,dc=com",
                    "(uid=*)",
                    ["uid"],
                    oracle_oid_mode=True,
                ),
            )
        attributes = results[0].get("attributes")
        assert isinstance(attributes, dict)
        assert attributes["userPassword"] == ["p"]

    def test_search_with_oracle_support_refuses_inside_running_loop(self) -> None:
        """Inside an active event loop the Oracle search yields no entries."""
        with self._client(search_result=self._ldap_result([])) as client:

            async def _invoke() -> t.SequenceOf[t.JsonMapping]:
                return client.search_with_oracle_support(
                    "dc=oracle,dc=com",
                    oracle_oid_mode=True,
                )

            assert list(asyncio.run(_invoke())) == []

    # ---- delegation contract --------------------------------------------

    def test_unknown_attributes_delegate_to_backend(self) -> None:
        """Attributes absent on the wrapper resolve against the LDAP backend."""
        with self._client(search_result=self._ldap_result([])) as client:
            with contextlib.suppress(AttributeError):
                _ = client.whoami
            assert callable(client.search)
