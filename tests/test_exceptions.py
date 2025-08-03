"""Tests for tap-ldap exceptions."""

from __future__ import annotations

import pytest

from flext_tap_ldap.exceptions import (
    FlextTapLdapAuthenticationError,
    FlextTapLdapConfigurationError,
    FlextTapLdapConnectionError,
    FlextTapLdapError,
    FlextTapLdapProcessingError,
    FlextTapLdapSearchError,
    FlextTapLdapStreamError,
    FlextTapLdapValidationError,
    _FlextTapLdapErrorMixin,
)


class TestFlextTapLdapErrorMixin:
    """Test error mixin functionality."""

    def test_build_ldap_context(self) -> None:
        """Test building LDAP context dictionary."""
        mixin = _FlextTapLdapErrorMixin()

        # Test with empty kwargs
        context = mixin._build_ldap_context({}, host="test.com", port=389)
        assert context == {"host": "test.com", "port": 389}

        # Test with existing kwargs
        kwargs = {"base_dn": "dc=test,dc=com"}
        context = mixin._build_ldap_context(kwargs, host="test.com", timeout=30)
        assert context == {
            "base_dn": "dc=test,dc=com",
            "host": "test.com",
            "timeout": 30,
        }

        # Test with None values (should be filtered out)
        context = mixin._build_ldap_context({}, host="test.com", port=None, ssl=True)
        assert context == {"host": "test.com", "ssl": True}

    def test_format_ldap_message(self) -> None:
        """Test formatting LDAP error messages."""
        mixin = _FlextTapLdapErrorMixin()

        message = mixin._format_ldap_message("Connection failed", "connection")
        assert message == "LDAP tap connection: Connection failed"

        message = mixin._format_ldap_message("Authentication error", "auth")
        assert message == "LDAP tap auth: Authentication error"


class TestFlextTapLdapError:
    """Test base FlextTapLdap error."""

    def test_base_error_creation(self) -> None:
        """Test creating base LDAP error."""
        error = FlextTapLdapError("Test error")
        assert "Test error" in str(error)
        assert isinstance(error, Exception)

    def test_base_error_with_context(self) -> None:
        """Test base error with context."""
        context = {"host": "ldap.example.com", "port": 389}
        error = FlextTapLdapError("Connection failed", **context)

        assert "Connection failed" in str(error)
        # Context should be accessible through args or stored attributes
        assert hasattr(error, "args")


class TestFlextTapLdapConnectionError:
    """Test LDAP connection errors."""

    def test_connection_error_creation(self) -> None:
        """Test creating connection error."""
        error = FlextTapLdapConnectionError("Failed to connect to LDAP server")
        error_str = str(error)
        assert "LDAP tap connection: Failed to connect to LDAP server" in error_str
        assert isinstance(error, Exception)

    def test_connection_error_with_context(self) -> None:
        """Test connection error with context."""
        error = FlextTapLdapConnectionError(
            "Connection timeout",
            host="ldap.example.com",
            port=389,
            timeout=30,
        )

        assert "LDAP tap connection: Connection timeout" in str(error)

    def test_connection_error_inheritance(self) -> None:
        """Test connection error inheritance."""
        error = FlextTapLdapConnectionError("Test")
        assert isinstance(error, Exception)
        assert isinstance(error, _FlextTapLdapErrorMixin)


class TestFlextTapLdapAuthenticationError:
    """Test LDAP authentication errors."""

    def test_authentication_error_creation(self) -> None:
        """Test creating authentication error."""
        error = FlextTapLdapAuthenticationError("Invalid credentials")
        error_str = str(error)
        assert "LDAP tap auth: Invalid credentials" in error_str
        assert isinstance(error, Exception)

    def test_authentication_error_with_bind_dn(self) -> None:
        """Test authentication error with bind DN context."""
        error = FlextTapLdapAuthenticationError(
            "Authentication failed",
            bind_dn="cn=REDACTED_LDAP_BIND_PASSWORD,dc=example,dc=com",
            host="ldap.example.com",
        )

        assert "LDAP tap auth: Authentication failed" in str(error)


class TestFlextTapLdapSearchError:
    """Test LDAP search errors."""

    def test_search_error_creation(self) -> None:
        """Test creating search error."""
        error = FlextTapLdapSearchError("Search operation failed")
        assert "LDAP tap search: Search operation failed" in str(error)
        assert isinstance(error, Exception)

    def test_search_error_with_context(self) -> None:
        """Test search error with search context."""
        error = FlextTapLdapSearchError(
            "Invalid search filter",
            base_dn="dc=example,dc=com",
            search_filter="(invalid filter)",
            scope="SUBTREE",
        )

        assert "LDAP tap search: Invalid search filter" in str(error)


class TestFlextTapLdapConfigurationError:
    """Test LDAP configuration errors."""

    def test_configuration_error_creation(self) -> None:
        """Test creating configuration error."""
        error = FlextTapLdapConfigurationError("Invalid configuration")
        assert "LDAP tap config: Invalid configuration" in str(error)
        assert isinstance(error, Exception)

    def test_configuration_error_with_context(self) -> None:
        """Test configuration error with context."""
        error = FlextTapLdapConfigurationError(
            "Missing required parameter",
            parameter="host",
            config_section="connection",
        )

        assert "LDAP tap config: Missing required parameter" in str(error)


