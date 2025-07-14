"""LDAP client for flext-tap-ldap using flext-core patterns.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import logging
import ssl
import time
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from typing import TYPE_CHECKING
from typing import Any

import ldap3
from ldap3 import ALL
from ldap3 import SAFE_SYNC
from ldap3 import SIMPLE
from ldap3 import Connection
from ldap3 import Server
from ldap3 import Tls
from ldap3.core.exceptions import LDAPException
from ldap3.utils.conv import escape_filter_chars

if TYPE_CHECKING:
    from collections.abc import Generator
    from collections.abc import Iterator

logger = logging.getLogger(__name__)


class LDAPClient:
    """LDAP client for connecting and querying LDAP directories."""

    def __init__(
        self,
        host: str,
        port: int = 389,
        bind_dn: str | None = None,
        password: str | None = None,
        *,
        use_ssl: bool = False,
        timeout: int = 30,
        page_size: int = 1000,
        pool_size: int = 10,
        pool_keepalive: int = 30,
        auto_retry: bool = True,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        validate_certificates: bool = True,
        ca_certs_file: str | None = None,
        client_cert_file: str | None = None,
        client_key_file: str | None = None,
    ) -> None:
        """Initialize LDAP client.

        Args:
            host: LDAP server host
            port: LDAP server port
            bind_dn: Bind DN for authentication
            password: Password for authentication
            use_ssl: Whether to use SSL/TLS
            timeout: Connection timeout
            page_size: Page size for search operations
            pool_size: Maximum number of connections in pool
            pool_keepalive: Keepalive time for connections in pool
            auto_retry: Whether to automatically retry failed operations
            max_retries: Maximum number of retries for failed operations
            retry_delay: Delay between retries
            validate_certificates: Whether to validate certificates
            ca_certs_file: Path to CA certificates file
            client_cert_file: Path to client certificate file
            client_key_file: Path to client key file

        """
        self.host = host
        self.port = port
        self.bind_dn = bind_dn
        self.password = password
        self.use_ssl = use_ssl
        self.timeout = timeout
        self.page_size = page_size
        self.pool_size = pool_size
        self.pool_keepalive = pool_keepalive
        self.auto_retry = auto_retry
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.validate_certificates = validate_certificates
        self.ca_certs_file = ca_certs_file
        self.client_cert_file = client_cert_file
        self.client_key_file = client_key_file

        self._connection_pool: list[Connection] = (
            []
        )  # TODO(marlonsc): Initialize in __post_init__
        self._pool_lock = ThreadPoolExecutor(max_workers=1)
        self._server: Server | None = None
        self._tls_context: Tls | None = None

        self._setup_tls_context()
        self._setup_server()

    def _setup_tls_context(self) -> None:
        """Setups an TLS context for LDAP connection."""
        if not self.use_ssl:
            return

        tls_config: dict[str, Any] = {}

        if not self.validate_certificates:
            tls_config["validate"] = ssl.CERT_NONE
        else:
            tls_config["validate"] = ssl.CERT_REQUIRED

        if self.ca_certs_file:
            tls_config["ca_certs_file"] = self.ca_certs_file

        if self.client_cert_file and self.client_key_file:
            tls_config["local_certificate_file"] = self.client_cert_file
            tls_config["local_private_key_file"] = self.client_key_file

        self._tls_context = Tls(**tls_config)

    def _setup_server(self) -> None:
        """Setups a new LDAP server."""
        self._server = Server(
            host=self.host,
            port=self.port,
            use_ssl=self.use_ssl,
            get_info=ALL,
            tls=self._tls_context,
            connect_timeout=self.timeout,
        )

    def _create_connection(self) -> Connection:
        """Create a new LDAP connection.

        Returns:
            A new LDAP connection

        """
        if not self._server:
            self._setup_server()

        return Connection(
            server=self._server,
            user=self.bind_dn,
            password=self.password,
            auto_bind=True,
            authentication=SIMPLE,
            client_strategy=SAFE_SYNC,
            pool_size=self.pool_size,
            pool_keepalive=self.pool_keepalive,
            read_only=True,
            receive_timeout=self.timeout,
        )

    def _execute_with_retry(self, operation: Any, *args: Any, **kwargs: Any) -> Any:
        """Execute an operation with retry.

        Args:
            operation: The operation to execute
            *args: Positional arguments for the operation
            **kwargs: Keyword arguments for the operation

        Returns:
            The result of the operation

        """
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                return operation(*args, **kwargs)
            except LDAPException as e:
                last_exception = e
                if attempt < self.max_retries:
                    logger.warning(
                        "LDAP operation failed, retrying in %ds: %s",
                        self.retry_delay,
                        e,
                    )
                    time.sleep(self.retry_delay)
                    continue
                logger.exception(
                    "LDAP operation failed after %d retries.",
                    self.max_retries,
                )
                break

        if last_exception:
            raise last_exception
        return None

    @property
    def server_uri(self) -> str:
        """Get the server URI.

        Returns:
            The server URI

        """
        protocol = "ldaps" if self.use_ssl else "ldap"
        return f"{protocol}://{self.host}:{self.port}"

    @contextmanager
    def get_connection(self) -> Generator[Connection]:
        """Get a connection to the LDAP server.

        Yields:
            A connection to the LDAP server.

        """
        def _create_and_bind() -> ldap3.Connection:
            connection = self._create_connection()
            logger.info("Connected to LDAP server: %s", self.server_uri)
            return connection

        connection = self._execute_with_retry(_create_and_bind)

        try:
            yield connection
        finally:
            if connection and connection.bound:
                connection.unbind()
                logger.info("Disconnected from LDAP server")

    def search(
        self,
        base_dn: str,
        search_filter: str = "(object_class=*)",
        attributes: list[str] | None = None,
        scope: str = "SUBTREE",
        size_limit: int = 0,
    ) -> Iterator[dict[str, Any]]:
        """Search for entries in the LDAP server.

        Args:
            base_dn: The base DN to search from
            search_filter: The search filter to use
            attributes: The attributes to return
            scope: The scope of the search
            size_limit: The maximum number of entries to return

        Yields:
            An iterator of entries

        """
        search_scope = getattr(ldap3, scope.upper(), ldap3.SUBTREE)

        with self.get_connection() as conn:
            # Use paged search for large result sets
            entries_returned = 0

            conn.search(
                search_base=base_dn,
                search_filter=search_filter,
                search_scope=search_scope,
                attributes=attributes or ["*"],
                paged_size=self.page_size,
            )

            while True:
                for entry in conn.entries:
                    if size_limit > 0 and entries_returned >= size_limit:
                        return

                    # Convert entry to dict
                    entry_dict = {
                        "dn": entry.entry_dn,
                        "attributes": {},
                    }

                    for attr in entry:
                        attr_name = str(attr.key)
                        attr_values = attr.values

                        # Handle single vs multi-valued attributes
                        if len(attr_values) == 1:
                            entry_dict["attributes"][attr_name] = attr_values[0]
                        else:
                            entry_dict["attributes"][attr_name] = attr_values
                    yield entry_dict
                    entries_returned += 1

                # Check for more pages
                cookie = (
                    conn.result.get("controls", {})
                    .get("1.2.840.113556.1.4.319", {})
                    .get("value", {})
                    .get("cookie")
                )

                if not cookie:
                    break

                # Continue paged search
                conn.search(
                    search_base=base_dn,
                    search_filter=search_filter,
                    search_scope=search_scope,
                    attributes=attributes or ["*"],
                    paged_size=self.page_size,
                    paged_cookie=cookie,
                )

    def get_schema(self) -> dict[str, Any]:
        """Get the schema from the LDAP server.

        Raises:
            LDAPException: If the schema cannot be retrieved

        Returns:
            A dictionary containing the schema

        """
        with self.get_connection() as conn:
            # Get schema from DSE
            conn.search(
                search_base="",
                search_filter="(object_class=*)",
                search_scope=ldap3.BASE,
                attributes=["subschemaSubentry"],
            )

            if not conn.entries:
                msg = "Could not find schema subentry"
                raise LDAPException(msg)

            schema_dn = conn.entries[0]["subschemaSubentry"][0]

            # Get schema details
            conn.search(
                search_base=schema_dn,
                search_filter="(object_class=*)",
                search_scope=ldap3.BASE,
                attributes=["objectClasses", "attributeTypes", "ldapSyntaxes"],
            )

            if not conn.entries:
                msg = f"Could not retrieve schema from {schema_dn}"
                raise LDAPException(msg)

            schema_entry = conn.entries[0]

            return {
                "object_classes": schema_entry.get("objectClasses", []),
                "attribute_types": schema_entry.get("attributeTypes", []),
                "ldap_syntaxes": schema_entry.get("ldapSyntaxes", []),
            }

    def test_connection(self) -> bool:
        """Test the connection to the LDAP server.

        Returns:
            True if the connection is successful, False otherwise

        """
        try:
            with self.get_connection() as conn:
                # Perform simple search to verify connection
                conn.search(
                    search_base="",
                    search_filter="(object_class=*)",
                    search_scope=ldap3.BASE,
                    attributes=["namingContexts"],
                    size_limit=1,
                )
                return bool(conn.result["result"] == 0)
        except LDAPException:
            logger.exception("Connection test failed.")
            return False

    def search_with_oracle_support(
        self,
        base_dn: str,
        search_filter: str = "(object_class=*)",
        attributes: list[str] | None = None,
        *,
        oracle_oid_mode: bool = False,
    ) -> Iterator[dict[str, Any]]:
        """Search for entries in the LDAP server with Oracle support.

        Args:
            base_dn: The base DN to search from
            search_filter: The search filter to use
            attributes: The attributes to return
            oracle_oid_mode: Whether to use Oracle OID mode

        Yields:
            An iterator of entries

        """
        # Oracle-specific attribute handling
        oracle_attrs = ["orclPassword", "orclPasswordAttribute", "userPassword"]

        if oracle_oid_mode and attributes:
            # Add Oracle-specific attributes if not present
            for oracle_attr in oracle_attrs:
                if oracle_attr not in attributes:
                    attributes.append(oracle_attr)

        # Escape filter for Oracle compatibility
        safe_filter = escape_filter_chars(search_filter)

        for entry in self.search(base_dn, safe_filter, attributes):
            # Oracle-specific processing
            if oracle_oid_mode:
                entry = self._process_oracle_entry(entry)
            yield entry

    def _process_oracle_entry(self, entry: dict[str, Any]) -> dict[str, Any]:
        attributes = entry.get("attributes", {})

        # Handle Oracle password attributes
        if "orclPassword" in attributes:
            # Oracle OID stores passwords differently
            attributes["userPassword"] = attributes.get("orclPassword")

        # Handle Oracle container objects
        if "objectClass" in attributes:
            obj_classes = attributes["objectClass"]
            if isinstance(obj_classes, str):
                obj_classes = [obj_classes]

            # Convert Oracle-specific object classes
            if (
                "orclContainer" in obj_classes
                and "organizationalUnit" not in obj_classes
            ):
                obj_classes.append("organizationalUnit")
                attributes["objectClass"] = obj_classes

        return entry

    def get_naming_contexts(self) -> list[str]:
        """Get naming contexts from LDAP server.

        Returns:
            A list of naming contexts

        """
        try:
            with self.get_connection() as conn:
                # Search for naming contexts
                conn.search(
                    "", "(objectClass=*)", ldap3.BASE, attributes=["namingContexts"],
                )
                if conn.entries:
                    contexts = conn.entries[0].get("namingContexts", [])
                    if isinstance(contexts, list):
                        return [str(ctx) for ctx in contexts]
                    return [str(contexts)]
                return []
        except Exception as e:
            logger.exception("Error getting naming contexts: %s", e)
            return []

    def health_check(self) -> dict[str, Any]:
        """Check the health of the LDAP server.

        Returns:
            A dictionary containing the health status

        """
        health = {
            "status": "unknown",
            "server_uri": self.server_uri,
            "connection_test": False,
            "response_time_ms": None,
            "naming_contexts": [],
            "error": None,
        }

        start_time = time.time()

        try:
            # Test basic connection
            health["connection_test"] = self.test_connection()

            if health["connection_test"]:
                # Get naming contexts
                health["naming_contexts"] = self.get_naming_contexts()
                health["status"] = "healthy"
            else:
                health["status"] = "unhealthy"
        except Exception as e:
            health["error"] = str(e)
            health["status"] = "error"

        health["response_time_ms"] = round((time.time() - start_time) * 1000, 2)

        return health
