"""FlextTapLdapClient - LDAP client infrastructure for FLEXT Tap LDAP.

Consolidates LDAP client functionality with testing convenience wrapper.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import time
from asyncio import get_running_loop, new_event_loop, set_event_loop
from collections.abc import Mapping, MutableSequence, Sequence

from pydantic import BaseModel, ValidationError

from flext_core import FlextLogger, r
from flext_ldap import ldap
from flext_tap_ldap import c, m, t

logger = FlextLogger(__name__)


class FlextTapLdapClient:
    """LDAP client infrastructure container with testing convenience wrapper.

    Consolidates LDAP client functionality following FlextTapLdap[Module] pattern
    with nested LDAPClient and LDAPClientConfig classes.
    """

    class LDAPClient:
        """Testing convenience LDAP client wrapper.

        Provides the old interface while using ldap internally.
        This eliminates code duplication while maintaining testing convenience.
        """

        def __init__(
            self,
            config: m.TapLdap.LdapClientConfig | None = None,
            **convenience_kwargs: t.Scalar,
        ) -> None:
            """Initialize with Parameter Object Pattern (preferred).

            Preferred Usage (Parameter Object Pattern):
                config = m.TapLdap.LdapClientConfig(
                    host="ldap.example.com", port=389
                )
                client = FlextTapLdapClient.LDAPClient(config=config)

            Testing convenience Usage:
                client = FlextTapLdapClient.LDAPClient(
                    host="ldap.example.com", port=389
                )
            """
            self._flext_api: ldap
            self._config: m.Ldap.ConnectionConfig
            self.host: str
            self.port: int
            self.bind_dn: str | None
            self.password: str | None
            self.use_ssl: bool
            self.timeout: int
            self.page_size: int
            self._bind_dn: str | None
            self._password: str | None
            client_config = (
                config
                if config is not None
                else self._create_config_from_kwargs(**convenience_kwargs)
            )
            self._initialize_flext_api(client_config)

        def __getattr__(self, name: str) -> t.ContainerMapping:
            """Delegate unknown attributes to the real API."""
            return getattr(self._flext_api, name)

        @property
        def server_uri(self) -> str:
            """Get server URI for testing convenience."""
            protocol = "ldaps" if self.use_ssl else "ldap"
            return f"{protocol}://{self.host}:{self.port}"

        def health_check(self) -> t.ScalarMapping:
            """Perform health check for testing convenience."""
            start_time = time.time()
            connection_ok: bool = self.test_connection()
            end_time = time.time()
            response_time_ms: float = round((end_time - start_time) * 1000, 2)
            return {
                "status": "healthy" if connection_ok else "unhealthy",
                "server_uri": self.server_uri,
                "connection_test": connection_ok,
                "response_time_ms": response_time_ms,
            }

        def search(
            self,
            base_dn: str,
            search_filter: str = "(objectClass=*)",
            attributes: t.StrSequence | None = None,
            scope: str = "SUBTREE",
            size_limit: int = 0,
        ) -> Sequence[t.ContainerMapping]:
            """Search for entries using flext-ldap infrastructure (synchronous).

            Returns a list of entries for testing convenience with Singer streams.

            Refactored for lower complexity using Single Responsibility Principle.
            """
            ldap_scope = self._convert_scope_to_enum(scope)
            return self._perform_search(
                base_dn,
                search_filter,
                attributes,
                ldap_scope,
                size_limit,
            )

        def search_with_oracle_support(
            self,
            base_dn: str,
            search_filter: str = "(objectClass=*)",
            attributes: t.StrSequence | None = None,
            *,
            oracle_oid_mode: bool = False,
        ) -> Sequence[t.ContainerMapping]:
            """Search with Oracle OID support for testing convenience.

            Refactored using Single Responsibility Principle to reduce complexity.
            Each step now has its own dedicated method.
            """
            extended_attributes = self._extend_attributes_with_oracle_support(
                attributes,
                oracle_oid_mode=oracle_oid_mode,
            )
            try:
                get_running_loop()
                msg = "Oracle LDAP search within an existing event loop is not implemented natively."
                raise NotImplementedError(msg)
            except RuntimeError:
                return self._execute_oracle_search_in_new_loop(
                    base_dn=base_dn,
                    search_filter=search_filter,
                    attributes=extended_attributes,
                    oracle_oid_mode=oracle_oid_mode,
                )

        def test_connection(self) -> bool:
            """Test the connection to the LDAP server."""
            try:
                test_search_options = m.Ldap.SearchOptions(
                    base_dn="dc=test",
                    filter_str="(objectClass=*)",
                    scope=c.Ldap.SearchScope.BASE,
                    attributes=None,
                    size_limit=1,
                    time_limit=5,
                )
                result: r[m.Ldap.SearchResult] = self._flext_api.search(
                    test_search_options,
                )
                return result.is_success
            except (RuntimeError, ValueError, TypeError, ValidationError) as e:
                err_msg = str(e)
                logger.warning("LDAP connection test failed: %s", err_msg)
                return False

        def _build_server_uri(self) -> str:
            """Build server URI from connection parameters.

            Single Responsibility: Handle only URI construction.
            """
            protocol = "ldaps" if self.use_ssl else "ldap"
            return f"{protocol}://{self.host}:{self.port}"

        def _convert_entry_to_dict(
            self,
            entry_data: t.RuntimeData | t.ContainerMapping | None,
        ) -> r[t.MutableContainerMapping]:
            """Convert FlextLdapModels.Entry to dict format for testing.

            Single Responsibility: Handle only entry format conversion.
            """
            if entry_data is None:
                return r[t.MutableContainerMapping].fail(
                    "Cannot convert None entry data",
                )
            if isinstance(entry_data, BaseModel):
                dn_value: str = str(getattr(entry_data, "dn", ""))
                model_data: t.MutableContainerMapping = dict(entry_data.model_dump())
                attrs_val: t.NormalizedValue = model_data.get("attributes", {})
                attrs_dict: t.MutableContainerMapping
                if isinstance(attrs_val, dict):
                    attrs_dict = attrs_val
                else:
                    return r[t.MutableContainerMapping].ok({"dn": dn_value})
                entry_dict: t.MutableContainerMapping = {"dn": dn_value}
                for key_str, val in attrs_dict.items():
                    typed_list: t.MutableContainerList = (
                        val if isinstance(val, list) else []
                    )
                    if isinstance(val, list) and len(typed_list) == 1:
                        entry_dict[key_str] = typed_list[0]
                    else:
                        entry_dict[key_str] = val
                return r[t.MutableContainerMapping].ok(entry_dict)
            if isinstance(entry_data, Mapping):
                result: t.MutableContainerMapping = {}
                for key, value in entry_data.items():
                    if isinstance(
                        value,
                        (str, int, float, bool, list, dict, type(None)),
                    ):
                        result[str(key)] = value
                return r[t.MutableContainerMapping].ok(result)
            return r[t.MutableContainerMapping].fail(
                f"Unsupported entry data type: {type(entry_data).__name__}",
            )

        def _convert_scope_to_enum(self, scope: str) -> str:
            """Convert scope string to flext-ldap scope string.

            Single Responsibility: Handle only scope conversion logic.
            """
            scope_map: t.StrMapping = {
                "SUBTREE": "SUBTREE",
                "ONELEVEL": "ONELEVEL",
                "BASE": "BASE",
            }
            return scope_map.get(scope.upper(), "SUBTREE")

        def _create_config_from_kwargs(
            self,
            **convenience_kwargs: t.Scalar,
        ) -> m.TapLdap.LdapClientConfig:
            """Create config from convenience keyword arguments."""
            try:
                config_dict = {
                    "host": convenience_kwargs.get("host", ""),
                    "port": convenience_kwargs.get(
                        "port", c.Ldap.ConnectionDefaults.PORT
                    ),
                    "bind_dn": convenience_kwargs.get("bind_dn") or None,
                    "password": convenience_kwargs.get("password") or None,
                    "use_ssl": bool(convenience_kwargs.get("use_ssl")),
                    "timeout": convenience_kwargs.get(
                        "timeout", c.TapLdap.DEFAULT_SEARCH_TIMEOUT
                    ),
                    "page_size": convenience_kwargs.get(
                        "page_size", c.TapLdap.DEFAULT_PAGE_SIZE
                    ),
                }
                return m.TapLdap.LdapClientConfig.model_validate(config_dict)
            except ValidationError as e:
                host_val = convenience_kwargs.get("host")
                if not host_val or not isinstance(host_val, str):
                    msg = "Either 'config' or valid string 'host' must be provided"
                    raise ValueError(msg) from e
                msg = f"Invalid configuration: {e}"
                raise ValueError(msg) from e

        def _execute_oracle_search_in_new_loop(
            self,
            base_dn: str,
            search_filter: str,
            attributes: t.StrSequence | None,
            *,
            oracle_oid_mode: bool,
        ) -> Sequence[t.ContainerMapping]:
            """Execute Oracle search in new event loop.

            Single Responsibility: Handle only event loop management for Oracle search.
            """
            loop = new_event_loop()
            set_event_loop(loop)
            try:
                search_result: Sequence[t.ContainerMapping] = self.search(
                    base_dn,
                    search_filter,
                    attributes,
                )
                return self._process_oracle_search_results(
                    search_result,
                    oracle_oid_mode=oracle_oid_mode,
                )
            finally:
                loop.close()
                set_event_loop(None)

        def _extend_attributes_with_oracle_support(
            self,
            attributes: t.StrSequence | None,
            *,
            oracle_oid_mode: bool,
        ) -> MutableSequence[str] | None:
            """Extend attributes list with Oracle-specific attributes.

            Single Responsibility: Handle only Oracle attribute extension logic.
            """
            if not oracle_oid_mode or not attributes:
                return list(attributes) if attributes else None
            oracle_attrs = ["orclPassword", "orclPasswordAttribute", "userPassword"]
            extended_attributes = list(attributes)
            for oracle_attr in oracle_attrs:
                if oracle_attr not in extended_attributes:
                    extended_attributes.append(oracle_attr)
            return extended_attributes

        def _initialize_flext_api(
            self,
            client_config: m.TapLdap.LdapClientConfig,
        ) -> None:
            """Initialize the ldap API with the given configuration."""
            flext_connection_config = m.Ldap.ConnectionConfig(
                host=client_config.host,
                port=int(client_config.port),
                use_ssl=bool(client_config.use_ssl),
                bind_dn=client_config.bind_dn,
                bind_password=client_config.password,
                timeout=int(client_config.timeout),
            )
            self._flext_api = ldap()
            self._config = flext_connection_config
            self.host = client_config.host
            self.port = client_config.port
            self.bind_dn = client_config.bind_dn
            self.password = client_config.password
            self.use_ssl = client_config.use_ssl
            self.timeout = client_config.timeout
            self.page_size = client_config.page_size
            self._bind_dn = client_config.bind_dn
            self._password = client_config.password

        def _perform_search(
            self,
            base_dn: str,
            search_filter: str,
            attributes: t.StrSequence | None,
            ldap_scope: str,
            size_limit: int,
        ) -> MutableSequence[t.MutableContainerMapping]:
            """Perform actual LDAP search.

            Single Responsibility: Handle only search execution.
            """
            self._build_server_uri()
            try:
                search_options = m.Ldap.SearchOptions(
                    base_dn=base_dn,
                    filter_str=search_filter,
                    scope=ldap_scope,
                    attributes=attributes,
                    size_limit=size_limit,
                    time_limit=c.TapLdap.DEFAULT_SEARCH_TIMEOUT,
                )
                result: r[m.Ldap.SearchResult] = self._flext_api.search(search_options)
                return self._process_search_results(result, size_limit)
            except c.Meltano.SINGER_SAFE_EXCEPTIONS as e:
                err_msg = f"LDAP search failed: {e}"
                logger.exception("LDAP search failed: %s", err_msg)
                raise RuntimeError(err_msg) from e

        def _process_oracle_entry(
            self,
            entry: t.MutableContainerMapping,
        ) -> t.MutableContainerMapping:
            """Process Oracle-specific LDAP entries for testing convenience."""
            raw_attrs: t.NormalizedValue = entry.get("attributes", {})
            attributes: t.MutableContainerMapping = {}
            if isinstance(raw_attrs, dict):
                attributes.update(raw_attrs)
            else:
                return entry
            if "orclPassword" in attributes:
                pwd_val = attributes.get("orclPassword")
                if pwd_val is not None:
                    attributes["userPassword"] = pwd_val
            if "objectClass" in attributes:
                raw_obj_classes = attributes["objectClass"]
                obj_classes: MutableSequence[str] = []
                if isinstance(raw_obj_classes, str):
                    obj_classes = [raw_obj_classes]
                elif isinstance(raw_obj_classes, list):
                    obj_classes = [str(item) for item in raw_obj_classes]
                if (
                    "orclContainer" in obj_classes
                    and "organizationalUnit" not in obj_classes
                ):
                    obj_classes.append("organizationalUnit")
                    attributes["objectClass"] = obj_classes
            entry["attributes"] = attributes
            return entry

        def _process_search_results(
            self,
            result: r[m.Ldap.SearchResult],
            size_limit: int,
        ) -> MutableSequence[t.MutableContainerMapping]:
            """Process LDAP search results with size limiting.

            Single Responsibility: Handle only result processing logic.
            """
            entries: MutableSequence[t.MutableContainerMapping] = []
            if not (result.is_success and result.value):
                return entries
            search_result = result.value
            data_entries = search_result.entries
            for entries_returned, entry_data in enumerate(data_entries):
                if size_limit > 0 and entries_returned >= size_limit:
                    break
                convert_result = self._convert_entry_to_dict(entry_data)
                if convert_result.is_failure:
                    logger.warning(
                        "Skipping entry %d: %s",
                        entries_returned,
                        convert_result.error or "conversion failed",
                    )
                    continue
                entries.append(convert_result.value)
            return entries

        def _process_oracle_search_results(
            self,
            search_result: Sequence[m.Ldif.Entry] | Sequence[t.ContainerMapping],
            *,
            oracle_oid_mode: bool,
        ) -> MutableSequence[t.MutableContainerMapping]:
            """Process search results with Oracle OID support.

            Single Responsibility: Handle only result processing logic.
            """
            results: MutableSequence[t.MutableContainerMapping] = []
            for idx, entry in enumerate(search_result):
                if isinstance(entry, Mapping):
                    entry_dict: t.MutableContainerMapping = {
                        str(key): value for key, value in entry.items()
                    }
                else:
                    convert_result = self._convert_entry_to_dict(entry)
                    if convert_result.is_failure:
                        logger.warning(
                            "Skipping Oracle entry %d: %s",
                            idx,
                            convert_result.error or "conversion failed",
                        )
                        continue
                    entry_dict = convert_result.value
                if oracle_oid_mode:
                    processed_entry = self._process_oracle_entry(entry_dict)
                    results.append(processed_entry)
                else:
                    results.append(entry_dict)
            return results


__all__: t.StrSequence = [
    "FlextTapLdapClient",
]
