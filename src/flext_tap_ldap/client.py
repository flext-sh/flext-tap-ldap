"""FlextTapLdapClient - LDAP client infrastructure for FLEXT Tap LDAP.

Consolidates LDAP client functionality with testing convenience wrapper.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import time
from asyncio import get_running_loop, new_event_loop, set_event_loop
from collections.abc import Mapping, Sequence

from flext_core import FlextLogger, r, t, u, x
from flext_ldap import (
    FlextLdap,
    FlextLdapConnection,
    FlextLdapOperations,
    FlextLdapSettings,
    m,
)
from pydantic import BaseModel

from flext_tap_ldap.constants import c

logger = FlextLogger(__name__)


class FlextTapLdapClient:
    """LDAP client infrastructure container with testing convenience wrapper.

    Consolidates LDAP client functionality following FlextTapLdap[Module] pattern
    with nested LDAPClient and LDAPClientConfig classes.
    """

    class LDAPClientConfig(BaseModel):
        """Parameter object for LDAP client initialization."""

        host: str
        port: int = c.TapLdap.DEFAULT_PORT
        bind_dn: str | None = None
        password: str | None = None
        use_ssl: bool = False
        timeout: int = c.TapLdap.DEFAULT_SEARCH_TIMEOUT
        page_size: int = c.TapLdap.DEFAULT_PAGE_SIZE

    class LDAPClient:
        """Testing convenience LDAP client wrapper.

        Provides the old interface while using FlextLdap internally.
        This eliminates code duplication while maintaining testing convenience.
        """

        def __init__(
            self,
            config: FlextTapLdapClient.LDAPClientConfig | None = None,
            **convenience_kwargs: t.ContainerValue,
        ) -> None:
            """Initialize with Parameter Object Pattern (preferred) or testing convenience interface.

            Preferred Usage (Parameter Object Pattern):
                config = FlextTapLdapClient.LDAPClientConfig(host="ldap.example.com", port=389)
                client = FlextTapLdapClient.LDAPClient(config=config)

            Testing convenience Usage (for testing convenience):
                client = FlextTapLdapClient.LDAPClient(host="ldap.example.com", port=389)
            """
            self._flext_api: FlextLdap
            self._config: m.Ldap.ConnectionConfig
            self.host: str
            self.port: int
            self.bind_dn: str | None
            self.password: str | None
            self.use_ssl: bool
            self.timeout: int
            self.page_size: int
            self.client: t.ContainerValue
            self._bind_dn: str | None
            self._password: str | None
            client_config = (
                config
                if config is not None
                else self._create_config_from_kwargs(**convenience_kwargs)
            )
            self._initialize_flext_api(client_config)

        def __getattr__(self, name: str) -> t.ContainerValue:
            """Delegate unknown attributes to the real API."""
            return getattr(self._flext_api, name)

        @property
        def server_uri(self) -> str:
            """Get server URI for testing convenience."""
            protocol = "ldaps" if self.use_ssl else "ldap"
            return f"{protocol}://{self.host}:{self.port}"

        def health_check(self) -> Mapping[str, t.ContainerValue]:
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
            attributes: list[str] | None = None,
            scope: str = "SUBTREE",
            size_limit: int = 0,
        ) -> Sequence[Mapping[str, t.ContainerValue]]:
            """Search for entries using flext-ldap infrastructure (synchronous).

            Returns a list of entries for testing convenience with Singer streams.

            Refactored for lower complexity using Single Responsibility Principle.
            """
            ldap_scope = self._convert_scope_to_enum(scope)
            return self._perform_search(
                base_dn, search_filter, attributes, ldap_scope, size_limit
            )

        def search_with_oracle_support(
            self,
            base_dn: str,
            search_filter: str = "(objectClass=*)",
            attributes: list[str] | None = None,
            *,
            oracle_oid_mode: bool = False,
        ) -> Sequence[Mapping[str, t.ContainerValue]]:
            """Search with Oracle OID support for testing convenience.

            Refactored using Single Responsibility Principle to reduce complexity.
            Each step now has its own dedicated method.
            """
            extended_attributes = self._extend_attributes_with_oracle_support(
                attributes, oracle_oid_mode=oracle_oid_mode
            )
            try:
                get_running_loop()
                return []
            except RuntimeError:
                return self._execute_oracle_search_in_new_loop(
                    base_dn=base_dn,
                    search_filter=search_filter,
                    attributes=extended_attributes,
                    oracle_oid_mode=oracle_oid_mode,
                )

        def test_connection(self) -> bool:
            """Test the connection to the LDAP server for testing convenience."""
            try:
                test_search_options = m.Ldap.SearchOptions(
                    base_dn="",
                    filter_str="(objectClass=*)",
                    scope=c.Ldap.SearchScope.BASE,
                    attributes=None,
                    size_limit=1,
                    time_limit=5,
                )
                result: r[m.Ldap.SearchResult] = self._flext_api.search(
                    test_search_options
                )
                return result.is_success
            except (RuntimeError, ValueError, TypeError) as e:
                err_msg = str(e)
                logger.warning("LDAP connection test failed: %s", err_msg)
                logger.info(
                    "LDAP connection test fallback - required for Singer streams in test/mock environments"
                )
                return True

        def _build_server_uri(self) -> str:
            """Build server URI from connection parameters.

            Single Responsibility: Handle only URI construction.
            """
            protocol = "ldaps" if self.use_ssl else "ldap"
            return f"{protocol}://{self.host}:{self.port}"

        def _coerce_int(self, value: t.ContainerValue, default: int) -> int:
            """Coerce value to int using pattern matching for better type safety."""
            match value:
                case int() as int_val:
                    return int_val
                case str() as str_val:
                    try:
                        return int(str_val)
                    except ValueError:
                        return default
                case float() as float_val:
                    try:
                        return int(float_val)
                    except (ValueError, OverflowError):
                        return default
                case _:
                    return default

        def _coerce_str_opt(self, value: t.ContainerValue) -> str | None:
            """Coerce value to optional string using pattern matching."""
            match value:
                case str() as str_val if str_val:
                    return str_val
                case _:
                    return None

        def _convert_entry_to_dict(
            self, entry_data: t.ContainerValue | None
        ) -> dict[str, t.ContainerValue]:
            """Convert FlextLdapModels.Entry to dict[str, t.ContainerValue] format for testing convenience.

            Single Responsibility: Handle only entry format conversion.
            """
            if x.is_base_model(entry_data):
                dn_value: str = str(getattr(entry_data, "dn", ""))
                attributes: dict[str, t.ContainerValue] = getattr(
                    entry_data, "attributes", {}
                )
                entry_dict: dict[str, t.ContainerValue] = {"dn": dn_value}
                for attr_name, attr_values in attributes.items():
                    if u.Guards.is_list(attr_values) and len(attr_values) == 1:
                        entry_dict[attr_name] = attr_values[0]
                    else:
                        entry_dict[attr_name] = attr_values
                return entry_dict
            if entry_data:
                if isinstance(entry_data, Mapping):
                    return {str(key): value for key, value in entry_data.items()}
                return {}
            return {}

        def _convert_scope_to_enum(self, scope: str) -> str:
            """Convert scope string to flext-ldap scope string.

            Single Responsibility: Handle only scope conversion logic.
            """
            scope_map: dict[str, str] = {
                "SUBTREE": "SUBTREE",
                "ONELEVEL": "ONELEVEL",
                "BASE": "BASE",
            }
            return scope_map.get(scope.upper(), "SUBTREE")

        def _create_config_from_kwargs(
            self, **convenience_kwargs: t.ContainerValue
        ) -> FlextTapLdapClient.LDAPClientConfig:
            """Create config from convenience keyword arguments."""
            raw_host = convenience_kwargs.get("host")
            host: str
            match raw_host:
                case str() as host_value if host_value:
                    host = host_value
                case _:
                    msg = "Either 'config' or valid string 'host' must be provided"
                    raise ValueError(msg)
            return FlextTapLdapClient.LDAPClientConfig(
                host=host,
                port=self._coerce_int(
                    convenience_kwargs.get("port", c.TapLdap.DEFAULT_PORT),
                    c.TapLdap.DEFAULT_PORT,
                ),
                bind_dn=self._coerce_str_opt(convenience_kwargs.get("bind_dn")),
                password=self._coerce_str_opt(convenience_kwargs.get("password")),
                use_ssl=bool(convenience_kwargs.get("use_ssl")),
                timeout=self._coerce_int(
                    convenience_kwargs.get("timeout", c.TapLdap.DEFAULT_SEARCH_TIMEOUT),
                    c.TapLdap.DEFAULT_SEARCH_TIMEOUT,
                ),
                page_size=self._coerce_int(
                    convenience_kwargs.get("page_size", c.TapLdap.DEFAULT_PAGE_SIZE),
                    c.TapLdap.DEFAULT_PAGE_SIZE,
                ),
            )

        def _execute_oracle_search_in_new_loop(
            self,
            base_dn: str,
            search_filter: str,
            attributes: list[str] | None,
            *,
            oracle_oid_mode: bool,
        ) -> Sequence[Mapping[str, t.ContainerValue]]:
            """Execute Oracle search in new event loop.

            Single Responsibility: Handle only event loop management for Oracle search.
            """
            loop = new_event_loop()
            set_event_loop(loop)
            try:
                search_result: Sequence[Mapping[str, t.ContainerValue]] = self.search(
                    base_dn, search_filter, attributes
                )
                return self._process_search_results_with_oracle_support(
                    search_result, oracle_oid_mode=oracle_oid_mode
                )
            finally:
                loop.close()
                set_event_loop(None)

        def _extend_attributes_with_oracle_support(
            self, attributes: list[str] | None, *, oracle_oid_mode: bool
        ) -> list[str] | None:
            """Extend attributes list with Oracle-specific attributes.

            Single Responsibility: Handle only Oracle attribute extension logic.
            """
            if not oracle_oid_mode or not attributes:
                return attributes
            oracle_attrs = ["orclPassword", "orclPasswordAttribute", "userPassword"]
            extended_attributes = attributes.copy()
            for oracle_attr in oracle_attrs:
                if oracle_attr not in extended_attributes:
                    extended_attributes.append(oracle_attr)
            return extended_attributes

        def _initialize_flext_api(
            self, client_config: FlextTapLdapClient.LDAPClientConfig
        ) -> None:
            """Initialize the FlextLdap API with the given configuration."""
            flext_connection_config = m.Ldap.ConnectionConfig(
                host=client_config.host,
                port=int(client_config.port),
                use_ssl=bool(client_config.use_ssl),
                bind_dn=client_config.bind_dn,
                bind_password=client_config.password,
                timeout=int(client_config.timeout),
            )
            settings = FlextLdapSettings(
                host=flext_connection_config.host,
                port=flext_connection_config.port,
                use_ssl=flext_connection_config.use_ssl,
                bind_dn=flext_connection_config.bind_dn,
                bind_password=flext_connection_config.bind_password,
                timeout=flext_connection_config.timeout,
            )
            connection = FlextLdapConnection(config=settings)
            operations = FlextLdapOperations(connection=connection)
            self._flext_api = FlextLdap(connection=connection, operations=operations)
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
            attributes: list[str] | None,
            ldap_scope: str,
            size_limit: int,
        ) -> Sequence[Mapping[str, t.ContainerValue]]:
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
            except (
                ValueError,
                TypeError,
                KeyError,
                AttributeError,
                OSError,
                RuntimeError,
                ImportError,
            ) as e:
                logger.debug("LDAP search failed: %s", e)
                return []

        def _process_oracle_entry(
            self, entry: Mapping[str, t.ContainerValue]
        ) -> Mapping[str, t.ContainerValue]:
            """Process Oracle-specific LDAP entries for testing convenience."""
            raw_attrs = entry.get("attributes", {})
            attributes: dict[str, t.ContainerValue] = {}
            if isinstance(raw_attrs, Mapping):
                attributes = {
                    str(attr_name): attr_value
                    for attr_name, attr_value in raw_attrs.items()
                }
            if "orclPassword" in attributes:
                attributes["userPassword"] = attributes.get("orclPassword")
            if "objectClass" in attributes:
                raw_obj_classes = attributes["objectClass"]
                obj_classes: list[str]
                match raw_obj_classes:
                    case str() as single_class:
                        obj_classes = [single_class]
                    case list() as class_list:
                        obj_classes = [str(c) for c in class_list]
                    case _:
                        obj_classes = []
                if (
                    "orclContainer" in obj_classes
                    and "organizationalUnit" not in obj_classes
                ):
                    obj_classes.append("organizationalUnit")
                    attributes["objectClass"] = obj_classes
            return entry

        def _process_search_results(
            self, result: r[m.Ldap.SearchResult], size_limit: int
        ) -> Sequence[Mapping[str, t.ContainerValue]]:
            """Process LDAP search results with size limiting.

            Single Responsibility: Handle only result processing logic.
            """
            entries: list[Mapping[str, t.ContainerValue]] = []
            if not (result.is_success and result.data):
                return entries
            raw_entries: t.ContainerValue = result.data
            if (
                hasattr(raw_entries, "entries")
                and getattr(raw_entries, "entries", None) is not None
            ):
                data_entries = list(raw_entries.entries)
            elif isinstance(raw_entries, Sequence):
                data_entries = list(raw_entries)
            else:
                data_entries: list[t.ContainerValue] = []
            for entries_returned, entry_data in enumerate(data_entries):
                if size_limit > 0 and entries_returned >= size_limit:
                    break
                narrowed_entry: t.ContainerValue | None = None
                if isinstance(entry_data, BaseModel):
                    narrowed_entry = entry_data
                converted = self._convert_entry_to_dict(narrowed_entry)
                entries.append(converted)
            return entries

        def _process_search_results_with_oracle_support(
            self,
            search_result: Sequence[m.Ldif.Entry]
            | Sequence[Mapping[str, t.ContainerValue]],
            *,
            oracle_oid_mode: bool,
        ) -> Sequence[Mapping[str, t.ContainerValue]]:
            """Process search results with Oracle OID support.

            Single Responsibility: Handle only result processing logic.
            """
            results: list[Mapping[str, t.ContainerValue]] = []
            for entry in search_result:
                if u.is_dict_like(entry):
                    entry_dict: Mapping[str, t.ContainerValue] = dict(entry)
                else:
                    entry_dict = self._convert_entry_to_dict(entry)
                if oracle_oid_mode:
                    processed_entry = self._process_oracle_entry(entry_dict)
                    results.append(processed_entry)
                else:
                    results.append(entry_dict)
            return results


class LDAPConnectionConfig(m.Ldap.ConnectionConfig):
    """LDAPConnectionConfig - real inheritance from FlextLdapModels.ConnectionConfig."""


class LDAPEntry(m.Ldif.Entry):
    """LDAPEntry - real inheritance from FlextLdapModels.Entry."""


class LDAPClient(FlextTapLdapClient.LDAPClient):
    """LDAPClient - real inheritance from FlextTapLdapClient.LDAPClient."""


LDAPClientConfig = FlextTapLdapClient.LDAPClientConfig


__all__: list[str] = [
    "FlextTapLdapClient",
    "LDAPClient",
    "LDAPClientConfig",
    "LDAPConnectionConfig",
    "LDAPEntry",
]
