"""Test models for flext-tap-ldap - uses m.TapLdap.Tests.* namespace pattern.

This module provides test-specific models that extend the main flext-tap-ldap models.
Uses the unified namespace pattern m.TapLdap.Tests.* for test-only objects.
Combines TestsFlextModels functionality with project-specific test models.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import Annotated

from flext_tests import FlextTestsModels

from flext_tap_ldap import FlextTapLdapModels, t
from tests.utilities import u


class TestsFlextTapLdapModels(FlextTestsModels, FlextTapLdapModels):
    """Test models combining TestsFlextModels with flext-tap-ldap models."""

    class TapLdap(FlextTapLdapModels.TapLdap):
        """TapLdap domain models extending project models."""

        class Tests:
            """Test models namespace for flext-tap-ldap tests.

            Contains test-specific models that extend the main models with test-only features.
            These models are only used in tests and not in production code.
            """

            class TestLdapConnection(FlextTapLdapModels.Entity):
                """Test model for LDAP database connections."""

                host: Annotated[str, u.Field(description="LDAP server hostname")]
                port: Annotated[int, u.Field(description="LDAP server port")]
                base_dn: Annotated[
                    str, u.Field(description="Base DN for LDAP searches")
                ]
                bind_dn: Annotated[
                    str | None, u.Field(description="Bind DN for authentication")
                ] = None
                bind_password: Annotated[
                    str | None, u.Field(description="Password for bind DN")
                ] = None
                use_ssl: Annotated[
                    bool, u.Field(description="Whether to use SSL/TLS")
                ] = False

                @property
                def connection_string(self) -> str:
                    """The LDAP connection string."""
                    protocol = "ldaps" if self.use_ssl else "ldap"
                    return f"{protocol}://{self.host}:{self.port}"

            class TestLdapSearch(FlextTapLdapModels.Entity):
                """Test model for LDAP search operations."""

                base_dn: Annotated[str, u.Field(description="Base DN for the search")]
                filter_str: Annotated[
                    str, u.Field(description="LDAP search filter string")
                ]
                attributes: Annotated[
                    t.StrSequence | None,
                    u.Field(description="Attributes to retrieve in the search"),
                ] = None
                scope: Annotated[
                    str, u.Field(description="Search scope (BASE, ONELEVEL, SUBTREE)")
                ] = "SUBTREE"
                size_limit: Annotated[
                    int | None,
                    u.Field(description="Maximum number of entries to return"),
                ] = None
                time_limit: Annotated[
                    int | None,
                    u.Field(
                        description="Maximum time allowed for the search in seconds"
                    ),
                ] = None

            class TestLdapStream(FlextTapLdapModels.Entity):
                """Test model for LDAP Singer streams."""

                stream_name: Annotated[
                    str, u.Field(description="Name of the Singer stream")
                ]
                base_dn: Annotated[str, u.Field(description="Base DN for the stream")]
                object_class: Annotated[
                    str, u.Field(description="Object class filtered by the stream")
                ]
                replication_method: Annotated[
                    str,
                    u.Field(description="Replication method for the stream"),
                ] = "FULL_TABLE"
                is_selected: Annotated[
                    bool, u.Field(description="Whether the stream is selected for sync")
                ] = True

            class TestLdapEntry(FlextTapLdapModels.Entity):
                """Test model for LDAP directory entries."""

                dn: Annotated[
                    str, u.Field(description="Distinguished name of the entry")
                ]
                attributes: Annotated[
                    t.StrSequenceMapping,
                    u.Field(description="Attributes mapped to their values"),
                ]
                object_class: Annotated[
                    str, u.Field(description="Object class of the entry")
                ]

                @property
                def attribute_count(self) -> int:
                    """The number of attributes."""
                    return len(self.attributes)


m = TestsFlextTapLdapModels

__all__: list[str] = ["TestsFlextTapLdapModels", "m"]
