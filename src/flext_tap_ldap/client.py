"""FlextTapLdapClient - LDAP client infrastructure for FLEXT Tap LDAP.

Consolidates LDAP client functionality with testing convenience wrapper.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import time
from asyncio import get_running_loop, new_event_loop, set_event_loop

from flext_ldap import FlextLdap
from flext_tap_ldap import c, m, p, t, u

logger = u.fetch_logger(__name__)


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
            settings: m.Ldap.ConnectionConfig | None = None,
            *,
            page_size: int = c.TapLdap.DEFAULT_PAGE_SIZE,
            **convenience_kwargs: t.Scalar,
        ) -> None:
            """Initialize with Parameter Object Pattern (preferred).

            Preferred Usage (Parameter Object Pattern):
                settings = m.Ldap.ConnectionConfig(
                    host="ldap.example.com", port=389
                )
                client = FlextTapLdapClient.LDAPClient(settings=settings)

            Testing convenience Usage:
                client = FlextTapLdapClient.LDAPClient(
                    host="ldap.example.com", port=389
                )
            """
            self._flext_api: p.Ldap.LdapClient
            self.config: m.Ldap.ConnectionConfig
            self.host: str
            self.port: int
            self.bind_dn: str | None
            self.password: str | None
            self.use_ssl: bool
            self.timeout: int
            self.page_size: int = page_size
            self._bind_dn: str | None
            self._password: str | None
            client_config = (
                settings
                if settings is not None
                else self._create_config_from_kwargs(**convenience_kwargs)
            )
            self._initialize_flext_api(client_config)

        def __getattr__(self, name: str) -> t.JsonMapping:
            """Delegate unknown attributes to the real API."""
            return getattr(self._flext_api, name)

        @property
        def server_uri(self) -> str:
            """The server URI for testing convenience."""
            server_uri: str = u.TapLdap.ClientSupport.build_server_uri(
                self.host,
                self.port,
                use_ssl=self.use_ssl,
            )
            return server_uri

        def health_check(self) -> t.ScalarMapping:
            """Perform health check for testing convenience."""
            start_time = time.time()
            connection_ok: bool = self.test_connection()
            end_time = time.time()
            response_time_ms: float = round((end_time - start_time) * 1000, 2)
            return {
                "status": c.HealthStatus.HEALTHY.value
                if connection_ok
                else c.HealthStatus.UNHEALTHY.value,
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
        ) -> t.SequenceOf[t.JsonMapping]:
            """Search for entries using flext-ldap infrastructure (synchronous).

            Returns a list of entries for testing convenience with Singer streams.

            Refactored for lower complexity using Single Responsibility Principle.
            """
            ldap_scope = u.TapLdap.ClientSupport.normalize_scope(scope)
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
        ) -> t.SequenceOf[t.JsonMapping]:
            """Search with Oracle OID support for testing convenience.

            Refactored using Single Responsibility Principle to reduce complexity.
            Each step now has its own dedicated method.
            """
            extended_attributes = (
                u.TapLdap.ClientSupport.extend_attributes_with_oracle_support(
                    attributes,
                    oracle_oid_mode=oracle_oid_mode,
                )
            )
            try:
                get_running_loop()
                logger.warning(
                    "Oracle LDAP search inside an active event loop is not supported",
                )
                return []
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
                result = self._flext_api.search(test_search_options)
                return result.success
            except (RuntimeError, ValueError, TypeError, c.ValidationError) as e:
                err_msg = str(e)
                logger.warning("LDAP connection test failed: %s", err_msg)
                return False

        def _create_config_from_kwargs(
            self,
            **convenience_kwargs: t.Scalar,
        ) -> m.Ldap.ConnectionConfig:
            """Create settings from convenience keyword arguments."""

            def _run__create_config_from_kwargs() -> m.Ldap.ConnectionConfig:
                config_dict: t.MutableJsonMapping = {
                    "host": u.to_str(
                        convenience_kwargs.get("host"),
                        default="",
                    ),
                    "port": u.to_int(
                        convenience_kwargs.get("port"),
                        default=c.Ldap.PORT,
                    ),
                    "bind_dn": u.to_optional_str(
                        convenience_kwargs.get("bind_dn"),
                    ),
                    "use_ssl": u.to_bool(
                        convenience_kwargs.get("use_ssl"),
                    ),
                    "timeout": u.to_int(
                        convenience_kwargs.get("timeout"),
                        default=c.TapLdap.DEFAULT_SEARCH_TIMEOUT,
                    ),
                }
                password_val = convenience_kwargs.get("password")
                if password_val is not None:
                    config_dict["bind_password"] = u.to_str(password_val)
                bind_password_val = convenience_kwargs.get("bind_password")
                if bind_password_val is not None:
                    config_dict["bind_password"] = u.to_str(bind_password_val)
                return m.Ldap.ConnectionConfig.model_validate(config_dict)

            try:
                return _run__create_config_from_kwargs()
            except c.ValidationError as e:
                host_val = convenience_kwargs.get("host")
                if not host_val or not isinstance(host_val, str):
                    msg = "Either 'settings' or valid string 'host' must be provided"
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
        ) -> t.SequenceOf[t.JsonMapping]:
            """Execute Oracle search in new event loop.

            Single Responsibility: Handle only event loop management for Oracle search.
            """
            loop = new_event_loop()
            set_event_loop(loop)
            try:
                search_result: t.SequenceOf[t.JsonMapping] = self.search(
                    base_dn,
                    search_filter,
                    attributes,
                )
                processed_results: t.SequenceOf[t.JsonMapping] = (
                    u.TapLdap.ClientSupport.process_oracle_search_results(
                        search_result,
                        oracle_oid_mode=oracle_oid_mode,
                    )
                )
                return processed_results
            finally:
                loop.close()
                set_event_loop(None)

        def _initialize_flext_api(
            self,
            client_config: m.Ldap.ConnectionConfig,
        ) -> None:
            """Initialize the ldap API with the given configuration."""
            self.config = client_config
            self._flext_api = FlextLdap()
            self.host = client_config.host
            self.port = client_config.port
            self._bind_dn = client_config.bind_dn
            self.bind_dn = client_config.bind_dn
            self._password = client_config.bind_password
            self.password = client_config.bind_password
            self.use_ssl = client_config.use_ssl
            self.timeout = client_config.timeout

        def _perform_search(
            self,
            base_dn: str,
            search_filter: str,
            attributes: t.StrSequence | None,
            ldap_scope: str,
            size_limit: int,
        ) -> t.SequenceOf[t.JsonMapping]:
            """Perform actual LDAP search.

            Single Responsibility: Handle only search execution.
            """
            try:
                normalized_config = m.Ldap.NormalizedConfig(
                    scope=ldap_scope,
                    filter_str=search_filter,
                    size_limit=size_limit,
                    time_limit=c.TapLdap.DEFAULT_SEARCH_TIMEOUT,
                    attributes=attributes,
                )
                search_options = m.Ldap.SearchOptions.normalized(
                    base_dn,
                    settings=normalized_config,
                )
                result = self._flext_api.search(search_options)
                if not (result.success and result.value):
                    return []
                processed_entries: t.SequenceOf[t.JsonMapping] = (
                    u.TapLdap.ClientSupport.process_search_results(
                        result.value.entries,
                        size_limit=size_limit,
                    )
                )
                return processed_entries
            except c.Meltano.SINGER_SAFE_EXCEPTIONS as e:
                err_msg = f"LDAP search failed: {e}"
                logger.exception("LDAP search failed: %s", err_msg)
                raise RuntimeError(err_msg) from e


__all__: t.StrSequence = ("FlextTapLdapClient",)
