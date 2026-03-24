"""Test models for flext-tap-ldap - uses m.TapLdap.Tests.* namespace pattern.

This module provides test-specific models that extend the main flext-tap-ldap models.
Uses the unified namespace pattern m.TapLdap.Tests.* for test-only objects.
Combines FlextTestsModels functionality with project-specific test models.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Sequence, Mapping

from flext_tests import FlextTestsModels

from flext_tap_ldap import FlextTapLdapModels


class FlextTapLdapTestModels(FlextTestsModels, FlextTapLdapModels):
    """Test models combining FlextTestsModels with flext-tap-ldap models."""

    class TapLdap(FlextTapLdapModels.TapLdap):
        """TapLdap domain models extending project models."""

        class Tests:
            """Test models namespace for flext-tap-ldap tests.

            Contains test-specific models that extend the main models with test-only features.
            These models are only used in tests and not in production code.
            """

            class TestLdapConnection(FlextTapLdapModels.Entity):
                """Test model for LDAP database connections."""

                host: str
                port: int
                base_dn: str
                bind_dn: str | None = None
                bind_password: str | None = None
                use_ssl: bool = False

                @property
                def connection_string(self) -> str:
                    """Get LDAP connection string."""
                    protocol = "ldaps" if self.use_ssl else "ldap"
                    return f"{protocol}://{self.host}:{self.port}"

            class TestLdapSearch(FlextTapLdapModels.Entity):
                """Test model for LDAP search operations."""

                base_dn: str
                filter_str: str
                attributes: Sequence[str] | None = None
                scope: str = "SUBTREE"
                size_limit: int | None = None
                time_limit: int | None = None

            class TestLdapStream(FlextTapLdapModels.Entity):
                """Test model for LDAP Singer streams."""

                stream_name: str
                base_dn: str
                object_class: str
                replication_method: str = "FULL_TABLE"
                is_selected: bool = True

            class TestLdapEntry(FlextTapLdapModels.Entity):
                """Test model for LDAP directory entries."""

                dn: str
                attributes: Mapping[str, Sequence[str]]
                object_class: str

                @property
                def attribute_count(self) -> int:
                    """Get number of attributes."""
                    return len(self.attributes)


m = FlextTapLdapTestModels

__all__ = ["FlextTapLdapTestModels", "m"]