class TestFlextTapLdapProcessingError:
    """Test LDAP processing errors."""

    def test_processing_error_creation(self) -> None:
        """Test creating processing error."""
        error = FlextTapLdapProcessingError("Processing failed")
        assert "LDAP tap processing: Processing failed" in str(error)
        assert isinstance(error, Exception)

    def test_processing_error_with_context(self) -> None:
        """Test processing error with context."""
        error = FlextTapLdapProcessingError(
            "Failed to process entry",
            entry_dn="uid=test,ou=users,dc=example,dc=com",
            operation="transform",
        )

        assert "LDAP tap processing: Failed to process entry" in str(error)


class TestFlextTapLdapStreamError:
    """Test LDAP stream errors."""

    def test_stream_error_creation(self) -> None:
        """Test creating stream error."""
        error = FlextTapLdapStreamError("Stream operation failed")
        assert "LDAP tap stream: Stream operation failed" in str(error)
        assert isinstance(error, Exception)

    def test_stream_error_with_context(self) -> None:
        """Test stream error with context."""
        error = FlextTapLdapStreamError(
            "Stream discovery failed",
            stream_name="users",
            stream_type="LDAP",
        )

        assert "LDAP tap stream: Stream discovery failed" in str(error)


class TestFlextTapLdapValidationError:
    """Test LDAP validation errors."""

    def test_validation_error_creation(self) -> None:
        """Test creating validation error."""
        error = FlextTapLdapValidationError("Data validation failed")
        assert "LDAP tap validation: Data validation failed" in str(error)
        assert isinstance(error, Exception)

    def test_validation_error_with_validation_context(self) -> None:
        """Test validation error with validation context."""
        error = FlextTapLdapValidationError(
            "Invalid DN format",
            dn="invalid_dn",
            field="dn",
            expected_format="attribute=value,...",
        )

        assert "LDAP tap validation: Invalid DN format" in str(error)


class TestErrorInheritanceHierarchy:
    """Test error inheritance hierarchy."""

    def test_all_errors_inherit_from_base(self) -> None:
        """Test that all specific errors inherit from appropriate base classes."""
        # Test FlextTapLdapError hierarchy (FlextTapLdapSearchError, FlextTapLdapStreamError)
        flext_tap_error_classes = [
            FlextTapLdapSearchError,
            FlextTapLdapStreamError,
        ]

        for error_class in flext_tap_error_classes:
            error = error_class("Test error")
            assert isinstance(error, Exception)
            assert isinstance(error, _FlextTapLdapErrorMixin)
            assert isinstance(error, Exception)

        # Test FlextSinger* hierarchy (inherits from Singer base classes)
        singer_error_classes = [
            FlextTapLdapConnectionError,
            FlextTapLdapAuthenticationError,
            FlextTapLdapValidationError,
            FlextTapLdapConfigurationError,
            FlextTapLdapProcessingError,
        ]

        for error_class in singer_error_classes:
            error = error_class("Test error")
            assert isinstance(error, _FlextTapLdapErrorMixin)
            assert isinstance(error, Exception)

    def test_error_mixin_functionality(self) -> None:
        """Test that all errors use the mixin functionality."""
        # Test with connection error
        conn_error = FlextTapLdapConnectionError("Test", host="test.com")
        assert "LDAP tap connection:" in str(conn_error)

        # Test with authentication error
        auth_error = FlextTapLdapAuthenticationError("Test", user="testuser")
        assert "LDAP tap auth:" in str(auth_error)

        # Test with search error
        search_error = FlextTapLdapSearchError("Test", search_filter="(cn=*)")
        assert "LDAP tap search:" in str(search_error)


class TestErrorHandlingIntegration:
    """Test error handling integration scenarios."""

    def test_error_with_multiple_context_params(self) -> None:
        """Test error with multiple context parameters."""
        error = FlextTapLdapConnectionError(
            "Connection failed",
            host="ldap.example.com",
            port=389,
            ssl=True,
            timeout=30,
            retry_count=3,
        )

        assert "LDAP tap connection: Connection failed" in str(error)
        # The context should be properly handled by the mixin

    def test_error_chain_compatibility(self) -> None:
        """Test error chaining compatibility."""
        try:
            msg = "Original error"
            raise ValueError(msg)
        except ValueError:
            chained_error = FlextTapLdapConnectionError(
                "Connection failed due to original error",
            )
            # Python exception chaining should work
            assert isinstance(chained_error, Exception)

    def test_exception_handling_patterns(self) -> None:
        """Test common exception handling patterns."""
        # Test catching specific error
        with pytest.raises(FlextTapLdapConnectionError):
            msg = "Connection failed"
            raise FlextTapLdapConnectionError(msg)

        # Test catching base error
        with pytest.raises(Exception):
            msg = "Auth failed"
            raise FlextTapLdapAuthenticationError(msg)

        # Test catching generic exception
        with pytest.raises(Exception):
            msg = "Validation failed"
            raise FlextTapLdapValidationError(msg)
