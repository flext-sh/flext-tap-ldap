"""Version information for FLEXT Tap LDAP.

Uses importlib.metadata for single source of truth from pyproject.toml.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from importlib.metadata import metadata

from pydantic import BaseModel, ConfigDict, Field

_metadata = metadata("flext_tap_ldap")


class FlextMeltanoTapLdapVersion(BaseModel):
    """Version information container."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    version: str = Field(description="Version string")
    version_info: tuple[int | str, ...] = Field(description="Version tuple")
    title: str = Field(description="Project title")
    description: str = Field(description="Project description")
    author: str = Field(description="Author name")
    author_email: str = Field(description="Author email")
    license_: str = Field(description="License identifier")
    url: str = Field(description="Project URL")


VERSION = FlextMeltanoTapLdapVersion(
    version=_metadata["Version"],
    version_info=tuple(
        int(part) if part.isdigit() else part
        for part in _metadata["Version"].split(".")
    ),
    title=_metadata["Name"],
    description=_metadata["Summary"],
    author=_metadata["Author"],
    author_email=_metadata["Author-Email"],
    license_=_metadata["License"],
    url=_metadata.get("Home-Page", ""),
)

__all__ = [
    "VERSION",
    "FlextMeltanoTapLdapVersion",
]
