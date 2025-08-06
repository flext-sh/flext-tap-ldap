"""tap-ldap main tap class using FLEXT centralized conventions.

This module implements the main tap class for LDAP data extraction
using the centralized patterns from flext-core.meltano.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from flext_core import get_logger
from flext_meltano import Tap, singer_typing as th
from flext_meltano.common_schemas import create_ldap_tap_schema

from flext_tap_ldap.config import TapLDAPConfig
from flext_tap_ldap.ldif_stream import LDIFAnalysisStream, LDIFStream
from flext_tap_ldap.streams import (
    CustomStream,
    CustomStreamParams,
    GroupsStream,
    OrganizationalUnitsStream,
    SchemaStream,
    UsersStream,
)

if TYPE_CHECKING:
    from flext_meltano import Stream


logger = get_logger(__name__)


class FlextTapLDAP(Tap):
    """Singer tap for LDAP data extraction using FLEXT centralized patterns."""

    name: str = "tap-ldap"
    config_class = TapLDAPConfig

    # REAL DRY: Use centralized LDAP schema from flext-meltano instead of duplicating
    config_jsonschema: ClassVar[dict[str, object]] = create_ldap_tap_schema(
        # LDAP-specific additional properties for tap-ldap
        additional_properties=th.PropertiesList(
            th.Property(
                "page_size",
                th.IntegerType,
                default=1000,
                description="Page size for paged results",
            ),
            th.Property(
                "user_filter",
                th.StringType,
                default="(object_class=inetOrgPerson)",
                description="LDAP filter for user entries",
            ),
            th.Property(
                "group_filter",
                th.StringType,
                default="(object_class=groupOfNames)",
                description="LDAP filter for group entries",
            ),
            th.Property(
                "custom_streams",
                th.ArrayType(
                    th.ObjectType(
                        th.Property("name", th.StringType, required=True),
                        th.Property("search_filter", th.StringType, required=True),
                        th.Property("primary_keys", th.ArrayType(th.StringType)),
                        th.Property("replication_key", th.StringType),
                        th.Property(
                            "schema",
                            th.ObjectType(),
                            description="JSON schema for the stream",
                        ),
                    ),
                ),
                description="Custom stream definitions",
            ),
            th.Property(
                "stream_maps",
                th.ObjectType(),
                description="Configuration for stream maps",
            ),
            th.Property(
                "stream_map_settings",
                th.ObjectType(),
                description="Settings for stream maps",
            ),
            # LDIF Processing Configuration
            th.Property(
                "ldif_files",
                th.ArrayType(th.StringType),
                description="List of LDIF files to process",
            ),
            th.Property(
                "ldif_directory",
                th.StringType,
                description="Directory containing LDIF files",
            ),
            th.Property(
                "ldif_file_pattern",
                th.StringType,
                default="*.ldif",
                description="File pattern for LDIF files in directory",
            ),
            th.Property(
                "ldif_ignore_errors",
                th.BooleanType,
                default=True,
                description="Continue processing on LDIF parsing errors",
            ),
            th.Property(
                "ldif_max_errors",
                th.IntegerType,
                default=100,
                description="Maximum number of parsing errors before stopping",
            ),
            th.Property(
                "ldif_ignore_file_errors",
                th.BooleanType,
                default=True,
                description="Continue processing if a file fails completely",
            ),
            th.Property(
                "ldif_ignore_entry_errors",
                th.BooleanType,
                default=True,
                description="Continue processing if an entry fails",
            ),
            th.Property(
                "ldif_apply_transformations",
                th.BooleanType,
                default=False,
                description="Apply transformation rules to LDIF entries",
            ),
            th.Property(
                "ldif_transformation_rules",
                th.ObjectType(),
                description="Transformation rules for LDIF processing",
            ),
            th.Property(
                "migration_batch",
                th.StringType,
                description="Migration batch identifier for tracking",
            ),
            th.Property(
                "enable_ldif_streams",
                th.BooleanType,
                default=False,
                description="Enable LDIF processing streams",
            ),
        ),
    ).to_dict()

    def discover_streams(self) -> list[Stream]:
        """Discover available streams."""
        streams: list[Stream] = []

        # Standard LDAP streams (always available)
        streams.extend(
            [
                UsersStream(self),
                GroupsStream(self),
                OrganizationalUnitsStream(self),
                SchemaStream(self),
            ],
        )

        # Add LDIF streams if enabled
        if self.config.get("enable_ldif_streams", False):
            streams.extend(
                [
                    LDIFStream(self),
                    LDIFAnalysisStream(self),
                ],
            )

        # Add custom streams if configured:
        custom_streams_config = self.config.get("custom_streams", [])
        for custom_config in custom_streams_config:

            params = CustomStreamParams(
                name=custom_config["name"],
                search_filter=custom_config["search_filter"],
                schema_properties=custom_config.get("schema", {}).get("properties", {}),
                primary_keys=custom_config.get("primary_keys"),
                replication_key=custom_config.get("replication_key"),
            )
            stream = CustomStream(tap=self, params=params)
            streams.append(stream)

        return streams


def main() -> None:
    """Main entry point for the tap."""
    FlextTapLDAP.cli()


if __name__ == "__main__":
    main()
