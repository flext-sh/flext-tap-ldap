"""Version information for FLEXT Tap LDAP.

Uses importlib.metadata for single source of truth from pyproject.toml.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from importlib.metadata import metadata
from typing import Annotated

from pydantic import BaseModel, Field


class FlextTapLdapVersion(BaseModel):
    """Version metadata for FLEXT Tap LDAP package."""

    version: Annotated[str, Field(min_length=1)]
    version_info: tuple[int | str, ...]
    title: str = ""
    description: str = ""
    author: str = ""
    author_email: str = ""
    license_: str = ""
    url: str = ""


_metadata = metadata("flext_tap_ldap")
VERSION = FlextTapLdapVersion(
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
__all__ = ["VERSION", "FlextTapLdapVersion"]
