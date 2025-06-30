"""tap-ldap main tap class.

This module implements the main tap class for LDAP data extraction.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, ClassVar

from singer_sdk import Tap
from singer_sdk import typing as th
from tap_ldap.ldif_stream import LDIFAnalysisStream, LDIFStream
from tap_ldap.streams import (
    CustomStream,
    GroupsStream,
    OrganizationalUnitsStream,
    SchemaStream,
    UsersStream,
)

if TYPE_CHECKING:
    from singer_sdk.streams import Stream


logger = logging.getLogger(__name__)


class TapLDAP(Tap):
    """Singer tap for LDAP data extraction."""

    name = "tap-ldap"

    config_jsonschema: ClassVar[dict[str, Any]] = th.PropertiesList(
        th.Property(
            "host",
            th.StringType,
            required=True,
            description="LDAP server hostname or IP address",
        ),
        th.Property(
            "port",
            th.IntegerType,
            default=389,
            description="LDAP server port (389 for LDAP, 636 for LDAPS)",
        ),
        th.Property(
            "bind_dn",
            th.StringType,
            description="Distinguished name for binding to LDAP",
        ),
        th.Property(
            "password",
            th.StringType,
            secret=True,
            description="Password for LDAP authentication",
        ),
        th.Property(
            "base_dn",
            th.StringType,
            required=True,
            description="Base DN for LDAP searches",
        ),
        th.Property(
            "use_ssl",
            th.BooleanType,
            default=False,
            description="Use SSL/TLS for LDAP connection",
        ),
        th.Property(
            "timeout",
            th.IntegerType,
            default=30,
            description="Connection timeout in seconds",
        ),
        th.Property(
            "page_size",
            th.IntegerType,
            default=1000,
            description="Page size for paged results",
        ),
        th.Property(
            "user_filter",
            th.StringType,
            default="(objectClass=inetOrgPerson)",
            description="LDAP filter for user entries",
        ),
        th.Property(
            "group_filter",
            th.StringType,
            default="(objectClass=groupOfNames)",
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
    ).to_dict()

    def discover_streams(self) -> list[Stream]:
        """Discover available streams.

        Returns
        -------
            List of discovered Stream instances

        """
        streams: list[Stream] = []

        # Add LDIF streams if enabled (for brutal simplification)
        if self.config.get("enable_ldif_streams", False):
            streams.extend(
                [
                    LDIFStream(self),
                    LDIFAnalysisStream(self),
                ],
            )
            # Standard LDAP streams
            streams.extend(
                [
                    UsersStream(self),
                    GroupsStream(self),
                    OrganizationalUnitsStream(self),
                    SchemaStream(self),
                ],
            )

        # Add custom streams if configured
        custom_streams_config = self.config.get("custom_streams", [])
        for custom_config in custom_streams_config:
            stream = CustomStream(
                tap=self,
                name=custom_config["name"],
                search_filter=custom_config["search_filter"],
                schema_properties=custom_config.get("schema", {}).get("properties", {}),
                primary_keys=custom_config.get("primary_keys"),
                replication_key=custom_config.get("replication_key"),
            )
            streams.append(stream)

        return streams


if __name__ == "__main__":
    TapLDAP.cli()
