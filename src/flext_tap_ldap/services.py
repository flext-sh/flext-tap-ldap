"""Services for FLEXT Tap LDAP operations and utilities.

Consolidates application services, LDIF processing, and simple API utilities
with maximum integration to flext-core, flext-ldap, and flext-ldif libraries.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import ClassVar

from flext_tap_ldap import FlextTapLdapSettings, c, m, p, r, t, u


class FlextTapLdapServices:
    """Unified services class for LDAP tap operations with complete service management.

    This class consolidates all LDAP tap services including connection management,
    stream processing, record handling, and LDIF processing following the unified
    class pattern with Clean Architecture and Domain-Driven Design.

    Contains all service classes and utility functions as nested classes and methods
    to maintain single responsibility while providing complete LDAP/LDIF
    data extraction and processing capabilities.
    """

    logger: ClassVar = u.fetch_logger(__name__)

    EXPECTED_DATA_COUNT = 3

    @staticmethod
    def create_development_ldap_config(
        **overrides: t.Scalar,
    ) -> p.Result[FlextTapLdapSettings]:
        """Create development LDAP configuration with defaults.

        Args:
        **overrides: Configuration overrides

        Returns:
        r with FlextTapLdapSettings for development use.

        """
        try:
            settings = FlextTapLdapSettings.model_validate(overrides)
            return r[FlextTapLdapSettings].ok(settings)
        except c.EXC_RUNTIME_TYPE as exc:
            return r[FlextTapLdapSettings].fail(
                f"Failed to create development settings: {exc}",
            )

    @staticmethod
    def create_ldap_connection_config(
        params: m.TapLdap.LdapConnectionParams,
    ) -> p.Result[t.JsonMapping]:
        """Create LDAP connection configuration using Parameter Object Pattern.

        Args:
        params: LDAP connection parameters t.JsonValue

        Returns:
        r with connection configuration or error message.

        """
        try:
            settings = {
                "host": params.host,
                "port": params.port,
                "bind_dn": params.bind_dn,
                "bind_password": params.bind_password,
                "base_dn": params.base_dn,
                "use_ssl": params.use_ssl,
                "timeout_seconds": params.timeout_seconds,
                "page_size": params.page_size,
                "max_retries": params.max_retries,
            }
            return r[t.JsonMapping].ok(settings)
        except c.EXC_RUNTIME_TYPE as exc:
            return r[t.JsonMapping].fail(
                f"Failed to create LDAP connection settings: {exc}",
            )

    @staticmethod
    def create_default_ldap_config(
        host: str,
        base_dn: str,
        port: int = c.Ldap.PORT,
        **kwargs: t.Scalar,
    ) -> p.Result[t.JsonMapping]:
        """Create LDAP connection configuration (testing convenience interface).

        Testing convenience wrapper for the Parameter Object Pattern implementation.
        Use FlextTapLdapServices.create_ldap_connection_config() with m.TapLdap.LdapConnectionParams for new code.
        """
        params = m.TapLdap.LdapConnectionParams(
            host=host,
            base_dn=base_dn,
            port=port,
            use_ssl=bool(kwargs.get("use_ssl")),
            bind_dn=u.to_str(kwargs.get("bind_dn")),
            bind_password=u.to_str(kwargs.get("bind_password")),
            timeout_seconds=c.TapLdap.DEFAULT_SEARCH_TIMEOUT,
            page_size=c.TapLdap.DEFAULT_PAGE_SIZE,
            max_retries=3,
        )
        return FlextTapLdapServices.create_ldap_connection_config(params)

    @staticmethod
    def create_production_ldap_config(
        **overrides: t.Scalar,
    ) -> p.Result[FlextTapLdapSettings]:
        """Create production LDAP configuration with security defaults.

        Args:
        **overrides: Configuration overrides

        Returns:
        r with FlextTapLdapSettings for production use.

        """
        try:
            production_overrides = {"use_ssl": True, **overrides}
            settings = FlextTapLdapSettings.model_validate(production_overrides)
            return r[FlextTapLdapSettings].ok(settings)
        except c.EXC_RUNTIME_TYPE as exc:
            return r[FlextTapLdapSettings].fail(
                f"Failed to create production settings: {exc}",
            )

    @staticmethod
    def setup_ldap_tap(
        settings: FlextTapLdapSettings | None = None,
    ) -> p.Result[FlextTapLdapSettings]:
        """Set up the LDAP tap with configuration.

        Args:
        settings: Optional configuration. If None, creates defaults.

        Returns:
        r with FlextTapLdapSettings or error message.

        """
        try:
            if settings is None:
                settings = FlextTapLdapSettings.model_validate({})
            validation_result = FlextTapLdapServices.validate_ldap_config(settings)
            if not validation_result.success or not validation_result.value:
                return r[FlextTapLdapSettings].fail(
                    validation_result.error or "Configuration validation failed",
                )
            return r[FlextTapLdapSettings].ok(settings)
        except c.EXC_RUNTIME_TYPE as exc:
            return r[FlextTapLdapSettings].fail(f"Failed to setup LDAP tap: {exc}")

    @staticmethod
    def validate_ldap_config(settings: FlextTapLdapSettings) -> p.Result[bool]:
        """Validate LDAP tap configuration.

        Args:
        settings: Configuration to validate

        Returns:
        r with validation success or error message.

        """
        try:
            valid = bool(settings.host and settings.port > 0 and settings.page_size > 0)
            return r[bool].ok(valid)
        except c.EXC_RUNTIME_TYPE as exc:
            return r[bool].fail_op("Configuration validation", exc)


__all__: list[str] = ["FlextTapLdapServices"]
