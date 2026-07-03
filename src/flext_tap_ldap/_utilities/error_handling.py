"""Tap LDAP error handling utility namespace."""

from __future__ import annotations

from flext_tap_ldap import e, t


class FlextTapLdapUtilitiesErrorHandling:
    """LDAP tap error handling utilities with enhanced context."""

    class ErrorHandling:
        """LDAP tap error handling utilities with enhanced context."""

        @staticmethod
        def create_bind_error(
            message: str = "LDAP bind failed",
            bind_dn: str | None = None,
            **kwargs: t.Scalar,
        ) -> e.AuthenticationError:
            """Create bind error with context."""
            context: t.MutableConfigurationMapping = dict(kwargs)
            if bind_dn is not None:
                context["bind_dn"] = bind_dn
            return e.AuthenticationError(message, context=context)

        @staticmethod
        def create_connection_error(
            message: str = "LDAP connection failed",
            host: str | None = None,
            port: int | None = None,
            base_dn: str | None = None,
            **kwargs: t.Scalar,
        ) -> e.ConnectionError:
            """Create connection error with context."""
            context: t.MutableConfigurationMapping = dict(kwargs)
            if host is not None:
                context["host"] = host
            if port is not None:
                context["port"] = port
            if base_dn is not None:
                context["base_dn"] = base_dn
            return e.ConnectionError(message, context=context)

        @staticmethod
        def create_search_error(
            message: str = "LDAP search failed",
            base_dn: str | None = None,
            filter_str: str | None = None,
            **kwargs: t.Scalar,
        ) -> e.OperationError:
            """Create search error with context."""
            context: t.MutableConfigurationMapping = dict(kwargs)
            if base_dn is not None:
                context["base_dn"] = base_dn
            if filter_str is not None:
                context["filter"] = filter_str[:100]
            return e.OperationError(message, context=context)


__all__: list[str] = ["FlextTapLdapUtilitiesErrorHandling"]
