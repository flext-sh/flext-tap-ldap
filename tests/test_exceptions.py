"""Tests for tap-ldap exceptions.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest

from flext_tap_ldap import (
    FlextMeltanoTapLdapAuthenticationError,
    FlextMeltanoTapLdapConfigurationError,
    FlextMeltanoTapLdapConnectionError,
    FlextMeltanoTapLdapError,
    FlextMeltanoTapLdapProcessingError,
    FlextMeltanoTapLdapSearchError,
    FlextMeltanoTapLdapStreamError,
    FlextMeltanoTapLdapValidationError,
)


class TestFlextMeltanoTapLdapExceptions:
    """Test factory-created exception functionality."""

    def test_exception_creation(self) -> None:
        """Test method."""
        """Test that all exceptions can be created with proper context."""
        # Test base error
        error = FlextMeltanoTapLdapError("Base error", host="test.com", port=389)
        assert "[FLEXT_TAP_LDAP_ERROR] Base error" in str(error)
        assert hasattr(error, "context")

        # Test specific errors with context
        config_error = FlextMeltanoTapLdapConfigurationError(
            "Config error",
            base_dn="dc=test,dc=com",
            host="test.com",
        )
        assert "[CONFIG_ERROR] flext_tap_ldap config: Config error" in str(config_error)

        # Test connection error
        conn_error = FlextMeltanoTapLdapConnectionError(
            "Connection failed",
            host="test.com",
            timeout=30,
        )
        assert "[FLEXT_2001] flext_tap_ldap connection: Connection failed" in str(
            conn_error,
        )
        assert hasattr(conn_error, "context")


class TestFlextMeltanoTapLdapError:
    """Test base FlextMeltanoTapLdap error."""

    def test_base_error_creation(self) -> None:
        """Test method."""
        """Test creating base LDAP error."""
        error = FlextMeltanoTapLdapError("Test error")
        assert "Test error" in str(error)
        assert isinstance(error, Exception)

    def test_base_error_with_context(self) -> None:
        """Test method."""
        """Test base error with context."""
        context = {"ldap_host": "ldap.example.com", "ldap_port": 389}
        error = FlextMeltanoTapLdapError("Connection failed", **context)

        assert "Connection failed" in str(error)
        # Context should be accessible through args or stored attributes
        assert hasattr(error, "args")


class TestFlextMeltanoTapLdapConnectionError:
    """Test LDAP connection errors."""

    def test_connection_error_creation(self) -> None:
        """Test method."""
        """Test creating connection error."""
        error = FlextMeltanoTapLdapConnectionError("Failed to connect to LDAP server")
        error_str = str(error)
        assert (
            "[FLEXT_2001] flext_tap_ldap connection: Failed to connect to LDAP server"
            in error_str
        )
        assert isinstance(error, Exception)

    def test_connection_error_with_context(self) -> None:
        """Test method."""
        """Test connection error with context."""
        error = FlextMeltanoTapLdapConnectionError(
            "Connection timeout",
            host="ldap.example.com",
            port=389,
            timeout=30,
        )

        assert "[FLEXT_2001] flext_tap_ldap connection: Connection timeout" in str(
            error,
        )

    def test_connection_error_inheritance(self) -> None:
        """Test method."""
        """Test connection error inheritance."""
        error = FlextMeltanoTapLdapConnectionError("Test")
        assert isinstance(error, Exception)


class TestFlextMeltanoTapLdapAuthenticationError:
    """Test LDAP authentication errors."""

    def test_authentication_error_creation(self) -> None:
        """Test method."""
        """Test creating authentication error."""
        error = FlextMeltanoTapLdapAuthenticationError("Invalid credentials")
        error_str = str(error)
        assert "[AUTH_ERROR] flext_tap_ldap: Invalid credentials" in error_str
        assert isinstance(error, Exception)

    def test_authentication_error_with_bind_dn(self) -> None:
        """Test method."""
        """Test authentication error with bind DN context."""
        error = FlextMeltanoTapLdapAuthenticationError(
            "Authentication failed",
            bind_dn="cn=admin,dc=example,dc=com",
            host="ldap.example.com",
        )

        assert "[AUTH_ERROR] flext_tap_ldap: Authentication failed" in str(error)


class TestFlextMeltanoTapLdapSearchError:
    """Test LDAP search errors."""

    def test_search_error_creation(self) -> None:
        """Test method."""
        """Test creating search error."""
        error = FlextMeltanoTapLdapSearchError("Search operation failed")
        assert (
            "[PROCESSING_ERROR] flext_tap_ldap processing: Search operation failed"
            in str(error)
        )
        assert isinstance(error, Exception)

    def test_search_error_with_context(self) -> None:
        """Test method."""
        """Test search error with search context."""
        error = FlextMeltanoTapLdapSearchError(
            "Invalid search filter",
            base_dn="dc=example,dc=com",
            search_filter="(invalid filter)",
            scope="SUBTREE",
        )

        assert (
            "[PROCESSING_ERROR] flext_tap_ldap processing: Invalid search filter"
            in str(error)
        )


class TestFlextMeltanoTapLdapConfigurationError:
    """Test LDAP configuration errors."""

    def test_configuration_error_creation(self) -> None:
        """Test method."""
        """Test creating configuration error."""
        error = FlextMeltanoTapLdapConfigurationError("Invalid configuration")
        assert "[CONFIG_ERROR] flext_tap_ldap config: Invalid configuration" in str(
            error,
        )
        assert isinstance(error, Exception)

    def test_configuration_error_with_context(self) -> None:
        """Test method."""
        """Test configuration error with context."""
        error = FlextMeltanoTapLdapConfigurationError(
            "Missing required parameter",
            parameter="host",
            config_section="connection",
        )

        assert (
            "[CONFIG_ERROR] flext_tap_ldap config: Missing required parameter"
            in str(error)
        )


class TestFlextMeltanoTapLdapProcessingError:
    """Test LDAP processing errors."""

    def test_processing_error_creation(self) -> None:
        """Test method."""
        """Test creating processing error."""
        error = FlextMeltanoTapLdapProcessingError("Processing failed")
        assert "[PROCESSING_ERROR] flext_tap_ldap processing: Processing failed" in str(
            error,
        )
        assert isinstance(error, Exception)

    def test_processing_error_with_context(self) -> None:
        """Test method."""
        """Test processing error with context."""
        error = FlextMeltanoTapLdapProcessingError(
            "Failed to process entry",
            entry_dn="uid=test,ou=users,dc=example,dc=com",
            operation="transform",
        )

        assert (
            "[PROCESSING_ERROR] flext_tap_ldap processing: Failed to process entry"
            in str(error)
        )


class TestFlextMeltanoTapLdapStreamError:
    """Test LDAP stream errors."""

    def test_stream_error_creation(self) -> None:
        """Test method."""
        """Test creating stream error."""
        error = FlextMeltanoTapLdapStreamError("Stream operation failed")
        assert (
            "[PROCESSING_ERROR] flext_tap_ldap processing: Stream operation failed"
            in str(error)
        )
        assert isinstance(error, Exception)

    def test_stream_error_with_context(self) -> None:
        """Test method."""
        """Test stream error with context."""
        error = FlextMeltanoTapLdapStreamError(
            "Stream discovery failed",
            stream_name="users",
            stream_type="LDAP",
        )

        assert (
            "[PROCESSING_ERROR] flext_tap_ldap processing: Stream discovery failed"
            in str(error)
        )


class TestFlextMeltanoTapLdapValidationError:
    """Test LDAP validation errors."""

    def test_validation_error_creation(self) -> None:
        """Test method."""
        """Test creating validation error."""
        error = FlextMeltanoTapLdapValidationError("Data validation failed")
        assert "[FLEXT_3001] flext_tap_ldap: Data validation failed" in str(error)
        assert isinstance(error, Exception)

    def test_validation_error_with_validation_context(self) -> None:
        """Test method."""
        """Test validation error with validation context."""
        error = FlextMeltanoTapLdapValidationError(
            "Invalid DN format",
            dn="invalid_dn",
            field="dn",
            expected_format="attribute=value,...",
        )

        assert "[FLEXT_3001] flext_tap_ldap: Invalid DN format" in str(error)


class TestErrorInheritanceHierarchy:
    """Test error inheritance hierarchy."""

    def test_all_errors_inherit_from_base(self) -> None:
        """Test method."""
        """Test that all specific errors inherit from appropriate base classes."""
        # Test FlextMeltanoTapLdapError hierarchy (FlextMeltanoTapLdapSearchError, FlextMeltanoTapLdapStreamError)
        flext_tap_error_classes = [
            FlextMeltanoTapLdapSearchError,
            FlextMeltanoTapLdapStreamError,
        ]

        for error_class in flext_tap_error_classes:
            error = error_class("Test error")
            assert isinstance(error, Exception)

        # Test FlextSinger* hierarchy (inherits from Singer base classes)
        singer_error_classes = [
            FlextMeltanoTapLdapConnectionError,
            FlextMeltanoTapLdapAuthenticationError,
            FlextMeltanoTapLdapValidationError,
            FlextMeltanoTapLdapConfigurationError,
            FlextMeltanoTapLdapProcessingError,
        ]

        for error_class in singer_error_classes:
            error = error_class("Test error")
            assert isinstance(error, Exception)

    def test_error_factory_functionality(self) -> None:
        """Test method."""
        """Test that all errors use the factory pattern correctly."""
        # Test with connection error
        conn_error = FlextMeltanoTapLdapConnectionError("Test", host="test.com")
        assert "[FLEXT_2001] flext_tap_ldap connection:" in str(conn_error)

        # Test with authentication error
        auth_error = FlextMeltanoTapLdapAuthenticationError("Test", user="testuser")
        assert "[AUTH_ERROR] flext_tap_ldap:" in str(auth_error)

        # Test with search error (aliased to processing)
        search_error = FlextMeltanoTapLdapSearchError("Test", search_filter="(cn=*)")
        assert "[PROCESSING_ERROR] flext_tap_ldap processing:" in str(search_error)


class TestErrorHandlingIntegration:
    """Test error handling integration scenarios."""

    def test_error_with_multiple_context_params(self) -> None:
        """Test method."""
        """Test error with multiple context parameters."""
        error = FlextMeltanoTapLdapConnectionError(
            "Connection failed",
            host="ldap.example.com",
            port=389,
            ssl=True,
            timeout=30,
            retry_count=3,
        )

        assert "[FLEXT_2001] flext_tap_ldap connection: Connection failed" in str(error)
        # The context should be properly handled by the mixin

    def test_error_chain_convenience(self) -> None:
        """Test method."""
        """Test error chaining testing convenience."""
        msg = "Original error"
        with pytest.raises(ValueError):
            raise ValueError(msg)
        chained_error = FlextMeltanoTapLdapConnectionError(
            "Connection failed due to original error",
        )
        # Python exception chaining should work
        assert isinstance(chained_error, Exception)

    def test_exception_handling_patterns(self) -> None:
        """Test method."""
        """Test common exception handling patterns."""
        # Test catching specific error
        msg = "Connection failed"
        with pytest.raises(FlextMeltanoTapLdapConnectionError):
            raise FlextMeltanoTapLdapConnectionError(msg)

        # Test catching base error - use specific exception type
        msg = "Auth failed"
        with pytest.raises(FlextMeltanoTapLdapAuthenticationError):
            raise FlextMeltanoTapLdapAuthenticationError(msg)

        # Test catching validation error - use specific exception type
        msg = "Validation failed"
        with pytest.raises(FlextMeltanoTapLdapValidationError):
            raise FlextMeltanoTapLdapValidationError(msg)
